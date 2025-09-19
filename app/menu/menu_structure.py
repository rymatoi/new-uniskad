class Menu:
    _children: []
    name: str
    translation: str
    mode: str
    location: str

    def __init__(self, name, translation, mode, location, children):
        self.name = name
        self.translation = translation
        self.mode = mode
        self.location = location
        self._children = children

        self.is_menu = True
        self.id_up = None
        self.is_root = None
        self.init_order = None

    @property
    def children(self):
        return [child.name for child in self.children]


class Action:
    name: str
    translation: str
    mode: str
    location: str

    def __init__(self, name, translation, mode, location):
        self.name = name
        self.translation = translation
        self.mode = mode
        self.location = location

        self.is_menu = False
        self.id_up = None
        self.is_root = None
        self.init_order = None
        self.children = None


menu_structure = [
    Menu('_file', 'Файл', 'any', 'any', children=[
        Action('_open', 'Открыть', 'any', 'any')
    ])
]
