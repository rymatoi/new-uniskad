import asyncio
import threading
from functools import wraps
from inspect import signature

import asyncpg
import typing

from PySide2.QtCore import QObject, QThread, Signal
from asyncpg import RaiseError
from config.config import config

from app import app_logger

logger = app_logger.get_logger(__name__)


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
    result_ready = Signal(object)
    started = Signal()
    finished = Signal()

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.started.emit()
        result = self.func(*self.args, **self.kwargs)
        self.result_ready.emit(result)
        self.finished.emit()


class _ProgressEmitter(QObject):
    progress = Signal(str)


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
        self._progress_emitter = _ProgressEmitter()

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
        self._progress_emitter.progress.connect(mw.set_progress_bar_status)
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
            for attempt in range(retries):
                try:
                    logger.info("Reconnect attempt %s of %s", attempt + 1, retries)
                    self._remote_connection = await self.connect_db()
                    if self._remote_connection:
                        self.update_loading_bar('Подключено.')
                        logger.info("Reconnected to the database")
                        if self._login and self._password:
                            query = 'SELECT * FROM "sc_ref".checkuserpassword($1, $2)'
                            try:
                                async with self._execute_lock:
                                    value = await self._remote_connection.fetchval(
                                        query, self._login, self._password)
                                logger.info(
                                    "Reauthorization after reconnect returned %s",
                                    bool(value)
                                )
                                return bool(value)
                            except Exception as e:
                                logger.exception("Failed to reauthorize after reconnect")
                                return False
                        return True
                except Exception as e:
                    logger.exception("Reconnection attempt %s failed", attempt + 1)
                await asyncio.sleep(delay)
            self.update_loading_bar('Не удалось подключиться к БД после нескольких попыток.')
            logger.error("Failed to reconnect to the database after several attempts")
            return False

    def update_loading_bar(self, message):
        if not getattr(self, 'main_window', None):
            logger.debug("Progress update skipped (main window not ready): %s", message)
            return

        main_window = self.main_window
        if QThread.currentThread() is main_window.thread():
            main_window.set_progress_bar_status(message)
        else:
            self._progress_emitter.progress.emit(message)
        logger.info("Progress bar message: %s", message)

    async def execute(self, procedure_name, *args):
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
            async with self._execute_lock:
                logger.debug("Execute lock acquired for %s", procedure_name)
                result = await self._remote_connection.fetch(query, *args)

            return QueryResult(result, columns=list(result[0].keys()) if len(result) else None)
        except (asyncpg.exceptions.ConnectionDoesNotExistError, asyncpg.exceptions.ConnectionFailureError):
            logger.warning("Connection lost while executing %s. Attempting to reconnect", procedure_name)
            self.update_loading_bar("Соединение потеряно. Попытка восстановления")
            if await self.reconnect_db():
                try:
                    async with self._execute_lock:
                        logger.debug(
                            "Execute lock reacquired for %s after reconnect", procedure_name
                        )
                        result = await self._remote_connection.fetch(query, *args)
                    return QueryResult(result, columns=list(result[0].keys()) if len(result) else None)
                except Exception as e:
                    logger.exception("Error executing %s after reconnect", procedure_name)
                    return e
            else:
                logger.error("Reconnect failed after connection loss during %s", procedure_name)
                return None
        except Exception as e:
            logger.exception("Unexpected error executing %s", procedure_name)
            return e

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
                if res is None or isinstance(res, Exception):
                    logger.error("Error during procedure execution in %s: %s", func.__name__, res)
                    return None

                if return_type_ in [bool, int, float]:
                    if res.one()[0] is None:
                        return None
                    return return_type_(res.one()[0])

                if not isinstance(return_type_, typing._GenericAlias):
                    if return_type_ is None:
                        return None
                    as_type = res.columns
                    value = res.one()
                    if value is None:
                        return None
                    _kwargs = {as_type[i]: value[i] for i in range(len(value))}
                    return return_type_(_kwargs)
                else:
                    as_type = res.columns
                    res_one = res.one()
                    return_type_ = return_type_.__args__[0]
                    if return_type_ in [int, bool, str]:
                        if isinstance(res_one, list) or isinstance(res_one, tuple):
                            return [return_type_(val) if val is not None else None for val in res_one[0]]
                        else:
                            return [return_type_(val) if val is not None else None for val in list(res_one)[0]]
                    parsed_result = []
                    for row in res.result:
                        _kwargs = {as_type[i]: row[i] for i in range(len(row))}
                        parsed_result.append(return_type_(_kwargs))
                    res.result = parsed_result
                    return res.all()

            @wraps(func)
            def wrapper(*args, **kwargs):
                # Адаптация аргументов
                logger.info(
                    "Calling stored procedure wrapper %s (description=%s)",
                    func.__name__,
                    description or 'Загрузка'
                )
                self.update_loading_bar(description if description else 'Загрузка')
                result = func(*args, **kwargs)
                if isinstance(result, RaiseError):
                    logger.error("Stored procedure %s raised database error: %s", func.__name__, result)
                    if 'seslogin' in str(result):
                        self.call('checkuserpassword', self._login, self._password)
                    return result

                return parse_obj_as(return_type, result)

            return wrapper

        return decorator

    def connected(self) -> bool:
        return self._remote_connection and not self._remote_connection.is_closed()

    def close(self):
        logger.info("Closing session")
        if self.connected():
            # noinspection PyBroadException
            try:
                logger.debug("Closing remote database connection")
                self.run_sync(self._remote_connection.close())
            except Exception:
                logger.exception("Error while closing remote connection")
        self.loop.call_soon_threadsafe(self.loop.stop)
        logger.debug("Stopping event loop thread")
        self._loop_thread.join()
        logger.debug("Event loop thread joined")
        self.loop.close()
        logger.info("Session closed")

    def authorize(self, login, password, auth_manually=False):
        self._login = login
        self._password = password
        logger.info(
            "Authorization updated (login=%s, manual=%s)",
            login,
            auth_manually,
        )
