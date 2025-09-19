import asyncio
from functools import wraps
from inspect import signature

import asyncpg
import typing

from PySide2.QtCore import QThread, Signal
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


class Session:
    def __init__(self, **dsn):
        self.dsn = dsn
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self._remote_connection = self.loop.run_until_complete(self.connect_db())
        self.main_window = None
        self._login = None
        self._password = None

    def init_main_window(self, mw):
        self.main_window = mw

    async def connect_db(self):
        try:
            connection = await asyncpg.connect(config.get_remote_db_url())
            return connection
        except Exception as e:
            self.update_loading_bar(f"Ошибка при попытке подключения к базе данных: {e}")
            print(f"Error connecting to the database: {e}")
            return None

    async def reconnect_db(self, retries=5, delay=5):
        for attempt in range(retries):
            try:
                self._remote_connection = await self.connect_db()
                if self._remote_connection:
                    self.update_loading_bar('Подключено.')
                    print("Reconnected to the database.")
                    success = self.call('checkuserpassword', self._login, self._password)
                    return success
            except Exception as e:
                print(f"Reconnection attempt {attempt + 1} failed: {e}")
            await asyncio.sleep(delay)
        self.update_loading_bar('Не удалось подключиться к БД после нескольких попыток.')
        print("Failed to reconnect to the database after several attempts.")
        return False

    def update_loading_bar(self, message):
        if hasattr(self, 'main_window') and self.main_window:
            self.main_window.set_progress_bar_status(message)

    async def execute(self, procedure_name, *args):
        query = f'SELECT * FROM "sc_ref".{procedure_name}({",".join([f"${i + 1}" for i, _ in enumerate(args)])})'
        try:
            if self._remote_connection is None or self._remote_connection.is_closed():
                if not await self.reconnect_db():
                    return None
            result = await self._remote_connection.fetch(query, *args)
            return QueryResult(result, columns=list(result[0].keys()) if len(result) else None)
        except (asyncpg.exceptions.ConnectionDoesNotExistError, asyncpg.exceptions.ConnectionFailureError):
            print("Connection lost. Attempting to reconnect...")
            self.update_loading_bar("Соединение потеряно. Попытка восстановления")
            if await self.reconnect_db():
                try:
                    result = await self._remote_connection.fetch(query, *args)
                    return QueryResult(result, columns=list(result[0].keys()) if len(result) else None)
                except Exception as e:
                    return e
            else:
                return None
        except Exception as e:
            return e

    def call(self, query, *args):
        if self.loop.is_running():
            return None
        try:
            if self.main_window:
                return self.main_window.run_with_progress(
                    lambda: self.loop.run_until_complete(self.execute(query, *args)))
            else:
                return self.loop.run_until_complete(self.execute(query, *args))
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
                self.loop.run_until_complete(self._remote_connection.close())
            except Exception:
                pass

    def authorize(self, login, password, auth_manually=False):
        self._login = login
        self._password = password
