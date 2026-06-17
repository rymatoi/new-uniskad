import asyncio
import contextlib
import threading
import time
from dataclasses import replace
from functools import wraps
from inspect import signature

import asyncpg
import typing

from PySide2.QtCore import QObject, QThread, Signal, Qt
from asyncpg import RaiseError
from config.config import config

from app import app_logger
from app.progress import ProgressState

logger = app_logger.get_logger(__name__)

def db_timing_log(message):
    """Emit detailed DB timings only when debug logging is enabled."""
    logger.debug("%s", message)



class QueryResult:
    def __init__(self, result=None, columns=None):
        self.result = result
        self.columns = columns

    def all(self):
        return self.result

    def one(self):
        if not self.result:
            return None
        return self.result[0]

    def last(self):
        if not self.result:
            return None
        return self.result[-1]


class Worker(QThread):
    # Keep QThread.started/finished intact: Qt emits them only at the actual
    # boundaries of the native thread lifecycle.
    result_ready = Signal(object)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            result = self.func(*self.args, **self.kwargs)
        except Exception as exc:  # noqa: BLE001 - want to propagate any failure to the UI thread safely
            logger.exception("Worker task raised an exception")
            self.result_ready.emit(exc)
        else:
            self.result_ready.emit(result)


class _ProgressEmitter(QObject):
    progress = Signal(object)


class _ProgressContext:
    def __init__(
        self, session, title, total=None, blocking=False, detail=None,
        suppress_loading_messages=False,
    ):
        self.session = session
        self.state = session.begin_progress(
            title, total, blocking, detail, suppress_loading_messages=suppress_loading_messages,
        )

    def update(self, **kwargs):
        self.state = self.session.update_progress(**kwargs)
        return self.state

    def advance(self, step=1, detail=None, message=None):
        self.state = self.session.advance_progress(step, detail, message)
        return self.state

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.end_progress()



class Session:
    def __init__(self, **dsn):
        self.dsn = dsn
        self.loop = asyncio.new_event_loop()
        self._loop_ready = threading.Event()
        self._loop_thread = threading.Thread(target=self._run_event_loop, daemon=True)
        self._loop_thread.start()
        self._loop_ready.wait()

        self._remote_connection = None
        self._execute_lock = None
        self._reconnect_lock = None
        self.main_window = None
        self._login = None
        self._password = None
        self._progress_emitter = None
        self._last_progress_message = None
        self._progress_state = None
        self._progress_started_at = None
        self._suppress_loading_bar_messages = False

        logger.info("Session initialized. Event loop thread: %s", self._loop_thread.name)

        self.run_sync(self._initialize_async_state())

    def _run_event_loop(self):
        logger.debug("Session event loop starting in thread %s", threading.current_thread().name)
        asyncio.set_event_loop(self.loop)
        self._loop_ready.set()
        self.loop.run_forever()
        logger.debug("Session event loop finished in thread %s", threading.current_thread().name)

    async def _initialize_async_state(self):
        logger.debug("Initializing async state (locks and initial connection)")
        self._execute_lock = asyncio.Lock()
        self._reconnect_lock = asyncio.Lock()
        self._remote_connection = await self.connect_db()
        if self._remote_connection:
            logger.info("Initial database connection established")
        else:
            logger.warning("Initial database connection failed; session will operate in degraded mode")

    def run_sync(self, coro):
        if not asyncio.iscoroutine(coro):
            raise TypeError("run_sync expected a coroutine object")

        if threading.current_thread() is self._loop_thread:
            raise RuntimeError("run_sync cannot be called from the session event loop thread")

        if not self.loop.is_running():
            raise RuntimeError("Session event loop is not running")

        logger.debug(
            "Scheduling coroutine %s on event loop from thread %s",
            getattr(coro, "__name__", repr(coro)),
            threading.current_thread().name,
        )
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        try:
            result = future.result()
            logger.debug(
                "Coroutine %s completed successfully", getattr(coro, "__name__", repr(coro))
            )
            return result
        except Exception:
            logger.exception("Coroutine %s raised an exception", getattr(coro, "__name__", repr(coro)))
            raise

    def init_main_window(self, mw):
        self.main_window = mw
        if self._progress_emitter is None:
            self._progress_emitter = _ProgressEmitter()
        self._progress_emitter.moveToThread(mw.thread())
        self._progress_emitter.progress.connect(mw.set_progress_bar_status, Qt.QueuedConnection)
        if self._progress_state is not None:
            self._progress_emitter.progress.emit(self._progress_state)
        elif self._last_progress_message:
            self._progress_emitter.progress.emit(ProgressState(title=self._last_progress_message))
        logger.debug("Main window initialized for session progress updates")

    async def connect_db(self):
        logger.info("Attempting to connect to the database")
        try:
            connection = await asyncpg.connect(config.get_remote_db_url())
            logger.info("Database connection established successfully")
            return connection
        except Exception as e:
            self.update_loading_bar(f"Ошибка при попытке подключения к базе данных: {e}")
            logger.exception("Error connecting to the database")
            return None

    async def reconnect_db(self, retries=5, delay=5):
        logger.warning("Reconnecting to the database (retries=%s, delay=%ss)", retries, delay)
        async with self._reconnect_lock:
            if self.connected():
                logger.info("Reconnect skipped: existing connection is still active")
                return True

            last_error = None

            for attempt in range(retries):
                connection = None
                try:
                    logger.info("Reconnect attempt %s of %s", attempt + 1, retries)
                    connection = await self.connect_db()
                    if not connection:
                        last_error = RuntimeError("connect_db returned no connection")
                    else:
                        try:
                            async with self._execute_lock:
                                if self.connected():
                                    logger.info(
                                        "Another coroutine restored the connection while reconnecting"
                                    )
                                    await connection.close()
                                    connection = None
                                    return True

                                auth_success = True
                                if self._login and self._password:
                                    query = 'SELECT * FROM "sc_ref".checkuserpassword($1, $2)'
                                    try:
                                        value = await connection.fetchval(
                                            query, self._login, self._password
                                        )
                                        auth_success = bool(value)
                                        logger.info(
                                            "Reauthorization after reconnect returned %s",
                                            auth_success,
                                        )
                                    except Exception:
                                        auth_success = False
                                        logger.exception(
                                            "Failed to reauthorize after reconnect"
                                        )

                                if auth_success:
                                    old_connection = self._remote_connection
                                    self._remote_connection = connection
                                    self.update_loading_bar('Подключено.')
                                    logger.info("Reconnected to the database")
                                    if old_connection and not old_connection.is_closed():
                                        with contextlib.suppress(Exception):
                                            await old_connection.close()
                                    self._clear_menu_cache('database session reconnected')
                                    return True

                                last_error = RuntimeError(
                                    "Reauthorization failed after reconnect"
                                )
                        finally:
                            if connection and self._remote_connection is not connection:
                                with contextlib.suppress(Exception):
                                    await connection.close()
                except Exception as e:
                    last_error = e
                    logger.exception("Reconnection attempt %s failed", attempt + 1)

                if attempt < retries - 1:
                    await asyncio.sleep(delay)

            self.update_loading_bar('Не удалось подключиться к БД после нескольких попыток.')
            logger.error("Failed to reconnect to the database after several attempts")
            if last_error:
                logger.debug("Last reconnect error: %s", last_error)
            return False

    @property
    def progress_state(self):
        return self._progress_state

    @property
    def has_active_progress(self):
        return self._progress_state is not None and self._progress_started_at is not None

    def _emit_progress(self, state):
        if not getattr(self, 'main_window', None) or self._progress_emitter is None:
            logger.debug("Progress update queued (main window not ready): %s", state)
            return
        self._progress_emitter.progress.emit(state)

    def begin_progress(
        self, title, total=None, blocking=False, detail=None, suppress_loading_messages=False,
    ):
        current = 0 if total is not None else None
        self._progress_state = ProgressState(
            title=title, detail=detail, current=current, total=total, blocking=blocking,
        )
        self._last_progress_message = title
        self._suppress_loading_bar_messages = suppress_loading_messages
        self._progress_started_at = time.perf_counter()
        logger.info("Progress started: title=%s, total=%s", title, total)
        self._emit_progress(self._progress_state)
        return self._progress_state

    def update_progress(self, current=None, total=None, title=None, message=None, detail=None):
        state = self._progress_state or ProgressState()
        state = replace(
            state,
            title=title if title is not None else state.title,
            message=message if message is not None else state.message,
            detail=detail if detail is not None else state.detail,
            current=current if current is not None else state.current,
            total=total if total is not None else state.total,
        )
        self._progress_state = state
        self._last_progress_message = state.message or state.title
        self._emit_progress(state)
        return state

    def advance_progress(self, step=1, detail=None, message=None):
        state = self._progress_state or ProgressState(current=0)
        current = (state.current or 0) + step
        return self.update_progress(current=current, detail=detail, message=message)

    def end_progress(self):
        state = self._progress_state
        if state is not None:
            elapsed = (time.perf_counter() - self._progress_started_at
                       if self._progress_started_at is not None else 0.0)
            logger.info(
                "Progress completed: title=%s, current=%s, total=%s, elapsed=%.4fs",
                state.title, state.current, state.total, elapsed,
            )
        self._progress_state = None
        self._progress_started_at = None
        self._suppress_loading_bar_messages = False
        self._last_progress_message = None
        self._emit_progress(None)

    def progress(
        self, title, total=None, blocking=False, detail=None, suppress_loading_messages=False,
    ):
        return _ProgressContext(
            self, title, total, blocking, detail, suppress_loading_messages,
        )

    def update_loading_bar(self, message):
        """Backward-compatible string progress update."""
        if self.has_active_progress:
            if getattr(self, '_suppress_loading_bar_messages', False):
                logger.debug(
                    "Ignored loading bar message during active progress: %s",
                    message,
                )
                return self._progress_state
            return self.update_progress(message=message)
        self._last_progress_message = message
        self._progress_state = ProgressState(title=message)
        self._emit_progress(self._progress_state)
        logger.info("Progress bar message: %s", message)
        return self._progress_state

    async def execute(self, procedure_name, *args):
        t_execute_total = time.perf_counter()
        query = f'SELECT * FROM "sc_ref".{procedure_name}({",".join([f"${i + 1}" for i, _ in enumerate(args)])})'
        try:
            if self._execute_lock is None:
                logger.debug("Execute lock missing; initializing async state again")
                await self._initialize_async_state()

            if self._remote_connection is None or self._remote_connection.is_closed():
                logger.warning(
                    "Remote connection missing or closed before executing %s", procedure_name
                )
                if not await self.reconnect_db():
                    logger.error("Reconnection failed before executing %s", procedure_name)
                    return None

            logger.info(
                "Executing procedure %s with %s argument(s)",
                procedure_name,
                len(args),
            )

            db_timing_log(
                f"[DB execute START] {procedure_name}: args={args}, query={query}"
            )

            t_wait_lock = time.perf_counter()
            async with self._execute_lock:
                lock_wait_time = time.perf_counter() - t_wait_lock
                logger.debug("Execute lock acquired for %s", procedure_name)

                t_fetch = time.perf_counter()
                result = await self._remote_connection.fetch(query, *args)
                fetch_time = time.perf_counter() - t_fetch

            t_columns = time.perf_counter()
            columns = list(result[0].keys()) if len(result) else None
            columns_time = time.perf_counter() - t_columns

            total_time = time.perf_counter() - t_execute_total
            db_timing_log(
                f"[DB execute END] {procedure_name}: "
                f"rows={len(result)}, "
                f"lock_wait={lock_wait_time:.4f}s, "
                f"fetch={fetch_time:.4f}s, "
                f"columns={columns_time:.4f}s, "
                f"total={total_time:.4f}s"
            )

            return QueryResult(result, columns=columns)
        except (asyncpg.exceptions.ConnectionDoesNotExistError, asyncpg.exceptions.ConnectionFailureError):
            logger.warning("Connection lost while executing %s. Attempting to reconnect", procedure_name)
            self.update_loading_bar("Соединение потеряно. Попытка восстановления")
            if await self.reconnect_db():
                try:
                    db_timing_log(f"[DB execute RETRY START] {procedure_name}: args={args}")

                    t_wait_lock = time.perf_counter()
                    async with self._execute_lock:
                        lock_wait_time = time.perf_counter() - t_wait_lock
                        logger.debug(
                            "Execute lock reacquired for %s after reconnect", procedure_name
                        )

                        t_fetch = time.perf_counter()
                        result = await self._remote_connection.fetch(query, *args)
                        fetch_time = time.perf_counter() - t_fetch

                    t_columns = time.perf_counter()
                    columns = list(result[0].keys()) if len(result) else None
                    columns_time = time.perf_counter() - t_columns

                    db_timing_log(
                        f"[DB execute RETRY END] {procedure_name}: "
                        f"rows={len(result)}, "
                        f"lock_wait={lock_wait_time:.4f}s, "
                        f"fetch={fetch_time:.4f}s, "
                        f"columns={columns_time:.4f}s"
                    )

                    return QueryResult(result, columns=columns)
                except Exception as e:
                    logger.exception("Error executing %s after reconnect", procedure_name)
                    return e
            else:
                logger.error("Reconnect failed after connection loss during %s", procedure_name)
                return None
        except Exception as e:
            logger.exception("Unexpected error executing %s", procedure_name)
            return e


    async def copy_import_file_data_records(
        self, rows, batch_size=None, progress_callback=None, insert_progress_callback=None,
    ):
        """Load import_file_data rows through a transaction-local temp table."""
        if self._execute_lock is None:
            logger.debug("Execute lock missing; initializing async state again")
            await self._initialize_async_state()

        if self._remote_connection is None or self._remote_connection.is_closed():
            logger.warning("Remote connection missing or closed before COPY import")
            if not await self.reconnect_db():
                raise RuntimeError("Database reconnect failed before COPY import")

        async with self._execute_lock:
            async with self._remote_connection.transaction():
                await self._remote_connection.execute("""
                    CREATE TEMP TABLE tmp_import_file_data_stage (
                        stage_id bigserial PRIMARY KEY,
                        id_excel_file integer,
                        file_version integer,
                        param_prop_name varchar,
                        date_time_izm timestamp,
                        zamer_n integer,
                        rejim_zamer varchar,
                        prop_value text,
                        npp integer,
                        id_name integer
                    ) ON COMMIT DROP
                """)
                copy_started_at = time.perf_counter()
                columns = (
                    'id_excel_file',
                    'file_version',
                    'param_prop_name',
                    'date_time_izm',
                    'zamer_n',
                    'rejim_zamer',
                    'prop_value',
                    'npp',
                    'id_name',
                )
                total_rows = len(rows)
                if batch_size and batch_size > 0:
                    copied_rows = 0
                    for offset in range(0, total_rows, batch_size):
                        batch = rows[offset:offset + batch_size]
                        await self._remote_connection.copy_records_to_table(
                            'tmp_import_file_data_stage',
                            records=batch,
                            columns=columns,
                        )
                        copied_rows += len(batch)
                        if progress_callback is not None:
                            progress_callback(copied_rows, total_rows)
                else:
                    await self._remote_connection.copy_records_to_table(
                        'tmp_import_file_data_stage',
                        records=rows,
                        columns=columns,
                    )
                    if progress_callback is not None:
                        progress_callback(total_rows, total_rows)
                logger.info(
                    "WorkData import COPY completed: records=%s, elapsed=%.4fs",
                    total_rows,
                    time.perf_counter() - copy_started_at,
                )
                insert_started_at = time.perf_counter()
                insert_batch_size = batch_size or 10000
                inserted_total = 0
                if insert_progress_callback is not None:
                    insert_progress_callback(0, total_rows)
                for start_id in range(1, total_rows + 1, insert_batch_size):
                    end_id = min(start_id + insert_batch_size - 1, total_rows)
                    status = await self._remote_connection.execute("""
                        INSERT INTO sc_ref.import_file_data (
                            id_excel_file,
                            file_version,
                            param_prop_name,
                            date_time_izm,
                            zamer_n,
                            rejim_zamer,
                            prop_value,
                            npp,
                            id_name
                        )
                        SELECT
                            id_excel_file,
                            file_version,
                            param_prop_name,
                            date_time_izm,
                            zamer_n,
                            rejim_zamer,
                            prop_value,
                            npp,
                            id_name
                        FROM tmp_import_file_data_stage
                        WHERE stage_id BETWEEN $1 AND $2
                        ORDER BY stage_id
                    """, start_id, end_id)
                    try:
                        inserted_count = int(status.rsplit(' ', 1)[-1])
                    except (AttributeError, TypeError, ValueError):
                        logger.warning("Could not parse INSERT status after COPY import: %s", status)
                        inserted_count = end_id - start_id + 1
                    inserted_total += inserted_count
                    if insert_progress_callback is not None:
                        insert_progress_callback(inserted_total, total_rows)
                logger.info(
                    "WorkData import INSERT SELECT completed: inserted=%s, elapsed=%.4fs",
                    inserted_total,
                    time.perf_counter() - insert_started_at,
                )

        return inserted_total

    def copy_import_file_data(
        self, rows, batch_size=None, progress_callback=None, insert_progress_callback=None,
    ):
        return self.run_sync(
            self.copy_import_file_data_records(
                rows, batch_size, progress_callback, insert_progress_callback,
            )
        )

    def call(self, query, *args):
        logger.debug(
            "call invoked for %s with %s argument(s) (main window available: %s)",
            query,
            len(args),
            bool(self.main_window),
        )
        try:
            if self.main_window:
                return self.main_window.run_with_progress(
                    lambda: self.run_sync(self.execute(query, *args)))
            else:
                return self.run_sync(self.execute(query, *args))
        except Exception as e:
            logger.exception("Error executing call for %s", query)

    def stored_procedure(self, modifying=False, result_type=None, description=None, autocommit=False):
        def decorator(func):
            sig = signature(func)
            return_type = sig.return_annotation

            def parse_obj_as(return_type_, res):
                t_parse_total = time.perf_counter()

                if res is None or isinstance(res, Exception):
                    logger.error("Error during procedure execution in %s: %s", func.__name__, res)
                    db_timing_log(
                        f"[DB parse ERROR] {func.__name__}: res={res}, "
                        f"time={time.perf_counter() - t_parse_total:.4f}s"
                    )
                    return None

                raw_rows_count = len(res.result) if getattr(res, 'result', None) is not None else 0
                columns_count = len(res.columns) if getattr(res, 'columns', None) is not None else 0
                db_timing_log(
                    f"[DB parse START] {func.__name__}: "
                    f"return_type={return_type_}, "
                    f"raw_rows={raw_rows_count}, "
                    f"columns={columns_count}"
                )

                if return_type_ in [bool, int, float]:
                    t_scalar = time.perf_counter()
                    one = res.one()

                    if one is None:
                        db_timing_log(
                            f"[DB parse END] {func.__name__}: scalar empty result, "
                            f"scalar_time={time.perf_counter() - t_scalar:.4f}s, "
                            f"total={time.perf_counter() - t_parse_total:.4f}s"
                        )
                        return None

                    if one[0] is None:
                        db_timing_log(
                            f"[DB parse END] {func.__name__}: scalar None, "
                            f"scalar_time={time.perf_counter() - t_scalar:.4f}s, "
                            f"total={time.perf_counter() - t_parse_total:.4f}s"
                        )
                        return None

                    value = return_type_(one[0])
                    db_timing_log(
                        f"[DB parse END] {func.__name__}: scalar={type(value).__name__}, "
                        f"scalar_time={time.perf_counter() - t_scalar:.4f}s, "
                        f"total={time.perf_counter() - t_parse_total:.4f}s"
                    )
                    return value

                if not isinstance(return_type_, typing._GenericAlias):
                    if return_type_ is None:
                        db_timing_log(
                            f"[DB parse END] {func.__name__}: return_type is None, "
                            f"total={time.perf_counter() - t_parse_total:.4f}s"
                        )
                        return None

                    as_type = res.columns
                    value = res.one()

                    if value is None:
                        db_timing_log(
                            f"[DB parse END] {func.__name__}: one=None, "
                            f"total={time.perf_counter() - t_parse_total:.4f}s"
                        )
                        return None

                    constructor_factory = getattr(return_type_, '_get_row_constructor', None)
                    if constructor_factory is not None and as_type is not None:
                        obj = constructor_factory(as_type)(value)
                    else:
                        obj = return_type_({as_type[i]: value[i] for i in range(len(value))})

                    db_timing_log(
                        f"[DB parse END] {func.__name__}: one_model={return_type_.__name__}, "
                        f"total={time.perf_counter() - t_parse_total:.4f}s"
                    )
                    return obj

                as_type = res.columns
                res_one = res.one()
                return_type_ = return_type_.__args__[0]

                # ВАЖНЫЙ ФИКС:
                # если процедура вернула пустой список, не пытаемся строить row_constructor
                # по columns=None. Старое поведение было — вернуть [].
                if not res.result:
                    db_timing_log(
                        f"[DB parse END] {func.__name__}: empty list result, "
                        f"model={getattr(return_type_, '__name__', return_type_)}, "
                        f"total={time.perf_counter() - t_parse_total:.4f}s"
                    )
                    return []

                if return_type_ in [int, bool, str]:
                    t_list_scalar = time.perf_counter()
                    if isinstance(res_one, list) or isinstance(res_one, tuple):
                        result_list = [
                            return_type_(val) if val is not None else None
                            for val in res_one[0]
                        ]
                    else:
                        result_list = [
                            return_type_(val) if val is not None else None
                            for val in list(res_one)[0]
                        ]

                    db_timing_log(
                        f"[DB parse END] {func.__name__}: list_scalar={return_type_.__name__}, "
                        f"rows={len(result_list)}, "
                        f"list_time={time.perf_counter() - t_list_scalar:.4f}s, "
                        f"total={time.perf_counter() - t_parse_total:.4f}s"
                    )
                    return result_list

                t_loop = time.perf_counter()
                constructor_factory = getattr(return_type_, '_get_row_constructor', None)

                if constructor_factory is not None and as_type is not None:
                    row_constructor = constructor_factory(as_type)
                    parsed_result = [row_constructor(row) for row in res.result]
                else:
                    parsed_result = [
                        return_type_({as_type[i]: row[i] for i in range(len(row))})
                        for row in res.result
                    ]

                loop_time = time.perf_counter() - t_loop
                res.result = parsed_result

                db_timing_log(
                    f"[DB parse END] {func.__name__}: "
                    f"model={return_type_.__name__}, "
                    f"rows={len(parsed_result)}, "
                    f"loop={loop_time:.4f}s, "
                    f"total={time.perf_counter() - t_parse_total:.4f}s"
                )
                return res.all()

            @wraps(func)
            def wrapper(*args, **kwargs):
                t_wrapper_total = time.perf_counter()

                # Адаптация аргументов
                logger.info(
                    "Calling stored procedure wrapper %s (description=%s)",
                    func.__name__,
                    description or 'Загрузка'
                )
                db_timing_log(
                    f"[DB wrapper START] {func.__name__}: "
                    f"description={description or 'Загрузка'}, "
                    f"return_type={return_type}, "
                    f"args={args}, kwargs={kwargs}"
                )

                t_progress = time.perf_counter()
                self.update_loading_bar(description if description else 'Загрузка')
                progress_time = time.perf_counter() - t_progress

                t_func = time.perf_counter()
                result = func(*args, **kwargs)
                func_time = time.perf_counter() - t_func

                if isinstance(result, RaiseError):
                    logger.error("Stored procedure %s raised database error: %s", func.__name__, result)
                    if 'seslogin' in str(result):
                        self.call('checkuserpassword', self._login, self._password)
                        self._clear_menu_cache('database session reauthorized')
                    db_timing_log(
                        f"[DB wrapper END] {func.__name__}: RaiseError, "
                        f"progress={progress_time:.4f}s, "
                        f"func_call={func_time:.4f}s, "
                        f"total={time.perf_counter() - t_wrapper_total:.4f}s"
                    )
                    return result

                t_parse = time.perf_counter()
                parsed = parse_obj_as(return_type, result)
                parse_time = time.perf_counter() - t_parse

                total_time = time.perf_counter() - t_wrapper_total
                parsed_len = len(parsed) if isinstance(parsed, list) else 'not_list'
                db_timing_log(
                    f"[DB wrapper END] {func.__name__}: "
                    f"progress={progress_time:.4f}s, "
                    f"func_call={func_time:.4f}s, "
                    f"parse={parse_time:.4f}s, "
                    f"total={total_time:.4f}s, "
                    f"parsed_len={parsed_len}"
                )
                return parsed

            return wrapper

        return decorator

    @staticmethod
    def _clear_menu_cache(reason):
        # Lazy import keeps database Session initialization independent from
        # the application-level menu service.
        from app.menu_service import clear_menu_cache

        clear_menu_cache(reason)

    def connected(self) -> bool:
        return self._remote_connection and not self._remote_connection.is_closed()

    def close(self):
        logger.info("Closing session")
        self._clear_menu_cache('database session closed')
        if self.connected():
            # noinspection PyBroadException
            try:
                logger.debug("Closing remote database connection")
                self.run_sync(self._remote_connection.close())
            except Exception:
                logger.exception("Error while closing remote connection")
            finally:
                self._remote_connection = None
        if self.loop.is_running():
            self.loop.call_soon_threadsafe(self.loop.stop)
            logger.debug("Stopping event loop thread")
            self._loop_thread.join()
            logger.debug("Event loop thread joined")
        else:
            logger.debug("Event loop already stopped")
        self.loop.close()
        logger.info("Session closed")

    def authorize(self, login, password, auth_manually=False):
        self._login = login
        self._password = password
        self._clear_menu_cache('authorization updated')
        logger.info(
            "Authorization updated (login=%s, manual=%s)",
            login,
            auth_manually,
        )

    def logout(self):
        """Clear local authorization state without closing the reusable DB connection."""
        logger.info("Logout started")
        self._login = None
        self._password = None
        self.main_window = None
        self._clear_menu_cache('user logged out')
        logger.info("Logout completed")
