import json
import time
from copy import copy
from datetime import datetime

from PySide2.QtGui import QIcon, Qt
from asyncpg import RaiseError

from app import app_logger, basic_funcs
from app.plugins.base_state.models import TreeModel, Node, ANY_CHILD_TYPE
from app.plugins.project import utils
from app.plugins.project.dialogs.create_epure import CreateEpureDialog
from app.plugins.project.dialogs.create_graph import CreateGraphDialog
from app.plugins.project.dialogs.edit_epure import EditEpureDialog
from app.plugins.project.dialogs.select_test import TestSelectionDialog
from app.plugins.project.dialogs.select_test_data import TestDataSelectionDialog
from app.plugins.project.dialogs.test_edit import EditProjectItemDialog
from app.plugins.project.utils_ import get_next_default_combination
from app.plugins.work_data.models import ProductNode, ModelNode, AssemblyNode
from db import sp
from db.tables import PROJECT_TABLE, PROJECT_DATA
from db.transactions import import_project_other_file_data, \
    delete_file_data_project


logger = app_logger.get_logger(__name__)


class InvalidWorkDataDbImport(RuntimeError):
    """DB import committed records that cannot form a Project table."""


_DIAGNOSTIC_STAGE_SECONDS = 0.05
_IMPORT_ITEM_SECONDS = 0.2


class _ImportDiagnostics:
    """Collect and emit compact timings for one WorkData import operation."""

    def __init__(self):
        self.started = time.perf_counter()
        self.stage_times = {}
        self.values = {
            'selected_count': 0,
            'test_count': 0,
            'params_count': 0,
            'records_count': 0,
            'inserted_rows': 0,
            'db_tests': 0,
            'skipped_tests': [],
            'skipped_files': [],
            'skipped_imports': [],
            'db_inserted_rows': 0,
            'source_file_calls': 0,
            'source_files_elapsed': 0.0,
            'db_import_elapsed': 0.0,
            'db_import_max_elapsed': 0.0,
            'slowest_id_excel_file': None,
            'failed_error': None,
        }

    def stage(self, name, always=False, **details):
        return _DiagnosticStage(self, name, always, details)

    def update(self, **values):
        self.values.update(values)

    def add(self, name, value):
        self.values[name] = self.values.get(name, 0) + value

    def record_stage(self, name, elapsed, always=False, **details):
        self.stage_times[name] = self.stage_times.get(name, 0.0) + elapsed
        if always or elapsed >= _DIAGNOSTIC_STAGE_SECONDS:
            suffix = _diagnostic_fields(details)
            logger.info(
                'WorkData import stage: stage=%s, elapsed=%.4fs%s',
                name, elapsed, f', {suffix}' if suffix else '',
            )

    def log_summary(self):
        db_tests = self.values['db_tests']
        db_average = self.values['db_import_elapsed'] / db_tests if db_tests else 0.0
        skipped_imports = self.values['skipped_imports']
        skipped_summary = json.dumps(skipped_imports, ensure_ascii=False, default=str)
        logger.info(
            'WorkData import summary: selected_count=%s, test_count=%s, params_count=%s, '
            'records_count=%s, inserted_rows=%s, db_tests=%s, db_inserted_rows=%s, '
            'skipped_tests=%s, skipped_files=%s, skipped_imports=%s, failed_error=%s, '
            'source_file_calls=%s, '
            'source_files_elapsed=%.4fs, db_import_elapsed=%.4fs, '
            'db_import_avg_elapsed=%.4fs, db_import_max_elapsed=%.4fs, '
            'slowest_id_excel_file=%s, elapsed=%.4fs',
            self.values['selected_count'], self.values['test_count'], self.values['params_count'],
            self.values['records_count'], self.values['inserted_rows'], db_tests,
            self.values['db_inserted_rows'], self.values['skipped_tests'],
            self.values['skipped_files'], skipped_summary, self.values['failed_error'],
            self.values['source_file_calls'],
            self.values['source_files_elapsed'], self.values['db_import_elapsed'], db_average,
            self.values['db_import_max_elapsed'], self.values['slowest_id_excel_file'],
            time.perf_counter() - self.started,
        )
        if self.values['failed_error']:
            logger.error('Импорт прерван из-за ошибки: %s', self.values['failed_error'])
        elif skipped_imports:
            skipped_names = ', '.join(item['file_name'] for item in skipped_imports)
            logger.warning(
                'Импорт завершён частично. Импортировано: %s. Пропущено: %s. '
                'Пропущенные файлы: %s',
                db_tests, len(skipped_imports), skipped_names,
            )
        else:
            logger.info('Импорт завершён успешно. Импортировано: %s. Пропущено: 0.', db_tests)


class _DiagnosticStage:
    def __init__(self, diagnostics, name, always, details):
        self.diagnostics = diagnostics
        self.name = name
        self.always = always
        self.details = details
        self.started = None

    def __enter__(self):
        self.started = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.diagnostics.record_stage(
            self.name, time.perf_counter() - self.started, self.always, **self.details
        )


def _diagnostic_fields(values):
    return ', '.join(f'{name}={value}' for name, value in values.items())


_INVALID_PROJECT_DATA_METADATA = 'WorkData import produced invalid ProjectData metadata'
_FILE_NAME_FIELDS = (
    'datafile_full_name', 'full_name', 'datafile_short_name', 'short_name',
    'file_name', 'name', 'excel_file_name', 'path',
)


def _workdata_file_name(datafile, id_excel_file, file_version):
    for field in _FILE_NAME_FIELDS:
        value = getattr(datafile, field, None)
        if value:
            return str(value)
    return f'id_excel_file={id_excel_file}, version={file_version}'


def _is_invalid_project_data_metadata_error(exc):
    return isinstance(exc, InvalidWorkDataDbImport) or _INVALID_PROJECT_DATA_METADATA in str(exc)


def _workdata_import_source(source_test, cache=None):
    source_test_id = int(source_test._data.id)
    if cache is not None and source_test_id in cache:
        result = cache[source_test_id]
        if isinstance(result, Exception):
            raise result
        return result

    try:
        datafile = sp.get_product_uniskad_files(source_test_id, 'input_excel')
        if not datafile:
            raise RuntimeError(f'No input Excel datafile found for WorkData test {source_test_id}')
        id_excel_file = datafile.id_datafile
        file_version = int(getattr(source_test, 'final_version', 0))
        result = id_excel_file, file_version, _workdata_file_name(
            datafile, id_excel_file, file_version
        )
    except Exception as exc:
        if cache is not None:
            cache[source_test_id] = exc
        raise
    if cache is not None:
        cache[source_test_id] = result
    return result


def _import_workdata_curves_db(target_project_id, id_excel_file, file_version, curve_names,
                               diagnostics=None, source_test_id=None):
    call_started = time.perf_counter()
    inserted_rows = sp.import_workdata_file_curves_to_project(
        target_project_id, id_excel_file, file_version, curve_names
    )
    call_elapsed = time.perf_counter() - call_started
    if diagnostics is not None:
        diagnostics.record_stage(
            'sp.import_workdata_file_curves_to_project', call_elapsed,
            target_project_id=target_project_id, source_test_id=source_test_id,
            id_excel_file=id_excel_file, file_version=file_version, params_count=len(curve_names),
        )
    if isinstance(inserted_rows, RaiseError):
        logger.error(
            'WorkData -> ProjectData DB import raised database error: '
            'target_project_id=%s, id_excel_file=%s, file_version=%s, error=%s, path=db',
            target_project_id, id_excel_file, file_version, inserted_rows,
        )
        raise inserted_rows
    if inserted_rows is None:
        raise RuntimeError('WorkData DB-side import returned no inserted row count')

    stats_started = time.perf_counter()
    stats = sp.get_project_data_import_stats(target_project_id)
    stats_elapsed = time.perf_counter() - stats_started
    if diagnostics is not None:
        diagnostics.record_stage(
            'sp.get_project_data_import_stats', stats_elapsed,
            target_project_id=target_project_id, source_test_id=source_test_id,
            id_excel_file=id_excel_file, file_version=file_version,
        )
    if stats is None:
        raise RuntimeError('WorkData DB-side import returned no validation statistics')
    rows_match = stats.row_type_count == stats.row_npp_count
    columns_match = stats.column_type_count == stats.column_npp_count
    if inserted_rows > 0 and (stats.column_type_count == 0 or stats.column_npp_count == 0):
        logger.error(
            'WorkData -> ProjectData DB import produced an unusable table: '
            'target_project_id=%s, inserted_rows=%s, column_type_count=%s, '
            'column_npp_count=%s, path=db',
            target_project_id, inserted_rows, stats.column_type_count,
            stats.column_npp_count,
        )
        raise InvalidWorkDataDbImport('WorkData DB-side import produced no ProjectData columns')
    if not rows_match or not columns_match:
        raise InvalidWorkDataDbImport('WorkData DB-side import produced mismatched ProjectData metadata')
    return inserted_rows


def _normalize_selected_parents(selected, parent_id):
    selected_ids = {obj._data.id_prod for obj in selected}
    for obj in selected:
        if obj._data.id_up_prod not in selected_ids:
            obj._data.id_up_prod = parent_id


def _resolve_workdata_import_sources(source_tests, diagnostics=None):
    started = time.perf_counter()
    cache = {}
    source_tests = list(source_tests)
    with sp.session.progress('Получение файлов WorkData', total=len(source_tests)) as progress:
        for index, source_test in enumerate(source_tests, 1):
            source_test_id = int(source_test._data.id)
            progress.update(
                current=index,
                message=f'Получение файла WorkData {index} из {len(source_tests)}',
                detail=f'Испытание: {source_test_id}',
            )
            if source_test_id in cache:
                continue
            item_started = time.perf_counter()
            if diagnostics is not None:
                diagnostics.add('source_file_calls', 1)
            try:
                cache[source_test_id] = _workdata_import_source(source_test, cache)
            except Exception as exc:
                cache[source_test_id] = exc
            elapsed = time.perf_counter() - item_started
            if diagnostics is not None:
                result = cache[source_test_id]
                id_excel_file = result[0] if not isinstance(result, Exception) else None
                file_version = result[1] if not isinstance(result, Exception) else None
                diagnostics.record_stage(
                    'sp.get_product_uniskad_files', elapsed, source_test_id=source_test_id,
                    id_excel_file=id_excel_file, file_version=file_version,
                )
    if diagnostics is not None:
        diagnostics.update(source_files_elapsed=time.perf_counter() - started)
    return cache


def _import_workdata_tests(test_projects, source_tests, param_list, source_cache,
                           diagnostics=None):
    db_elapsed = 0.0
    db_inserted_rows = 0
    db_tests = 0
    db_max_elapsed = 0.0
    slowest_id_excel_file = None
    skipped_imports = []

    total = len(test_projects)
    with sp.session.progress('Импорт WorkData', total=total, blocking=True) as progress:
        for index, test in enumerate(test_projects, 1):
            source_test_id = int(test.prop_value)
            source_hint = source_cache.get(source_test_id)
            file_hint = source_hint[2] if isinstance(source_hint, tuple) and len(source_hint) > 2 else None
            progress.update(
                current=index,
                message=f'Импорт испытания {index} из {total}',
                detail=f'Файл: {file_hint or "не определён"}  Испытание: {source_test_id}  Осталось: {total - index}',
            )
            source_test = source_tests.get(source_test_id)
            id_excel_file = file_version = None
            file_name = None
            db_started = time.perf_counter()
            try:
                if source_test is None:
                    raise RuntimeError(f'Selected WorkData test {source_test_id} was not found')
                id_excel_file, file_version, file_name = _workdata_import_source(source_test, source_cache)
                inserted_count = _import_workdata_curves_db(
                    test.project_id, id_excel_file, file_version, param_list, diagnostics, source_test_id
                )
            except Exception as exc:
                elapsed = time.perf_counter() - db_started
                db_elapsed += elapsed
                if elapsed > db_max_elapsed:
                    db_max_elapsed = elapsed
                    slowest_id_excel_file = id_excel_file
                if not _is_invalid_project_data_metadata_error(exc):
                    if diagnostics is not None:
                        diagnostics.update(
                            db_tests=db_tests, db_inserted_rows=db_inserted_rows,
                            inserted_rows=db_inserted_rows, db_import_elapsed=db_elapsed,
                            failed_error=str(exc),
                        )
                    raise
                file_name = file_name or f'id_excel_file={id_excel_file}, version={file_version}'
                reason = f'Файл {file_name}: {exc}'
                skipped_import = {
                    'source_test_id': source_test_id,
                    'target_project_id': test.project_id,
                    'id_excel_file': id_excel_file,
                    'file_version': file_version,
                    'file_name': file_name,
                    'reason': reason,
                }
                skipped_imports.append(skipped_import)
                logger.warning(
                    'WorkData import skipped item: target_project_id=%s, source_test_id=%s, '
                    'id_excel_file=%s, file_version=%s, file_name=%s, elapsed=%.4fs, reason=%s',
                    test.project_id, source_test_id, id_excel_file, file_version, file_name,
                    elapsed, reason,
                )
                progress.update(
                    detail=f'Пропущен файл: {file_name}  Осталось: {total - index}'
                )
                continue

            elapsed = time.perf_counter() - db_started
            db_elapsed += elapsed
            db_inserted_rows += inserted_count
            db_tests += 1
            if elapsed > db_max_elapsed:
                db_max_elapsed = elapsed
                slowest_id_excel_file = id_excel_file
            if elapsed >= _IMPORT_ITEM_SECONDS:
                logger.info(
                    'WorkData import item: target_project_id=%s, source_test_id=%s, '
                    'id_excel_file=%s, file_version=%s, file_name=%s, rows=%s, '
                    'elapsed=%.4fs, path=db',
                    test.project_id, source_test_id, id_excel_file, file_version, file_name,
                    inserted_count, elapsed,
                )

    if diagnostics is not None:
        diagnostics.record_stage('DB-import loop', db_elapsed, tests_count=db_tests,
                                 inserted_rows=db_inserted_rows,
                                 skipped_files=len(skipped_imports))
        diagnostics.update(
            db_tests=db_tests, db_inserted_rows=db_inserted_rows,
            inserted_rows=db_inserted_rows, db_import_elapsed=db_elapsed,
            db_import_max_elapsed=db_max_elapsed, slowest_id_excel_file=slowest_id_excel_file,
            skipped_tests=sorted({item['source_test_id'] for item in skipped_imports}),
            skipped_files=[item['file_name'] for item in skipped_imports],
            skipped_imports=skipped_imports,
        )
    return len(test_projects), db_inserted_rows, skipped_imports


class ProjectRoot(Node):
    """Корень дерева первичных данных"""

    def __init__(self, data):
        super().__init__(data)
        self.scheme = PROJECT_TABLE

        self.curve_name = None
        self.curve_width = None
        self.curve_color = None
        self.curve_line_style = None
        self.curve_point_symbol = None
        self.curve_point_size = None

        self.curve_point_size = None
        self.curve_symbol_color = None
        self.curve_symbol_fill_color = None

        self.selected_curve_point_size = 0.5
        self.selected_curve_symbol_color = 'black'
        self.selected_curve_symbol_fill_color = 'red'

        self.selected_points = None

        self.display_as_curve = True
        self.use_conditions = False
        self.use_filters = False
        self.conditions = None
        self.filters = None

        self.graph_x_comment = None
        self.graph_y_comment = None

    _project_types_cache = None

    @staticmethod
    def internal_type():
        return 'root'

    def columnCount(self):
        return 1

    @classmethod
    def get_project_type_id(cls, type_name):
        if cls._project_types_cache is None:
            cls._project_types_cache = {
                project_type.project_type: project_type.id_project_type
                for project_type in sp.get_projecttypes_list()
            }
        return cls._project_types_cache.get(type_name)

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [FolderNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return ['add']

    @staticmethod
    def update(item, prop_name, prop_value):
        """
        Обновление элементов проекта
        :param item:
        :param prop_name:
        :param prop_value:
        :return:
        """
        data = item._data
        data.project_prop = prop_name
        data.project_prop_value = prop_value
        project_record = data.table_fit(PROJECT_TABLE)
        item = sp.new_update_project_from_record(project_record)
        if item:
            return item

    @staticmethod
    def bulk_update(item, props):
        item = sp.new_update_project_from_record_array(props)

    @staticmethod
    def remove(item, final=False):
        cascade = False
        if item.childCount():
            if basic_funcs.get_answer('Внимание',
                                      'Невозможно удалить этот элемент, так как у него есть дочерние элементы. Удалить каскадно?'):
                cascade = True
            else:
                return False
        success = sp.delete_project(item._data.id, True, cascade, final)
        if success:
            item._data.deleted = True
        return success

    @staticmethod
    def restore(item):
        success = sp.delete_project(item._data.id, False, False, False)
        if success:
            item._data.deleted = False
        return success


class ProjectNode(ProjectRoot):

    @staticmethod
    def internal_type():
        return 'project'

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [FolderNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return ['add']

    @staticmethod
    def self_internal_actions():
        return ['remove']

    def get_icon(self, column=0):
        if self.icon:
            return QIcon(self.icon)
        return QIcon(":/project_copy.png")


class FolderNode(ProjectRoot):
    inherit_actions_from_parent = False

    @staticmethod
    def internal_type():
        return 'folder'

    @staticmethod
    def is_folder():
        return True

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [ANY_CHILD_TYPE]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return ['add']

    @classmethod
    def creatable_types(cls):
        return [cls]

    @staticmethod
    def add(up_node_id, parent):
        folder_name = basic_funcs.get_text('Создание элемента', 'Название: ', '')
        if not folder_name:
            return
        folder_name = folder_name.strip()
        if not folder_name:
            return

        folder_type_id = ProjectRoot.get_project_type_id('folder')
        if folder_type_id is None:
            basic_funcs.error('Ошибка', 'Не удалось определить тип "folder".')
            return

        parent_data = getattr(parent, '_data', None)
        project_author = getattr(parent_data, 'project_author', None)
        project_owner = getattr(parent_data, 'project_owner', None)

        record = (
            None,
            None,
            up_node_id,
            folder_type_id,
            'name',
            folder_name,
            project_author,
            project_owner,
            datetime.now(),
            0,
            False,
        )

        new_folder = sp.new_update_project_from_record(record)
        if new_folder:
            new_folder.type_ = 'folder'
            return FolderNode(new_folder)

    def get_icon(self, column=0):
        if self.icon:
            return QIcon(self.icon)
        return QIcon(":/folder.png")


class ProductFolderNode(ProjectRoot):
    exclude_from_base_actions = ['_open', '_remove']

    @staticmethod
    def internal_type():
        return 'product_folder'

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [TestNode, FileNode, FolderNode, WDAssemblyNode, WDProductNode, WDModelNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return ['add', 'import']

    def get_icon(self, column=0):
        if self.icon:
            return QIcon(self.icon)
        return QIcon(":/folder.png")


class GraphFolderNode(ProjectRoot):
    exclude_from_base_actions = ['_open', '_remove']

    @staticmethod
    def internal_type():
        return 'graph_folder'

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [GraphNode, FileNode, FolderNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return ['add', 'save_graph_template', 'apply_graph_template']

    def get_icon(self, column=0):
        if self.icon:
            return QIcon(self.icon)
        return QIcon(":/folder.png")


class EpureFolderNode(ProjectRoot):
    exclude_from_base_actions = ['_open', '_remove']

    @staticmethod
    def internal_type():
        return 'epure_folder'

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [EpureNode, FileNode, FolderNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return ['add', 'save_epure_template', 'apply_epure_template']

    def get_icon(self, column=0):
        if self.icon:
            return QIcon(self.icon)
        return QIcon(":/folder.png")


class WDAssemblyNode(AssemblyNode, ProjectRoot):
    has_customization = True
    scheme = PROJECT_TABLE

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [FolderNode, WDProductNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return ['add', 'remove']

    @staticmethod
    def remove(item, final=False):
        success = sp.delete_project(item._data.id, True, False, final)
        if success:
            item._data.deleted = True
        return success

    def customize(self, ):
        dialog = EditProjectItemDialog(self)
        if dialog.exec_():
            parent = self.parent()
            while parent.internal_type() != 'product_folder':
                parent = parent.parent()

            if parent is None:
                return self

            root = parent.parent()
            graph_folder = [folder for folder in root.children if folder.internal_type() == 'graph_folder']
            if len(graph_folder) == 1:
                return tuple([child for child in graph_folder[0].children if child._data.deleted is False] + [self])
            return self

    @staticmethod
    def restore(item):
        cascade = False
        if item.childCount():
            if basic_funcs.get_answer('Внимание',
                                      'Невозможно удалить этот элемент, так как у него есть дочерние элементы. Удалить каскадно?'):
                cascade = True
            else:
                return False
        success = sp.delete_project(item._data.id, False, cascade, False)
        if success:
            item._data.deleted = False
        return success


class WDModelNode(ModelNode, ProjectRoot):
    has_customization = True
    scheme = PROJECT_TABLE

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [FolderNode, WDAssemblyNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return ['add', 'remove']

    @staticmethod
    def remove(item, final=False):
        cascade = False
        if item.childCount():
            if basic_funcs.get_answer('Внимание',
                                      'Невозможно удалить этот элемент, так как у него есть дочерние элементы. Удалить каскадно?'):
                cascade = True
            else:
                return False
        success = sp.delete_project(item._data.id, True, cascade, final)
        if success:
            item._data.deleted = True
        return success

    def customize(self, ):
        dialog = EditProjectItemDialog(self)
        if dialog.exec_():
            parent = self.parent()
            while parent.internal_type() != 'product_folder':
                parent = parent.parent()

            if parent is None:
                return self

            root = parent.parent()
            graph_folder = [folder for folder in root.children if folder.internal_type() == 'graph_folder']
            if len(graph_folder) == 1:
                return tuple([child for child in graph_folder[0].children if child._data.deleted is False] + [self])
            return self

    @staticmethod
    def restore(item):
        success = sp.delete_project(item._data.id, False, False, False)
        if success:
            item._data.deleted = False
        return success


class WDProductNode(ProductNode, ProjectRoot):
    has_customization = True
    scheme = PROJECT_TABLE

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [FolderNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return ['add', 'remove']

    @staticmethod
    def remove(item, final=False):
        cascade = False
        if item.childCount():
            if basic_funcs.get_answer('Внимание',
                                      'Невозможно удалить этот элемент, так как у него есть дочерние элементы. Удалить каскадно?'):
                cascade = True
            else:
                return False
        success = sp.delete_project(item._data.id, True, cascade, final)
        if success:
            item._data.deleted = True
        return success

    def customize(self, ):
        dialog = EditProjectItemDialog(self)
        if dialog.exec_():
            parent = self.parent()
            while parent.internal_type() != 'product_folder':
                parent = parent.parent()

            if parent is None:
                return self

            root = parent.parent()
            graph_folder = [folder for folder in root.children if folder.internal_type() == 'graph_folder']
            if len(graph_folder) == 1:
                return tuple([child for child in graph_folder[0].children if child._data.deleted is False] + [self])
            return self

    @staticmethod
    def restore(item):
        success = sp.delete_project(item._data.id, False, False, False)
        if success:
            item._data.deleted = False
        return success


class TestNode(ProjectRoot):
    has_customization = True

    def __init__(self, data):

        super().__init__(data)
        self.param_sort_setting = None
        self.default_values = False

    @staticmethod
    def internal_type():
        return 'test'

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return [FolderNode]

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        # return ['export', 'remove']
        return ['remove']

    def get_icon(self, column=0):
        if self.icon:
            return QIcon(self.icon)
        return QIcon(":/test.png")

    def customize(self, ):
        dialog = EditProjectItemDialog(self)
        if dialog.exec_():
            parent = self.parent()
            while parent.internal_type() != 'product_folder':
                parent = parent.parent()

            if parent is None:
                return self

            root = parent.parent()
            graph_folder = [folder for folder in root.children if folder.internal_type() == 'graph_folder']
            epure_folder = [folder for folder in root.children if folder.internal_type() == 'epure_folder']
            if len(graph_folder) == 1 and len(epure_folder) == 1:
                return tuple([child for child in graph_folder[0].children + epure_folder[0].children if
                              child._data.deleted is False] + [self])
            return self

    @staticmethod
    def add(up_node_id, parent):
        diagnostics = _ImportDiagnostics()
        try:
            with diagnostics.stage('create TestSelectionDialog'):
                dialog = TestSelectionDialog()
            with diagnostics.stage('wait TestSelectionDialog'):
                accepted = dialog.exec_()
            if not accepted:
                return None

            with diagnostics.stage('sp.get_projecttypes_list'):
                project_type_list = sp.get_projecttypes_list()
            project_types = {}
            project_types_reversed = {}  # TODO придумать как тут ускорить
            for project_type in project_type_list:
                project_types[project_type.project_type] = project_type.id_project_type
                project_types_reversed[project_type.id_project_type] = project_type.project_type

            def new_prop(data, prop_name, prop_value):
                prop = copy(data)
                prop.project_prop = prop_name
                prop.project_prop_value = str(prop_value)
                return prop

            class_dict = {
                'test': TestNode, 'assembly': WDAssemblyNode, 'model': WDModelNode,
                'product': WDProductNode, 'folder': FolderNode, 'file': FileNode,
            }

            with diagnostics.stage('get selected result'):
                selected = dialog.get_result()
            diagnostics.update(selected_count=len(selected))

            with diagnostics.stage('normalize selected parents', selected_count=len(selected)):
                current_item = selected[0]
                while current_item.parent() in selected:
                    current_item = current_item.parent()
                parent_id = current_item._data.id_up_prod
                _normalize_selected_parents(selected, parent_id)

            with diagnostics.stage('build source WorkData test ids', selected_count=len(selected)):
                source_tests = {
                    int(item._data.id): item for item in selected if item.internal_type() == 'test'
                }
            diagnostics.update(test_count=len(source_tests))

            # This lookup only needs source WorkData ids, so parameter selection can safely
            # happen before project writes. Cancelling now leaves the project untouched.
            sp.session.update_loading_bar('Получение списка параметров')
            with diagnostics.stage(
                    'sp.get_param_list_from_test_id_list', test_count=len(source_tests)):
                params = sp.get_param_list_from_test_id_list(list(source_tests))
            diagnostics.update(params_count=len(params) if params else 0)
            if not params:
                print('Не хватает данных.')
                return None

            with diagnostics.stage('create TestDataSelectionDialog', params_count=len(params)):
                data_dialog = TestDataSelectionDialog(params)
            with diagnostics.stage('wait TestDataSelectionDialog', params_count=len(params)):
                accepted = data_dialog.exec_()
            if not accepted:
                return None
            with diagnostics.stage('get param_list', params_count=len(params)):
                param_list = data_dialog.get_result()
            diagnostics.update(params_count=len(param_list))

            with diagnostics.stage('build selected_data and selected_props_data',
                                   selected_count=len(selected), test_count=len(source_tests)):
                selected_data = []
                selected_props_data = []
                project_node = parent.parent()
                next_default_value = (int(project_node.default_test_value) + 1
                                      if hasattr(project_node, 'default_test_value') else 0)
                for product in selected:
                    product_data = product._data
                    product_data.project_id = product_data.id_prod
                    product_data.project_id_up = product_data.id_up_prod
                    product_data.project_type = project_types[product.internal_type()]
                    product_data.project_prop = product_data.prod_prop
                    product_data.project_prop_value = product_data.prod_prop_value
                    selected_data.append(product_data.table_fit(PROJECT_TABLE))

                    if product.internal_type() == 'file':
                        pass  # TODO не работает импорт файлов из рабочих данных
                    if product.internal_type() == 'test':
                        next_default_value += 1
                        line_style, color, symbol = get_next_default_combination(next_default_value)
                        test_prop_data = copy(product_data)
                        test_prop_data.project_prop = 'test_id'
                        test_prop_data.project_prop_value = str(product_data.id)
                        selected_props_data.append(test_prop_data.table_fit(PROJECT_TABLE))
                        selected_props_data.extend([
                            new_prop(product_data, 'curve_line_style', int(Qt.NoPen)).table_fit(PROJECT_TABLE),
                            new_prop(product_data, 'curve_color', color).table_fit(PROJECT_TABLE),
                            new_prop(product_data, 'curve_symbol_color', 'black').table_fit(PROJECT_TABLE),
                            new_prop(product_data, 'curve_symbol_fill_color', color).table_fit(PROJECT_TABLE),
                            new_prop(product_data, 'curve_point_symbol', symbol).table_fit(PROJECT_TABLE),
                            new_prop(product_data, 'curve_point_size', 10).table_fit(PROJECT_TABLE),
                            new_prop(product_data, 'curve_width', 1).table_fit(PROJECT_TABLE),
                        ])
            records_count = len(selected_data) + len(selected_props_data)
            diagnostics.update(records_count=records_count)

            sp.session.update_loading_bar('Подготовка проекта')
            with diagnostics.stage('sp.new_update_project_from_record', project_id=up_node_id):
                sp.new_update_project_from_record(
                    new_prop(project_node._data, 'default_test_value', next_default_value).table_fit(
                        PROJECT_TABLE))

            with diagnostics.stage('sp.copy_tree_project_bunch', project_id=up_node_id,
                                   records_count=records_count):
                result = sp.copy_tree_project_bunch(
                    selected_data + selected_props_data, parent_id, up_node_id)

            with diagnostics.stage('build test_projects', records_count=len(result)):
                result_mass = []
                test_projects = []
                for item in result:
                    item.type_ = project_types_reversed[item.project_type]
                    result_mass.append(class_dict[item.type_](item))
                    if item.type_ == 'test' and item.prop_name == 'test_id':
                        test_projects.append(item)

            with diagnostics.stage('resolve WorkData source files', test_count=len(source_tests)):
                source_cache = _resolve_workdata_import_sources(source_tests.values(), diagnostics)

            with diagnostics.stage('DB-import loop',
                                   test_count=len(test_projects), params_count=len(param_list)):
                _import_workdata_tests(
                    test_projects, source_tests, param_list, source_cache, diagnostics,
                )
            return tuple(result_mass)
        finally:
            diagnostics.log_summary()

    @staticmethod
    def export(item):
        pass


class GraphNode(ProjectRoot):
    has_customization = False

    def __init__(self, data):
        super().__init__(data)

        self.graph_label_y = ''
        self.graph_label_x = ''
        self.graph_grid_size = 0

        self.graph_left_x = ''
        self.graph_right_x = ''
        self.graph_bottom_y = ''
        self.graph_top_y = ''
        self.graph_fixed_x = False
        self.graph_fixed_y = False
        self.graph_x_major_step = ''
        self.graph_x_minor_step = ''
        self.graph_y_major_step = ''
        self.graph_y_minor_step = ''
        self.graph_name = ''
        self.graph_x_step_auto = True
        self.graph_y_step_auto = True

        self.graph_group_by = ''
        self.graph_constraints = '{}'
        self.graph_appr_type = ''

        self.graph_x_multiplier = 1
        self.graph_y_multiplier = 1

        self.graph_x_dultiplier = 1
        self.graph_y_dultiplier = 1

    @staticmethod
    def internal_type():
        return 'graph'

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return []

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return []

    @staticmethod
    def self_internal_actions():
        return ['remove']

    def get_icon(self, column=0):
        if self.icon:
            return QIcon(self.icon)
        return QIcon(":/graph.png")

    @staticmethod
    def add(up_node_id, parent):
        project_item = parent.parent()
        dialog = CreateGraphDialog(project_item._data.id)
        if dialog.exec_():  # Если произошло изменение данных
            res = dialog.get_result()
            return GraphNode._add_graph(up_node_id, 'xy', f'{res["graph_name"]}', res["x_curve"], res["y_curve"],
                                        res["group_by"], res['constraints'])

    @staticmethod
    def _add_graph(up_node_id, graph_type, item_name, x_curve=None, y_curve=None, group_by=None, constraints=None):
        project_types = {}
        project_types_reversed = {}
        result = []
        result_mass = []

        for project_type in sp.get_projecttypes_list():
            project_types[project_type.project_type] = project_type.id_project_type
            project_types_reversed[project_type.id_project_type] = project_type.project_type

        if graph_type == 'xy':
            curves = sp.add_new_xy_graph(up_node_id, item_name, x_curve, y_curve, group_by, constraints)
            result = curves

        class_dict = {
            'graph': GraphNode
        }

        for item in result:
            item.type_ = project_types_reversed[item.project_type]
            result_mass.append(class_dict[item.type_](item))

        return tuple(result_mass)


class EpureNode(ProjectRoot):
    has_customization = True

    def __init__(self, data):
        super().__init__(data)

        self.graph_label_y = ''
        self.graph_label_x = ''
        self.graph_grid_size = 0

        self.graph_x_step_auto = True
        self.graph_y_step_auto = True

        self.graph_left_x = ''
        self.graph_right_x = ''
        self.graph_bottom_y = ''
        self.graph_top_y = ''
        self.graph_fixed_x = False
        self.graph_fixed_y = False
        self.graph_x_major_step = 0
        self.graph_x_minor_step = 0
        self.graph_y_major_step = 0
        self.graph_y_minor_step = 0
        self.graph_name = ''

        self.oy_list = None
        self.extra_param = None
        self.extra_param_values = None

        self.graph_x_multiplier = 1
        self.graph_y_multiplier = 1

        self.graph_x_dultiplier = 1
        self.graph_y_dultiplier = 1

    @staticmethod
    def internal_type():
        return 'epure'

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return []

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return []

    @staticmethod
    def self_internal_actions():
        return ['remove']

    def get_icon(self, column=0):
        if self.icon:
            return QIcon(self.icon)
        return QIcon(":/epure.png")

    def customize(self, ):
        project_item = self.parent().parent()
        dialog = EditEpureDialog(self, project_item, project_item._data.id, self.parent()._data.project_id)
        if dialog.exec_():
            return self

    @staticmethod
    def add(up_node_id, parent):
        project_item = parent.parent()
        dialog = CreateEpureDialog(project_item, project_item._data.id, up_node_id)
        if dialog.exec_():  # Если произошло изменение данных
            result = dialog.get_result()
            for item in result:
                item.type_ = 'epure'
            return tuple(result)


class FileNode(ProjectRoot):
    """Узел-файл"""

    @staticmethod
    def internal_type():
        return 'file'

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (модель)"""
        return []

    @staticmethod
    def self_internal_actions():
        """Список действий с данным элементом (изделие)"""
        return ['remove']

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return []

    def get_icon(self, column=0):
        """Иконка элемента"""
        if column == 0:
            return QIcon(":/file.png")

    @staticmethod
    def add(up_node_id, parent):
        files = basic_funcs.get_files("Открытие сторонних файлов", "* (*.*)",
                                      single_selection=False)
        result_items = []
        for file in files:
            filename = file.split('/')[-1][:30]
            new_product = import_project_other_file_data(filename, file, 19, up_node_id)
            if new_product:
                result_items += [FileNode(new_product)]
        return tuple(result_items)

    @staticmethod
    def remove(item, final=False):
        if not final:
            success = sp.delete_project(item._data.id, True, False, False)
            if success:
                item._data.deleted = True
            return success
        else:
            success = delete_file_data_project(item._data.id, 'other', other_format=True)
            return success


class ParamNode(Node):

    @staticmethod
    def internal_type():
        return 'param'

    @staticmethod
    def container_types():
        """Возвращает типы возможных дочерних элементов"""
        return []

    @staticmethod
    def internal_actions():
        """Список действий с данным элементом (корень дерева)"""
        return []

    def get_icon(self, column=0):
        return QIcon(":/alpha.png")

    def data(self, column=0):
        return self._data.prop_value


class ProjectTreeModel(TreeModel):
    """Дерево справочника изделий"""

    def __init__(self):
        super().__init__()
        self._root = ProjectRoot(None)  # переопределяем корень
        self.root_id = 1
        # связать тип элемента с классом в программе
        self.register_nodes(
            [ProjectRoot, ProjectNode, FolderNode, TestNode, GraphNode, EpureNode, EpureFolderNode,
             WDProductNode, WDModelNode, WDAssemblyNode, GraphFolderNode, ProductFolderNode, ParamNode, FileNode,
             ])

    def update_external_graphs(self):
        root = self._root
        graph_folder = [folder for folder in root.children if folder.internal_type() == 'graph_folder']
        epure_folder = [folder for folder in root.children if folder.internal_type() == 'epure_folder']
        if len(graph_folder) == 1 and len(epure_folder) == 1:
            self.view.update_external_nodes(
                tuple([child for child in graph_folder[0].children + epure_folder[0].children if
                       child._data.deleted is False]))
