import datetime
import json

from app import app_logger

logger = app_logger.get_logger(__name__)


class QueryField:
    def __init__(self, type_, alias=None, default=None):
        self.type_ = type_
        self.alias = alias
        self.default = default


class QueryObject:
    """Объект результата выполнения хранимой процедуры."""

    _query_field_metadata = None
    _row_constructor_cache = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        # Each schema class gets its own cache.  Building it lazily also keeps
        # inherited QueryField definitions in the final metadata.
        cls._query_field_metadata = None
        cls._row_constructor_cache = None

    @classmethod
    def _get_query_field_metadata(cls):
        """Return cached QueryField definitions and their defaults/aliases."""
        metadata = cls._query_field_metadata
        if metadata is None:
            fields = {}
            for base in reversed(cls.__mro__):
                for name, value in vars(base).items():
                    if isinstance(value, QueryField):
                        fields[name] = value
            metadata = (fields, tuple(fields.items()))
            cls._query_field_metadata = metadata
        return metadata

    @staticmethod
    def _query_field_value(field, value):
        # Preserve the historical behavior: a truthy default replaces a
        # false-y database value, while false-y defaults do not.
        return field.default if not value and field.default else value

    @classmethod
    def _get_row_constructor(cls, columns):
        """Return a cached constructor specialized for a result column set."""
        cache = cls._row_constructor_cache
        if cache is None:
            cache = {}
            cls._row_constructor_cache = cache
        column_key = tuple(columns)
        constructor = cache.get(column_key)
        if constructor is not None:
            return constructor

        fields, field_items = cls._get_query_field_metadata()
        actions = []
        consumed_fields = set()
        aliases = {}
        for name in column_key:
            field = fields.get(name)
            alias = field.alias if field is not None else None
            if alias:
                aliases[alias] = name
                consumed_fields.add(alias)
                actions.append((name, alias, field))
            else:
                actions.append((name, None, None))
            if field is not None:
                consumed_fields.add(name)
        defaults = tuple(
            (name, field.default if field.default is not None else None)
            for name, field in field_items
            if name not in consumed_fields
        )

        def construct(row):
            obj = cls.__new__(cls)
            obj._changed_variables = set()
            obj._alias_dict = aliases.copy()
            for action, value in zip(actions, row):
                name, alias, field = action
                if alias:
                    setattr(obj, alias, cls._query_field_value(field, value))
                setattr(obj, name, value)
            for name, default in defaults:
                setattr(obj, name, default)
            return obj

        cache[column_key] = construct
        return construct

    @classmethod
    def _from_row(cls, row, columns):
        """Construct a schema object directly from an asyncpg row."""
        return cls._get_row_constructor(columns)(row)

    def __init__(self, args):
        self._changed_variables = set()
        self._alias_dict = {}
        fields, field_items = self._get_query_field_metadata()
        consumed_fields = set()

        for name, value in args.items():
            field = fields.get(name)
            if field is not None:
                alias = field.alias
                if alias:
                    self._alias_dict[alias] = name
                    consumed_fields.add(alias)
                    setattr(self, alias, self._query_field_value(field, value))
                consumed_fields.add(name)
            setattr(self, name, value)

        for name, field in field_items:
            if name not in consumed_fields:
                setattr(self, name, field.default if field.default is not None else None)

    def set_val(self, prop_name, prop_value):
        if prop_name in self._alias_dict:
            setattr(self, self._alias_dict[prop_name], prop_value)
        if hasattr(self, prop_name):
            setattr(self, prop_name, prop_value)

    @property
    def _attrs(self):
        props = tuple(prop for prop in dir(self) if
                      not prop.startswith('__') and not prop.endswith('__') and prop != '_attrs')
        return {prop: getattr(self, prop) for prop in props if
                not prop.startswith('__') and not prop.endswith('__')}

    def attrs_update(self, new_attrs):
        for attr, value in new_attrs.items():
            setattr(self, attr, value)
        return self

    def table_fit(self, column_names):
        """Возвращает tuple-представление объекта с нужными полями в нужном порядке"""
        res = []
        for column in column_names:
            if hasattr(self, column):
                res.append(getattr(self, column))
            else:
                res.append(None)
        return tuple(res)


class QueryTreeItemObject(QueryObject):
    """
    Элемент, который будет использоваться как элемент дерева.
    Обязательные поля: id, id_up, type_.
    Эти поля должны обязательно быть проинициализированы (либо значениями из поцедуры,
    либо через объект QueryField.)
    Что делать, если нужные поля приходят под другими именами? Инициализиовать поле как объект
    QueryField, где нужно определить новое имя в alias.
    """
    id = QueryField(type_=int)
    id_up = QueryField(type_=int)
    type_ = QueryField(type_=str, default='root')
    prop_name = QueryField(type_=str, default='name')
    prop_value = QueryField(type_=str, default=None)


class QueryListItemObject(QueryObject):
    """
    Элемент, который будет использоваться как элемент списка.
    Обязательные поля: id, type_.
    В программе везде используется только модель дерева, поэтому здесь id_up по умолчанию
    всегда инициализируется как 0, это поле можно проигнорировать.
    Поле type_ нужно определять, если хотите, чтобы элементы этого типа не выглядели
    как простые заглушки без иконок и кастомных пунктов меню.
    """
    id = QueryField(type_=int, default=None)
    id_up = QueryField(type_=int, default=0)
    type_ = QueryField(type_=str, default='root')
    prop_name = QueryField(type_=str, default='name')
    prop_value = QueryField(type_=str, default=None)


class Menu(QueryTreeItemObject):
    id: int
    id_up: int
    type_ = QueryField(type_=str, default='action')
    name: str
    translation: str
    children: list
    is_root: bool
    is_menu: bool
    init_order: int
    is_checkable: bool
    mode: str
    location: str


class Mode(QueryTreeItemObject):
    id_prog: int
    id_up = QueryField(type_=int, default=0)
    type_ = QueryField(type_=str, default='mode')
    id_rejim: int
    rejim_name_base: str
    rejim_name_rus: str


class User(QueryListItemObject):
    id: int
    type_ = QueryField(type_=str, default='user')

    login: str
    fam: str
    name: str
    default_id_role: int
    active: bool
    deleted: bool
    password_fail_count: int
    default_password_fail_count: int
    last_login: datetime.datetime
    last_logout: datetime.datetime


class Role(QueryTreeItemObject):
    id_role = QueryField(type_=int, alias='id')
    id_role_up = QueryField(type_=int, alias='id_up')
    type_ = QueryField(type_=str, default='role')

    id_prog: int
    rolename: str
    descr: str
    deleted: bool


class UserRole(QueryObject):
    fam: str
    name: str
    default_id_role: int
    id_role: int
    rolename: str


class Product(QueryTreeItemObject):
    record_id: int
    id_prod = QueryField(type_=int, alias='id')
    id_up_prod = QueryField(type_=int, alias='id_up')
    type_ = QueryField(type_=int, default='root')

    id_ptype: int
    prod_prop = QueryField(type_=str, alias='prop_name')
    prod_prop_value = QueryField(type_=str, alias='prop_value')
    creation_date: datetime.datetime
    npp: int
    deleted: bool


class ProductType(QueryObject):
    id_prod_type: int
    prod_type: str
    prod_type_name: str


class Location(QueryTreeItemObject):
    type_ = QueryField(type_=str, default='location')
    name = QueryField(type_=str, alias='id')
    translation: str


class DataFile(QueryListItemObject):
    id_datafile = QueryField(type_=int, alias='id')
    type_ = QueryField(type_=str, default='test')
    id_prod: int
    prod_title: str
    prod_type: str
    prod_type_name: str
    datafile_type: str
    datafile_type_name: str
    datafile_short_name: str
    datafile_full_name: str
    datafile_comment: str
    full_name: str
    short_name: str


class DataFileType(QueryObject):
    id_datafile_type: int
    datafile_type: str
    datafile_type_name: str
    datafile_type_descr: str


class BinaryFile(QueryObject):
    id_datafile: int
    id_prod: int
    id_datafile_type: str
    short_name: str
    full_name: str
    comment: str
    datafile_creator: int
    creation_date: datetime.datetime
    id_datafile_bin: int
    bin_file_name: str
    bin_file_ext: str
    bin_npp_ver: int
    bin_user_ver: str
    bin_ver_comment: str
    bin_creation_date: datetime.datetime
    bindata: bytes


class ImportFileData(QueryObject):
    id_record: int
    is_secret: bool
    id_excel_file: int
    file_version: int
    excel_param_name: str
    param_prop_name = QueryField(type_=str, alias='prop_name')
    date_time_izm: datetime.datetime
    zamer_n: int
    rejim_zamer: str
    prop_name: str
    prop_value: str
    deleted: bool
    id_name: int
    sprav_name: str
    accuracy: int
    id_eizm: int
    eizm_short: str
    eizm_full: str


class SpravName(QueryTreeItemObject):
    id_name = QueryField(type_=int, alias='id')
    is_secret: bool
    param_name = QueryField(type_=str, alias='prop_value')
    param_id_eizm = QueryField(type_=int, default=0)
    flag_synonim: bool
    flag_permanent: bool
    param_descr = QueryField(type_=str, default='')
    id_permanent_name = QueryField(type_=int, alias='id_up')
    accuracy = QueryField(type_=int, default=2)
    type_ = QueryField(type_=str, default='standard')
    eizm_short = QueryField(type_=str, default='')
    eizm_full = QueryField(type_=str, default='')
    eizm_descr = QueryField(type_=str, default='')


class SpravEizm(QueryTreeItemObject):
    id_eizm = QueryField(type_=int, alias='id')
    id_up = QueryField(type_=int, default=None)
    type_ = QueryField(type_=str, default='eizm')
    eizm_short: str
    eizm_full: str
    eizm_descr: str


class Project(QueryTreeItemObject):
    id_record: int
    project_id = QueryField(type_=int, alias='id')
    project_id_up = QueryField(type_=int, alias='id_up')
    project_type: int
    project_prop = QueryField(type_=str, alias='prop_name')
    project_prop_value = QueryField(type_=str, alias='prop_value')
    project_author: int
    project_owner: int
    creation_date: datetime.datetime
    npp: int
    sprav_name: str
    deleted: bool


class ProjectType(QueryObject):
    id_project_type: int
    project_type: str
    project_type_name: str


class ProjectData(QueryObject):
    id_record: int
    project_id: int
    id_excel_file: int
    file_version: int
    excel_param_name = QueryField(type_=str, alias='sprav_name')
    param_prop_name = QueryField(type_=str, alias='prop_name')
    date_time_izm: datetime.datetime
    zamer_n: int
    rejim_zamer: str
    prop_value: str
    deleted: bool
    npp = QueryField(type_=int, default=0)
    id_name: int
    sprav_name = QueryField(type_=str, default=None)
    id_eizm: int
    eizm_short: str
    eizm_full: str


class CurveData(QueryObject):
    x_val: str
    y_val: str
    project_id: int
    excel_param_name: int


class XCurveData(QueryObject):
    y_val: str
    formula: str
    broken: str
    date_time_izm: datetime.datetime


class ImportFileState(QueryObject):
    id_record: int
    id_excel_file: int
    file_version: int
    file_state: int
    deleted: bool


class SettingsItem(QueryTreeItemObject):
    type_ = QueryField(type_=str, default='settings_item')


class DefaultValue(QueryObject):
    id: int
    id_prog: int
    u_base_name: str
    u_obj_name: str
    u_prm_name: str
    prm_value: str


class UserFormula(QueryListItemObject):
    id_record: int
    type_ = QueryField(type_=str, default='formula')
    id: int
    id_up: int
    param_formula: str
    x_vals: str
    user_id: int


class PlotTemplate(QueryListItemObject):
    id_record: int
    type_ = QueryField(type_=str, default='plot_template')
    id: int
    id_up = QueryField(type_=str, default=-1)
    value: str
    user_id: int


class CustomCurve(QueryObject):
    id: int
    graph_project_id: int
    values: str


class ParamValues(QueryObject):
    param: str
    value: float
    prop_name: float
