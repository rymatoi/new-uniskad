import ast

from PySide2 import QtWidgets
from PySide2.QtCore import QEventLoop, Slot, QByteArray, qCompress, qUncompress
from PySide2.QtGui import QIcon, QCloseEvent, Qt, QKeySequence
from PySide2.QtWidgets import QMenu, QToolBar, QHBoxLayout, QToolButton, QWidget, QDialog, QShortcut, QDockWidget, \
    QAction, QProgressBar, QLabel
from app import app_logger, _menu, basic_funcs
from app.cache import DataCache
from app.history_manager.history_manager import EventStack
from app.notifications import StackedNotifications
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

    _MAX_DB_STRING_LENGTH = 255

    def __init__(self):

        self.version = '250425'
        self.script_version = '2025'

        super(MainWindow, self).__init__()

        self.user_settings = UserSettings()

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

        self.toolbar_layout = QHBoxLayout(self)

        self.init_modes()
        self.init_menu()
        self.init_toolbar()
        # self.init_role_buttons_toolbar()
        self.init_dock_widgets()

        self.connect_triggered_funcs()

        self.notification = None
        self.notifications_timeout = 10000
        self.init_notifications()

        self.event_stack = EventStack()
        shortcut_undo = QShortcut(QKeySequence('Ctrl+Z'), self)
        shortcut_undo.activated.connect(self.event_stack.undo)

        shortcut_redo = QShortcut(QKeySequence('Ctrl+Shift+Z'), self)
        shortcut_redo.activated.connect(self.event_stack.redo)

        self.restore_windows_state()

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

    def init_toolbar(self):
        toolbar = QToolBar(self)
        toolbar.setWindowTitle('Панель инструментов')

        # self._move_up = QAction(QIcon(":up.png"), 'Переместить вверх', self, )
        # self._move_down = QAction(QIcon(":down.png"), 'Переместить вниз', self, )
        #
        # toolbar.addAction(self._move_up)
        # toolbar.addAction(self._move_down)

        self.role_button = QToolButton(self)
        self.role_button.setPopupMode(QToolButton.MenuButtonPopup)
        self.role_button.setMenu(self._init_role_button_menu())

        default_user_role = self._get_default_user_role()
        self.role_button.setText(default_user_role.rolename)

        self.current_role = default_user_role

        self.toolbar_layout.addStretch()
        self.toolbar_layout.addWidget(self.role_button)

        widget = QWidget()
        widget.setLayout(self.toolbar_layout)
        toolbar.addWidget(widget)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

    def init_role_buttons_toolbar(self):
        """
        Создает и инициализирует панель инструментов
        :return:
        """
        toolbar = QToolBar(self)
        toolbar.setWindowTitle('Панель инструментов')

        layout = QHBoxLayout(self)
        layout.addStretch()

        self.role_button = QToolButton(self)
        self.role_button.setPopupMode(QToolButton.MenuButtonPopup)
        self.role_button.setMenu(self._init_role_button_menu())

        default_user_role = self._get_default_user_role()
        self.role_button.setText(default_user_role.rolename)
        layout.addWidget(self.role_button)

        widget = QWidget()
        widget.setLayout(layout)
        toolbar.addWidget(widget)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

    def _init_role_button_menu(self):
        """
        Инициализирует кнопку переключения ролей (будет переделано, ибо обращается к пунктам меню, а нужно к списку ролей
        # TODO
        :return:
        """
        self.roles = sp.get_user_role_list_()
        for role in self.roles:
            role.children = None
            role.name = f'_role_{role.id}'
            role.is_root = True
            role.translation = role.rolename
            role.is_menu = None
            role.is_checkable = False
            role.init_order = 0

        # role_button_menu = sp.get_user_menu_('any', 'role_button')

        # user_rolenames = [role.rolename for role in self.roles]
        # role_button_menu = [role for role in role_button_menu if role.translation in user_rolenames]
        menu = QMenu(self)
        _menu.init_menu(self.roles, self, menu)
        return menu

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
        menu_list = sp.get_user_menu_('any', 'main_menu')
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
            '_role_200': (self.change_role, self.ADMIN_ROLE),
            '_role_100': (self.change_role, self.USER_ROLE),
            '_role_1000': (self.change_role, self.DEVELOPER_ROLE),
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

    def save_windows_state(self):
        active_plugins = []
        for dw in self.findChildren(QDockWidget):
            if not dw.isHidden() and hasattr(dw, 'plugin_name'):
                active_plugins.append(dw.plugin_name)
                if dw.plugin_name == 'project':
                    sp.set_user_default_value(None, None, None, 'active_project', str(dw.project_id))
        sp.set_user_default_value(None, None, None, 'active_plugins', str(active_plugins))

        try:
            geometry = self._encode_window_data(self.saveGeometry())
            if geometry is not None:
                sp.set_user_default_value(None, None, None, 'main_window_geometry', geometry)
            else:
                logger.warning('Не удалось сохранить геометрию окна: строка превышает %s символов',
                               self._MAX_DB_STRING_LENGTH)
        except Exception as exc:
            logger.warning('Не удалось сохранить геометрию окна: %s', exc)

        try:
            state = self._encode_window_data(self.saveState())
            if state is not None:
                sp.set_user_default_value(None, None, None, 'main_window_state', state)
            else:
                logger.warning('Не удалось сохранить состояние окна: строка превышает %s символов',
                               self._MAX_DB_STRING_LENGTH)
        except Exception as exc:
            logger.warning('Не удалось сохранить состояние окна: %s', exc)

    def restore_windows_state(self):
        geometry = self.user_settings.get('main_window_geometry')
        if geometry:
            try:
                geometry_bytes = self._decode_window_data(geometry)
                if not geometry_bytes.isEmpty():
                    self.restoreGeometry(geometry_bytes)
            except Exception as exc:
                logger.warning('Не удалось восстановить геометрию окна: %s', exc)

        window_state = self.user_settings.get('main_window_state')
        if window_state:
            try:
                state_bytes = self._decode_window_data(window_state)
                if not state_bytes.isEmpty():
                    self.restoreState(state_bytes)
            except Exception as exc:
                logger.warning('Не удалось восстановить состояние окна: %s', exc)

        active_plugins = self.user_settings.get('active_plugins')
        if active_plugins:
            active_plugins = ast.literal_eval(active_plugins)
            for plugin in active_plugins:
                if plugin == 'project':
                    active_project = self.user_settings.get('active_project')
                    if active_project:
                        self.project.autoopen_project_id = active_project
                self.activate_tree(getattr(self, plugin), getattr(self, plugin + '_tree_dock_widget'),
                                   getattr(self, plugin.upper() + '_TREE'))

    @classmethod
    def _encode_window_data(cls, data: QByteArray):
        if data is None or data.isNull() or data.isEmpty():
            return ''

        try:
            compressed = qCompress(data, 9)
            encoded_bytes = compressed.toBase64()
            encoded = 'z:' + bytes(encoded_bytes).decode('ascii')
        except Exception as exc:
            logger.warning('Ошибка при кодировании состояния окна: %s', exc)
            encoded = None

        if encoded and len(encoded) <= cls._MAX_DB_STRING_LENGTH:
            return encoded

        try:
            fallback_bytes = data.toBase64()
            fallback = bytes(fallback_bytes).decode('ascii')
        except Exception:
            fallback = None

        if fallback and len(fallback) <= cls._MAX_DB_STRING_LENGTH:
            return fallback

        return None

    @staticmethod
    def _decode_window_data(encoded: str) -> QByteArray:
        if not encoded:
            return QByteArray()

        if encoded.startswith('z:'):
            payload = encoded[2:]
            try:
                compressed = QByteArray.fromBase64(payload.encode('ascii'))
                decompressed = qUncompress(compressed)
                if decompressed.isNull():
                    return QByteArray()
                result = QByteArray()
                result.append(decompressed)
                return result
            except Exception as exc:
                logger.warning('Ошибка при декодировании сжатого состояния окна: %s', exc)

        try:
            return QByteArray.fromBase64(encoded.encode('ascii'))
        except Exception:
            logger.warning('Ошибка при декодировании состояния окна')
            return QByteArray()

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
            self.menuBar().clear()
            self.init_menu()
            self.connect_triggered_funcs()
            self.role_button.setText(getattr(self, role).text())
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
                dock_widget.setWidget(obj.tree_view())
                obj.tree_view().init_dock_widget(dock_widget)
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
        if settings.exec_() == QDialog.Accepted:
            print('done')

    def _close(self):
        logger.info("Выход из программы.")
        self.close()
