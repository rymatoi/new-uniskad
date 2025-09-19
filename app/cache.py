from db import sp


class DataCache:
    def __init__(self):
        self.sprav_names = None
        self.sprav_eizm = None
        self.project_types = None
        self.project_types_reversed = None

    def get_sprav_names(self):
        if self.sprav_names is None:
            self.sprav_names = sp.get_sprav_names_all()
            self.sprav_names = sorted(self.sprav_names, key=lambda x: x.param_name)
        return self.sprav_names

    def get_sprav_eizm(self):
        if self.sprav_eizm is None:
            self.sprav_eizm = sp.get_sprav_eizm_all()
        return self.sprav_eizm

    def get_project_types(self, reversed=False):
        if self.project_types is None:
            _ = sp.get_projecttypes_list()
            self.project_types_reversed = {}
            self.project_types = {}
            for project_type in _:
                self.project_types[project_type.project_type] = project_type.id_project_type
                self.project_types_reversed[project_type.id_project_type] = project_type.project_type
        return self.project_types if not reversed else self.project_types_reversed
