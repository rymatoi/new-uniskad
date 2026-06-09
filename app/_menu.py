from operator import attrgetter

from PySide2.QtWidgets import QAction, QMenu


class CustomMenu:  # узлы дерева меню в программе

    def __init__(self, children, is_root=False, is_menu=False):
        self.children = children  # список дочерних элементов в виде вектора имен
        self.is_root = is_root  # является ли элемент корневым в дереве
        self.is_menu = is_menu  # является ли элемент корневым в дереве


def init_menu(menu_list, parent, menu_bar, _exclude=None):
    if _exclude:
        menu_list = [el for el in menu_list if el.name not in _exclude]
    actions = [action for action in menu_list if not action.is_menu]
    action_titles = [action.name for action in actions]
    for action in actions:
        if hasattr(parent, action.name):
            existing_action = getattr(parent, action.name)
            existing_action.blockSignals(True)
            existing_action.triggered.connect(lambda: None)
            existing_action.triggered.disconnect()
            existing_action.blockSignals(False)
            if action.name not in parent.available_actions:
                parent.available_actions.append(action.name)
            continue
        setattr(parent, action.name, QAction(action.translation, parent))
        getattr(parent, action.name).setCheckable(
            action.is_checkable if action.is_checkable is (True or False) else False)
        if action.name not in parent.available_actions:
            parent.available_actions.append(action.name)

    root_menus = sorted([menu for menu in menu_list if menu.is_root], key=attrgetter('init_order'))
    menus = root_menus + [menu for menu in menu_list if menu.is_menu and not menu.is_root]
    menu_structure = {}

    for menu in menus:
        if not hasattr(parent, menu.name):
            if menu.is_menu:
                setattr(parent, menu.name, QMenu(menu.translation, parent))
            else:
                setattr(parent, menu.name, QAction(menu.translation, parent))
        else:
            if menu.is_menu:
                getattr(parent, menu.name).clear()

        menu_structure[menu.name] = CustomMenu(children=menu.children,
                                               is_root=menu.is_root,
                                               is_menu=menu.is_menu)

    for menu in menu_structure:  # проходимся по узлам меню
        if menu_structure[menu].is_root:  # root - этот элемент корневой
            if menu_structure[menu].is_menu:
                menu_bar.addMenu(getattr(parent, menu))
            else:
                menu_bar.addAction(getattr(parent, menu))  # если корневой, то добавляем на менюбар
        if not menu_structure[menu].is_menu:
            continue
        for action in menu_structure[menu].children:  # проходимся по дочерним элементам текущего узла
            if action.strip() == '|':
                getattr(parent, menu).addSeparator()
                continue
            if action in menu_structure.keys():  # если текущий элемент находится в списке узлов, то добавляем как пункт меню
                getattr(parent, menu).addMenu(getattr(parent, action))
            else:  # иначе как ветка (action)
                if action in action_titles:
                    getattr(parent, menu).addAction(getattr(parent, action))
