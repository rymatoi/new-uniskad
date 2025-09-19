import asyncio
import threading
from functools import wraps
from inspect import signature

import asyncpg
import typing

from PySide2.QtCore import QObject, QThread, Signal
from asyncpg import RaiseError
from config.config import config


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

        self.run_sync(self._initialize_async_state())

    def _run_event_loop(self):
        asyncio.set_event_loop(self.loop)
        self._loop_ready.set()
        self.loop.run_forever()

    async def _initialize_async_state(self):
        self._execute_lock = asyncio.Lock()
        self._reconnect_lock = asyncio.Lock()
        self._remote_connection = await self.connect_db()

    def run_sync(self, coro):
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return future.result()

    def init_main_window(self, mw):
        self.main_window = mw
        self._progress_emitter.progress.connect(mw.set_progress_bar_status)

    async def connect_db(self):
        try:
            connection = await asyncpg.connect(config.get_remote_db_url())
            return connection
        except Exception as e:
            self.update_loading_bar(f"Ошибка при попытке подключения к базе данных: {e}")
            print(f"Error connecting to the database: {e}")
            return None

    async def reconnect_db(self, retries=5, delay=5):
        async with self._reconnect_lock:
            for attempt in range(retries):
                try:
                    self._remote_connection = await self.connect_db()
                    if self._remote_connection:
                        self.update_loading_bar('Подключено.')
                        print("Reconnected to the database.")
                        if self._login and self._password:
                            query = 'SELECT * FROM "sc_ref".checkuserpassword($1, $2)'
                            try:
                                async with self._execute_lock:
                                    value = await self._remote_connection.fetchval(
                                        query, self._login, self._password)
                                return bool(value)
                            except Exception as e:
                                print(f"Failed to reauthorize after reconnect: {e}")
                                return False
                        return True
                except Exception as e:
                    print(f"Reconnection attempt {attempt + 1} failed: {e}")
                await asyncio.sleep(delay)
            self.update_loading_bar('Не удалось подключиться к БД после нескольких попыток.')
            print("Failed to reconnect to the database after several attempts.")
            return False

    def update_loading_bar(self, message):
        if not getattr(self, 'main_window', None):
            return

        main_window = self.main_window
        if QThread.currentThread() is main_window.thread():
            main_window.set_progress_bar_status(message)
        else:
            self._progress_emitter.progress.emit(message)

    async def execute(self, procedure_name, *args):
        query = f'SELECT * FROM "sc_ref".{procedure_name}({",".join([f"${i + 1}" for i, _ in enumerate(args)])})'
        try:
            if self._execute_lock is None:
                await self._initialize_async_state()

            if self._remote_connection is None or self._remote_connection.is_closed():
                if not await self.reconnect_db():
                    return None

            async with self._execute_lock:
                result = await self._remote_connection.fetch(query, *args)

            return QueryResult(result, columns=list(result[0].keys()) if len(result) else None)
        except (asyncpg.exceptions.ConnectionDoesNotExistError, asyncpg.exceptions.ConnectionFailureError):
            print("Connection lost. Attempting to reconnect...")
            self.update_loading_bar("Соединение потеряно. Попытка восстановления")
            if await self.reconnect_db():
                try:
                    async with self._execute_lock:
                        result = await self._remote_connection.fetch(query, *args)
                    return QueryResult(result, columns=list(result[0].keys()) if len(result) else None)
                except Exception as e:
                    return e
            else:
                return None
        except Exception as e:
            return e

    def call(self, query, *args):
        try:
            if self.main_window:
                return self.main_window.run_with_progress(
                    lambda: self.run_sync(self.execute(query, *args)))
            else:
                return self.run_sync(self.execute(query, *args))
        except Exception as e:
            print(e)

    def stored_procedure(self, modifying=False, result_type=None, description=None, autocommit=False):
        def decorator(func):
            sig = signature(func)
            return_type = sig.return_annotation

            def parse_obj_as(return_type_, res):
                if res is None or isinstance(res, Exception):
                    print(f"Error during procedure execution: {res}")
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
                self.update_loading_bar(description if description else 'Загрузка')
                result = func(*args, **kwargs)
                if isinstance(result, RaiseError):
                    print(str(result))
                    if 'seslogin' in str(result):
                        self.call('checkuserpassword', self._login, self._password)
                    return result

                return parse_obj_as(return_type, result)

            return wrapper

        return decorator

    def connected(self) -> bool:
        return self._remote_connection and not self._remote_connection.is_closed()

    def close(self):
        if self.connected():
            # noinspection PyBroadException
            try:
                self.run_sync(self._remote_connection.close())
            except Exception:
                pass
        self.loop.call_soon_threadsafe(self.loop.stop)
        self._loop_thread.join()
        self.loop.close()

    def authorize(self, login, password, auth_manually=False):
        self._login = login
        self._password = password
