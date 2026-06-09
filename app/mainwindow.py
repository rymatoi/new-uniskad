import ast
import json
from typing import Any, Dict, Optional

from PySide2 import QtWidgets
from PySide2.QtCore import QEventLoop, Slot
from PySide2.QtGui import QIcon, QCloseEvent, Qt, QKeySequence
from PySide2.QtWidgets import QShortcut, QDockWidget, QProgressBar, QLabel
from app import app_logger, _menu, basic_funcs
from app.cache import DataCache
from app.menu_service import clear_menu_cache, get_menu
from app.history_manager.history_manager import EventStack
from app.notifications import StackedNotifications
from app.ui_font import apply_application_font
from app.plugins import *
from app.plugins.admin_users.widgets.docks import AdminUsersDockWidget
from app.plugins.base_state.widgets import TreeView, DockWidget
from app.plugins.project.widgets.docks import ProjectDockWidget
from db import sp
from db._session import Worker
from db.user_settings import UserSettings
from dialogs.help import HelpApp
from resources.ui.ui_py.ui_mainwindow import Ui_MainWindow
from settings.dialog import SettingsDialog
from widgets.role_switcher import RoleSwitcherWidget
from db import session
import config.config

logger = app_logger.get_logger(__name__)


class Dock_:
    """
    Небольшой класс для док-виджетов
    """

    def __init__(self, title, tree_name, area, dock_class=DockWidget):
        self.title = title
        self.tree_name = tree_name
        self.area = area

        self.dock_class = dock_class


class MainWindow(QtWidgets.QMainWindow):
    # modes
    BASE_STATE = 'base_state'
    ADMIN = 'admin'
    SYNONYM_DICTIONARY = 'synonym_dictionary'
    EIZM_DICTIONARY = 'eizm_dictionary'
    PROJECT = 'project'
    WORK_DATA = 'work_data'

    # sub modes
    ADMIN_ROLES = 'admin_roles'
    ADMIN_USERS = 'admin_users'

    # tree views for modes (action names)
    ADMIN_ROLES_TREE = '_roles_treeview'
    ADMIN_USERS_TREE = '_users_treeview'
    SYNONYM_DICTIONARY_TREE = '_synonym_dictionary_treeview'
    EIZM_DICTIONARY_TREE = '_eizm_dictionary_treeview'
    PROJECT_TREE = '_project_treeview'
    WORK_DATA_TREE = '_products_treeview'

    # roles
    ADMIN_ROLE = '_role_200'
    USER_ROLE = '_role_100'
    DEVELOPER_ROLE = '_role_1000'

    def __init__(self):

        self.version = '250425'
        self.script_version = '2025'

        super(MainWindow, self).__init__()

        self.user_settings = UserSettings()
        self._tree_states_to_restore = {}
        self._pending_window_state_bytes = None
        self._pending_central_window_state_bytes = None

        config.config.app.enable_timer(self.user_settings.get('application_close_timeout', 30))
        config.config.app._main_window_initialized = True  # TODO test

        self.result = None

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.user = None
        self.init_user()

        self.data_cache = DataCache()

        session.init_main_window(self)

        self.roles = []
        self.available_actions = []
        self.available_modes = []
        self.plugins_dict = {
            self.BASE_STATE: BasePlugin,
            self.ADMIN_ROLES: AdminRolesPlugin,
            self.ADMIN_USERS: AdminUsersPlugin,
            self.SYNONYM_DICTIONARY: SynonymDictionaryPlugin,
            self.EIZM_DICTIONARY: EizmDictionaryPlugin,
            self.PROJECT: ProjectPlugin,
            self.WORK_DATA: WorkDataPlugin
        }

        self.dock_widgets = {
            self.ADMIN_ROLES: Dock_('Роли', self.ADMIN_ROLES_TREE, Qt.LeftDockWidgetArea),
            self.ADMIN_USERS: Dock_('Пользователи', self.ADMIN_USERS_TREE, Qt.LeftDockWidgetArea, AdminUsersDockWidget),
            self.WORK_DATA: Dock_('Изделия', self.WORK_DATA_TREE, Qt.RightDockWidgetArea),
            self.SYNONYM_DICTIONARY: Dock_('Словарь синонимов', self.SYNONYM_DICTIONARY_TREE, Qt.RightDockWidgetArea),
            self.EIZM_DICTIONARY: Dock_('Словарь единиц измерения', self.EIZM_DICTIONARY_TREE,
                                        Qt.RightDockWidgetArea),
            self.PROJECT: Dock_('Дерево проекта', self.PROJECT_TREE, Qt.LeftDockWidgetArea, ProjectDockWidget)
        }

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        self.progress_bar.setVisible(False)
        self._current_progress_message = ''

        self.status_label = QLabel()

        self.statusBar().addWidget(self.progress_bar)
        self.statusBar().addWidget(self.status_label)

        self.work_data = None
        self.admin_roles = None
        self.admin_users = None
        self.synonym_dictionary = None
        self.eizm_dictionary = None
        self.project = None
        self.base_state = None

        self.help_shown = False

        self.setWindowIcon(QIcon(":/uniskad.ico"))
        self.setWindowTitle(session._login)
        # self.setStyleSheet("MainWindow::title {text-align: center;}")

        # self.setWindowTitle('UNISKAD')

        self.init_modes()
        self.init_menu()
        self.init_roles()
        self.init_dock_widgets()

        self.connect_triggered_funcs()

        self.notification = None
        self.notifications_enabled = True
        self.notifications_timeout = 10000
        self.init_notifications()

        self.event_stack = EventStack()
        shortcut_undo = QShortcut(QKeySequence('Ctrl+Z'), self)
        shortcut_undo.activated.connect(self.event_stack.undo)

        shortcut_redo = QShortcut(QKeySequence('Ctrl+Shift+Z'), self)
        shortcut_redo.activated.connect(self.event_stack.redo)

        self.restore_windows_state()
        self.apply_runtime_settings()

    def show_message_sb(self, message, timeout=5000):
        pass
        # self.statusBar().showMessage(message, timeout)

    def init_notifications(self):
        """
        Инициализация виджета уведомлений
        """
        self.notification = StackedNotifications(self)
        self.notification.setGeometry(100, 100, 600, 100)
        self.notification.hide()

    def show_notification(self, text):
        """
        Показывает окошко с уведомлением
        """
        if not self.notifications_enabled:
            return
        self.notification.show()
        self.notification.add_notification(text, self.notifications_timeout)

    def set_statusbar_text(self, text):
        """
        Обновляет текст статус бара
        :param text:
        :return:
        """
        pass
        # self.statusBar().showMessage(text, 1000)

    def init_user(self):
        """
        Инициализация пользователя
        :return:
        """
        current_user_name = sp.get_sesion_user()
        self.user = next(
            user for user in sp.get_full_users_list() if user.login == current_user_name['get_sesion_user'])

    def init_roles(self):
        """Load the available roles and initialize the current role."""
        self.roles = sp.get_user_role_list_()
        for role in self.roles:
            role.name = f'_role_{role.id}'
        self.current_role = self._get_default_user_role()

    def create_role_switcher(self, parent=None):
        """Create a role-switching control for embedding in application UI."""
        return RoleSwitcherWidget(self, parent)

    def _get_default_user_role(self):
        """
        Возвращает роль пользователя по умолчанию
        :return:
        """
        return [role for role in self.roles if role.id_role == self.user.default_id_role][0]

    def init_dock_widgets(self):
        """
        Первоначальная инициализация док-виджетов
        :return:
        """
        for dock_name, dock_data in self.dock_widgets.items():
            dock_widget = dock_data.dock_class(dock_data.title, dock_data.tree_name, dock_name, self)
            dock_widget.setObjectName(f'{dock_name}_dock_widget')
            setattr(self, f"{dock_name}_tree_dock_widget", dock_widget)
            dock_widget.setWindowTitle(dock_data.title)
            dock_widget.setWidget(TreeView(self))
            self.addDockWidget(dock_data.area, dock_widget)
            dock_widget.hide()

    def init_menu(self):
        """
        Инициализация главного меню
        :return:
        """
        logger.info('Инициализация меню.')
        menu_list = get_menu('any', 'main_menu')
        _menu.init_menu(menu_list, self, self.menuBar())
        logger.info('Инициализация меню прошла успешно.')

    def _connect_func(self, action_name, func, *args):
        """
        Функция-хелпер для связи действий с функциями
        :param action_name: имя действия
        :param func: функция для связи
        :param args: аргументы для функции
        :return:
        """
        action = getattr(self, action_name, None)
        if action and action_name in self.available_actions:
            if args:
                action.triggered.connect(lambda: func(*args))
            else:
                action.triggered.connect(func)

    def connect_triggered_funcs(self):
        """
        Связь всех действий с функциями
        :return:
        """
        func_map = {
            '_select_project': (self.activate_tree, self.project, self.project_tree_dock_widget, self.PROJECT_TREE),
            '_import_excel': (self.import_files, 'excel'),
            '_exit': (self._close,),
            '_admin_roles': (
                self.activate_tree, self.admin_roles, self.admin_roles_tree_dock_widget, self.ADMIN_ROLES_TREE),
            '_admin_users': (
                self.activate_tree, self.admin_users, self.admin_users_tree_dock_widget, self.ADMIN_USERS_TREE),
            '_products_treeview': (self.show_tree, self.WORK_DATA_TREE),
            '_clear_modes': (lambda: None,),
            '_users_treeview': (self.show_tree, self.ADMIN_USERS_TREE),
            '_roles_treeview': (self.show_tree, self.ADMIN_ROLES_TREE),
            '_synonym_dictionary_treeview': (self.show_tree, self.SYNONYM_DICTIONARY_TREE),
            '_eizm_dictionary_treeview': (self.show_tree, self.EIZM_DICTIONARY_TREE),
            '_project_treeview': (self.show_tree, self.PROJECT_TREE),
            '_settings': (self.show_settings,),
            '_products_dictionary': (
                self.activate_tree, self.work_data, self.work_data_tree_dock_widget, self.WORK_DATA_TREE),
            '_synonym_dictionary': (
                self.activate_tree, self.synonym_dictionary, self.synonym_dictionary_tree_dock_widget,
                self.SYNONYM_DICTIONARY_TREE),
            '_eizm_dictionary': (self.activate_tree, self.eizm_dictionary, self.eizm_dictionary_tree_dock_widget,
                                 self.EIZM_DICTIONARY_TREE),
            '_help_docs': (self.show_help,),
            '_about': (self.show_about,)
        }
        for action_name, args in func_map.items():
            func, func_args = args[0], args[1:]
            self._connect_func(action_name, func, *func_args)

    def show_about(self):
        basic_funcs.info('О программе',
                         f'Версия программы {self.version}. Версия скрипта обновления {self.script_version}.')

    def show_help(self):
        if self.help_shown:
            return
        window = HelpApp('resources/docs', self)
        self.help_shown = True
        if window.exec_():
            pass
        self.help_shown = False

    def show_tree(self, type_, show=True):
        """
        Отображение дерева
        :param type_: тип дерева
        :param show: показывать ли (не используется)
        :return:
        """
        dock_widgets = {
            self.ADMIN_USERS_TREE: self.admin_users_tree_dock_widget,
            self.ADMIN_ROLES_TREE: self.admin_roles_tree_dock_widget,
            self.WORK_DATA_TREE: self.work_data_tree_dock_widget,
            self.PROJECT_TREE: self.project_tree_dock_widget,
            self.SYNONYM_DICTIONARY_TREE: self.synonym_dictionary_tree_dock_widget,
            self.EIZM_DICTIONARY_TREE: self.eizm_dictionary_tree_dock_widget
        }
        dock_widget = dock_widgets.get(type_)
        if dock_widget:
            dock_widget.setHidden(not getattr(self, type_).isChecked())

    def init_modes(self):
        """
        Инициализация доступных в программе режимов
        :return:
        """
        logger.info("Инициализация режимов.")
        self.available_modes = [mode for mode in sp.get_modes()]
        self.plugins_dict = {
            setattr(self, mode.rejim_name_base,
                    self.plugins_dict.get(mode.rejim_name_base, None)(self)) for mode in
            self.available_modes}

    def closeEvent(self, event: QCloseEvent):
        """Выполнение действий до закрытия главного окна."""
        self.save_windows_state()
        sp.session.close()
        logger.info("Выход из программы.")
        super().closeEvent(event)

    def handle_result(self, result):
        self.result = result

    def display_result(self, result):
        if isinstance(result, str):
            self.label.setText(f"Error: {result}")
        else:
            self.label.setText(f"Result: {result}")

    @Slot()
    def on_worker_started(self):
        if not self._current_progress_message:
            self._current_progress_message = 'Загрузка...'
        self.progress_bar.setRange(0, 0)
        self.set_progress_bar_status(self._current_progress_message)
        self.progress_bar.setVisible(True)

    @Slot(str)
    def set_progress_bar_status(self, message):
        self._current_progress_message = message
        self.progress_bar.setFormat(message + '..')

    @Slot()
    def on_worker_finished(self):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100)

    def run_with_progress(self, func, progress_text="Загрузка..."):
        self.result = None
        self._current_progress_message = progress_text or self._current_progress_message
        worker = Worker(func)
        worker.setParent(self)
        worker.result_ready.connect(self.handle_result)
        worker.started.connect(self.on_worker_started)
        worker.finished.connect(self.on_worker_finished)
        worker.finished.connect(worker.deleteLater)

        # self.status_label.setText(progress_text)
        event_loop = QEventLoop()
        worker.finished.connect(event_loop.quit)
        worker.start()
        event_loop.exec_()

        # self.status_label.clear()
        self.progress_bar.setVisible(False)

        return self.result

    @staticmethod
    def _coerce_tree_states(raw_value):
        def normalize_dict(mapping):
            normalized = {}
            for key, value in mapping.items():
                if isinstance(value, dict):
                    normalized[str(key)] = value
            return normalized

        if isinstance(raw_value, dict):
            return normalize_dict(raw_value)

        if isinstance(raw_value, list):
            result = {}
            for entry in raw_value:
                if not isinstance(entry, dict):
                    continue
                plugin = entry.get('plugin') or entry.get('name') or entry.get('key')
                state = entry.get('state') or entry.get('value')
                if plugin and isinstance(state, dict):
                    result[str(plugin)] = state
            return result

        if isinstance(raw_value, str):
            for parser in (json.loads, ast.literal_eval):
                try:
                    parsed = parser(raw_value)
                except Exception:
                    continue
                return MainWindow._coerce_tree_states(parsed)
            return {}

        return {}

    def _restore_tree_view_state(self, plugin_name, tree_widget):
        if not plugin_name or not isinstance(tree_widget, TreeView):
            return
        state = self._tree_states_to_restore.get(str(plugin_name))
        if not isinstance(state, dict):
            return
        try:
            accepted = tree_widget.schedule_state_restore(state)
        except Exception as exc:
            logger.warning('Не удалось восстановить состояние дерева "%s": %s', plugin_name, exc)
            return
        if accepted:
            self._tree_states_to_restore.pop(str(plugin_name), None)

    def _apply_pending_window_state(self):
        state_bytes = self._pending_window_state_bytes
        central_bytes = self._pending_central_window_state_bytes

        if state_bytes is None and central_bytes is None:
            return

        try:
            if state_bytes is not None:
                if hasattr(state_bytes, 'isEmpty') and state_bytes.isEmpty():
                    state_bytes = None
                else:
                    restored_main = self.restoreState(state_bytes)
                    logger.debug('Результат восстановления состояния окна: %s', restored_main)
        except Exception as exc:
            logger.warning('Не удалось восстановить состояние окна: %s', exc)

        try:
            if central_bytes is not None:
                if hasattr(central_bytes, 'isEmpty') and central_bytes.isEmpty():
                    central_bytes = None
                else:
                    restored_central = self.ui.centralWidget.restoreState(central_bytes)
                    logger.debug('Результат восстановления центрального окна: %s', restored_central)
        except Exception as exc:
            logger.warning('Не удалось восстановить состояние центрального окна: %s', exc)
        finally:
            self._pending_window_state_bytes = None
            self._pending_central_window_state_bytes = None

    def save_windows_state(self):
        remember_session = self._coerce_bool(self.user_settings.get('remember_last_session', True), default=True)
        restore_layout = self._coerce_bool(self.user_settings.get('restore_window_layout', True), default=True)

        if remember_session:
            active_plugins = []
            active_project_id = None
            for dw in self.findChildren(QDockWidget):
                if not dw.isHidden() and hasattr(dw, 'plugin_name'):
                    plugin_name = dw.plugin_name
                    active_plugins.append(plugin_name)
                    if plugin_name == 'project' and hasattr(dw, 'project_id') and dw.project_id is not None:
                        active_project_id = str(dw.project_id)

            if active_project_id is None and hasattr(self, 'project_tree_dock_widget'):
                project_dock = self.project_tree_dock_widget
                if hasattr(project_dock, 'project_id') and project_dock.project_id is not None:
                    active_project_id = str(project_dock.project_id)

            if active_plugins:
                ordered_unique_plugins = list(dict.fromkeys(active_plugins))
            else:
                ordered_unique_plugins = []

            self.user_settings.set('active_plugins', ordered_unique_plugins)

            if active_project_id is not None:
                self.user_settings.set('active_project', active_project_id)
            else:
                self.user_settings.remove('active_project')
        else:
            self.user_settings.remove('active_plugins')
            self.user_settings.remove('active_project')

        if restore_layout:
            try:
                geometry_bytes = self.saveGeometry()
                logger.debug('Сохраняем геометрию окна: длина raw=%s', geometry_bytes.size())
                self.user_settings.set('main_window_geometry', geometry_bytes)
            except Exception as exc:
                logger.warning('Не удалось сохранить геометрию окна: %s', exc)

            try:
                state_bytes = self.saveState()
                logger.debug('Сохраняем состояние окна: длина raw=%s', state_bytes.size())
                self.user_settings.set('main_window_state', state_bytes)
            except Exception as exc:
                logger.warning('Не удалось сохранить состояние окна: %s', exc)

            try:
                central_state_bytes = self.ui.centralWidget.saveState()
                logger.debug('Сохраняем состояние центрального окна: длина raw=%s', central_state_bytes.size())
                self.user_settings.set('central_window_state', central_state_bytes)
            except Exception as exc:
                logger.warning('Не удалось сохранить состояние центрального окна: %s', exc)
        else:
            self.user_settings.remove('main_window_geometry')
            self.user_settings.remove('main_window_state')
            self.user_settings.remove('central_window_state')

        if remember_session:
            existing_states = self._coerce_tree_states(self.user_settings.get('tree_states', {}))
            tree_states = dict(existing_states)

            for dock_name, dock_data in self.dock_widgets.items():
                dock_widget = getattr(self, f'{dock_name}_tree_dock_widget', None)
                if dock_widget is None:
                    continue
                tree_widget = dock_widget.widget()
                if not isinstance(tree_widget, TreeView):
                    continue
                if tree_widget.model() is None:
                    continue
                plugin_key = getattr(dock_widget, 'plugin_name', dock_name)
                if not plugin_key:
                    continue
                try:
                    state = tree_widget.capture_persistent_state()
                except Exception:
                    logger.exception('Не удалось сохранить состояние дерева для режима "%s".', plugin_key)
                    continue
                tree_states[str(plugin_key)] = state

            if tree_states:
                try:
                    serialized = json.dumps(tree_states, ensure_ascii=False)
                    self.user_settings.set('tree_states', serialized)
                except (TypeError, ValueError) as exc:
                    logger.warning('Не удалось сериализовать состояние деревьев: %s', exc)
            else:
                self.user_settings.remove('tree_states')
        else:
            self.user_settings.remove('tree_states')

    def restore_windows_state(self):
        restore_layout = self._coerce_bool(self.user_settings.get('restore_window_layout', True), default=True)
        remember_session = self._coerce_bool(self.user_settings.get('remember_last_session', True), default=True)

        if restore_layout:
            geometry_bytes = self.user_settings.get_bytes('main_window_geometry')
            if not geometry_bytes.isEmpty():
                try:
                    if not geometry_bytes.isEmpty():
                        restored = self.restoreGeometry(geometry_bytes)
                        logger.debug('Результат восстановления геометрии окна: %s', restored)
                    else:
                        logger.debug('Геометрия окна пуста, пропускаем восстановление')
                except Exception as exc:
                    logger.warning('Не удалось восстановить геометрию окна: %s', exc)

            window_state = self.user_settings.get_bytes('main_window_state')
            if not window_state.isEmpty():
                self._pending_window_state_bytes = window_state
            else:
                self._pending_window_state_bytes = None

            central_state = self.user_settings.get_bytes('central_window_state')
            if not central_state.isEmpty():
                self._pending_central_window_state_bytes = central_state
            else:
                self._pending_central_window_state_bytes = None
        else:
            self._pending_window_state_bytes = None
            self._pending_central_window_state_bytes = None

        if remember_session:
            self._tree_states_to_restore = self._coerce_tree_states(self.user_settings.get('tree_states', {}))
        else:
            self._tree_states_to_restore = {}

        restore_last_project = self._coerce_bool(self.user_settings.get('restore_last_project', True), default=True)
        if remember_session and restore_last_project and hasattr(self, 'project') and self.project is not None:
            active_project_setting = self.user_settings.get('active_project')
            if active_project_setting:
                self.project.autoopen_project_id = str(active_project_setting)

        active_plugins = []
        if remember_session:
            stored_plugins = self.user_settings.get('active_plugins')
            if isinstance(stored_plugins, str):
                try:
                    stored_plugins = ast.literal_eval(stored_plugins)
                except (ValueError, SyntaxError):
                    stored_plugins = [stored_plugins]

            if isinstance(stored_plugins, (list, tuple)):
                active_plugins = list(stored_plugins)

        for plugin in active_plugins:
            if hasattr(self, plugin) and hasattr(self, f'{plugin}_tree_dock_widget'):
                self.activate_tree(getattr(self, plugin), getattr(self, plugin + '_tree_dock_widget'),
                                   getattr(self, plugin.upper() + '_TREE'))

        self._apply_pending_window_state()

    # slots:
    def import_files(self, type_):
        pass

    def change_role(self, role):
        """
        Изменение роли. Меняет набор пунктов главного меню.
        :param role: на какую роль меняем
        :return:
        """
        current_role = None
        for role_ in self.roles:
            if role_.name == role:
                current_role = role_
                break
        if not current_role:
            logger.error('Не удалось сменить роль')
            return

        if self.current_role.rolename == current_role.rolename:
            return

        success = sp.set_sesion_role(current_role.id_role)
        if success:
            clear_menu_cache('active role changed')
            self.menuBar().clear()
            self.init_menu()
            self.connect_triggered_funcs()
            self.current_role = current_role

            self.clear_interface()

    def clear_interface(self):
        for widget in self.findChildren(QDockWidget):
            widget.hide()

    def activate_tree(self, obj, dock_widget, tree_name):
        """
        Активация дерева
        :param obj: класс режима (*Plugin)
        :param dock_widget: док-виджет с деревом, используемый для этого режима
        :param tree_name: название дерева
        :return:
        """
        if obj is None:
            return False
        if dock_widget.widget().model() is None or getattr(self, tree_name).isChecked():
            if obj.activate():
                dock_widget.init_menu()
                tree_widget = obj.tree_view()
                if tree_widget is not None:
                    dock_widget.setWidget(tree_widget)
                    tree_widget.init_dock_widget(dock_widget)
                    self._restore_tree_view_state(getattr(dock_widget, 'plugin_name', tree_name), tree_widget)
                if obj.dock_widget_name:
                    dock_widget.set_title_label(obj.dock_widget_name)
                if hasattr(self, tree_name):
                    getattr(self, tree_name).setChecked(True)
                    self.show_tree(tree_name, True)
        else:
            dock_widget.init_menu()
            if hasattr(self, tree_name):
                getattr(self, tree_name).setChecked(True)
                self.show_tree(tree_name, True)

    def show_settings(self):
        settings = SettingsDialog(self)
        settings.settings_applied.connect(self.apply_runtime_settings)
        settings.exec_()

    def apply_runtime_settings(self, values: Optional[Dict[str, Any]] = None):
        """Применяет настройки интерфейса и поведения без перезапуска."""

        values = values or {}

        def setting(key: str, default):
            if key in values:
                return values[key]
            return self.user_settings.get(key, default)

        timeout = self._coerce_int(setting('application_close_timeout', 30), default=30, minimum=1)
        config.config.app.enable_timer(timeout)

        status_bar_visible = self._coerce_bool(setting('show_status_bar', True), default=True)
        self.statusBar().setVisible(status_bar_visible)

        apply_application_font(config.config.app, {
            'use_custom_font': setting('use_custom_font', False),
            'font_name': setting('font_name', None),
            'font_size': setting('font_size', None),
        })

        notifications_enabled = self._coerce_bool(
            setting('enable_notifications', True),
            default=True,
        )
        notifications_timeout = self._coerce_int(
            setting('notifications_timeout', 10),
            default=10,
            minimum=1,
        )
        self._apply_notification_settings(notifications_enabled, notifications_timeout)

    def _apply_notification_settings(self, enabled: bool, timeout_seconds: int) -> None:
        self.notifications_enabled = enabled
        self.notifications_timeout = max(1, int(timeout_seconds)) * 1000
        if not enabled and self.notification is not None:
            self.notification.hide()

    @staticmethod
    def _coerce_bool(value: Any, default: bool = False) -> bool:
        if isinstance(value, bool):
            return value
        if value is None:
            return default
        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {'true', '1', 'yes', 'y', 'on'}:
                return True
            if normalized in {'false', '0', 'no', 'n', 'off'}:
                return False
            return default
        if isinstance(value, (int, float)):
            return value != 0
        return default

    @staticmethod
    def _coerce_int(value: Any, default: int = 0, minimum: Optional[int] = None) -> int:
        try:
            coerced = int(value)
        except (TypeError, ValueError):
            coerced = int(default)
        if minimum is not None and coerced < minimum:
            return minimum
        return coerced

    def _close(self):
        logger.info("Выход из программы.")
        self.close()
