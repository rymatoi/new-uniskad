import datetime
from functools import lru_cache
from typing import List

import asyncpg

import config.config
from app.basic_funcs import timing_decorator
from app.menu import menu_structure
from db import session
from db.schemas import *


def convert_to_pg_array(tuples_list):
    pg_array = ['(' + ','.join(map(str, tpl)) + ')' for tpl in tuples_list]
    return pg_array


@session.stored_procedure(modifying=True, description='Авторизация')
def checkuserpassword(name: str, password: str) -> bool:
    session.authorize(name, password)
    return session.call('checkuserpassword', name, password)


@session.stored_procedure(modifying=True, description='Изменение количества попыток')
def reduce_user_fail_count(userlogin: str) -> bool:
    return session.call('reduce_user_fail_count', userlogin)


@session.stored_procedure(modifying=True, description='Получение пользовательских настроек')
def set_default_value(p_id_prog: int, p_base_name: str,
                      p_obj_name: str,
                      p_prm_name: str,
                      p_prm_value: str) -> bool:
    return session.call('set_default_value', p_id_prog, p_base_name,
                        p_obj_name,
                        p_prm_name,
                        p_prm_value)


@session.stored_procedure(modifying=True, description='Установка пользовательской настройки')
def set_user_default_value(p_id_prog: int, p_base_name: str,
                           p_obj_name: str,
                           p_prm_name: str,
                           p_prm_value: str) -> bool:
    return session.call('set_user_default_value', p_id_prog, p_base_name,
                        p_obj_name,
                        p_prm_name,
                        p_prm_value)


@session.stored_procedure(description='Получение пользовательской настройки')
def get_default_value(p_id_prog: int, p_base_name: str,
                      p_obj_name: str,
                      p_prm_name: str,
                      ) -> dict:
    return session.call('get_default_value', p_id_prog, p_base_name,
                        p_obj_name,
                        p_prm_name)


@session.stored_procedure()
def get_user_default_value(p_id_prog: int, p_base_name: str,
                           p_obj_name: str,
                           p_prm_name: str,
                           ) -> dict:
    return session.call('get_user_default_value', p_id_prog, p_base_name,
                        p_obj_name,
                        p_prm_name)


@session.stored_procedure(description='Создание пользователя')
def new_uniskaduser(p_new_user_id_prog: int, p_new_user_login: str, p_new_user_password: str, p_new_user_fam: str,
                    p_new_user_name: str) -> bool:
    return session.call('new_uniskaduser', p_new_user_id_prog, p_new_user_login, p_new_user_password, p_new_user_fam,
                        p_new_user_name)


@session.stored_procedure(description="Получение локаций")
def get_locations() -> List[Location]:
    return session.call('get_locations')


@session.stored_procedure(description="Получение пунктов меню")
def get_all_menus() -> List[Menu]:
    return session.call('get_all_menus')


@session.stored_procedure(description="Получение режимов")
def get_modes() -> List[Mode]:
    return session.call('get_modes')


@session.stored_procedure(description="Получение списка пользователей")
def get_full_users_list() -> List[User]:
    return session.call('get_full_users_list')


@session.stored_procedure(description="Получение списка ролей для сессионного пользователя")
def get_user_role_list_() -> List[Role]:
    return session.call('get_user_role_list_')


@session.stored_procedure(description="Получение списка ролей для пользователя")
def get_user_role_list_by_id(p_user_id: int) -> List[Role]:
    return session.call('get_user_role_list_by_id', p_user_id)


@session.stored_procedure(description="Получение ролей")
def get_roles() -> List[Role]:
    return session.call('get_roles')


@session.stored_procedure(description="Получение текущего пользователя")
def get_sesion_user() -> dict:
    return session.call('get_sesion_user')


@session.stored_procedure(description="Получение списка ролей для пользователя")
def get_user_role_list() -> List[UserRole]:
    return session.call('get_user_role_list')


@session.stored_procedure(description="Получение списка элементов дерева изделий")
def get_all_products() -> List[Product]:
    return session.call('get_all_products')


@session.stored_procedure(modifying=True, description='Удаление изделия')
def delete_product(p_id_product: int, p_deleted: bool, p_cascade: bool, p_final_delete: bool) -> bool:
    return session.call('delete_product', p_id_product, p_deleted, p_cascade, p_final_delete)


@session.stored_procedure(description='Получение данных файла')
def get_all_uniskad_datafiles() -> List[DataFile]:
    return session.call('get_all_uniskad_datafiles')


@session.stored_procedure(description='Получение текущего пользователя')
def get_current_active_user() -> User:
    return session.call('get_current_active_user')


@session.stored_procedure(description='Авторизация')
def get_datafile_type_id(p_datafile_type: str) -> int:
    return session.call('get_datafile_type_id', p_datafile_type)


@lru_cache
@session.stored_procedure()
def get_datafiletypes_list() -> List[DataFileType]:
    return session.call('get_datafiletypes_list')


@session.stored_procedure()
def get_id_datafile_from_short_name(p_excel_file_short_name: str, p_datafile_type: str) -> int:
    return session.call('get_id_datafile_from_short_name', p_excel_file_short_name, p_datafile_type)


@session.stored_procedure()
def get_id_datafile_type_from_datafile_type(p_datafile_type: str) -> int:
    return session.call('get_id_datafile_type_from_datafile_type', p_datafile_type)


@timing_decorator
@session.stored_procedure(description='Получение списка испытаний')
def get_product_uniskad_files(p_id_prod: int, p_type: str) -> DataFile:
    return session.call('get_product_uniskad_files', p_id_prod, p_type)


@session.stored_procedure(description='Получение списка испытаний')
def get_project_uniskad_files(p_id_prod: int, p_type: str) -> DataFile:
    return session.call('get_project_uniskad_files', p_id_prod, p_type)


@session.stored_procedure()
def get_uniskad_bin_file(p_id_data_file: int) -> BinaryFile:
    return session.call('get_uniskad_bin_file', p_id_data_file)


@session.stored_procedure()
def get_uniskad_bin_file_only(p_id_data_file: int) -> bytes:
    return session.call('get_uniskad_bin_file_only', p_id_data_file)


@session.stored_procedure()
def get_uniskad_datafile_id(p_short_name: str, p_datafile_type: str) -> int:
    return session.call('get_uniskad_datafile_id', p_short_name, p_datafile_type)


@session.stored_procedure(modifying=True, autocommit=False)
def new_uniskad_binfile(p_id_datafile: int, p_file_name: str, p_file_ext: str, p_user_ver: str, p_ver_comment: str,
                        p_bindata: bytes) -> int:
    return session.call('new_uniskad_binfile', p_id_datafile, p_file_name, p_file_ext, p_user_ver, p_ver_comment,
                        p_bindata)


@session.stored_procedure(modifying=True, autocommit=False)
def new_uniskad_datafile(p_product_id: int, p_datafile_type: str, p_short_name: str, p_full_name: str,
                         p_comment: str) -> DataFile:
    return session.call('new_uniskad_datafile', p_product_id, p_datafile_type, p_short_name, p_full_name,
                        p_comment)


@session.stored_procedure(modifying=True, autocommit=False)
def new_uniskad_datafile_project(p_product_id: int, p_datafile_type: str, p_short_name: str, p_full_name: str,
                                 p_comment: str) -> DataFile:
    return session.call('new_uniskad_datafile_project', p_product_id, p_datafile_type, p_short_name, p_full_name,
                        p_comment)


@session.stored_procedure(modifying=True, autocommit=False)
def create_update_import_file_state(p_id_excel_file: int, p_id_file_state: int, p_file_version: int) -> bool:
    return session.call('create_update_import_file_state', p_id_excel_file, p_id_file_state, p_file_version)


@session.stored_procedure(modifying=True, autocommit=True)
def new_excel_data_array(p_excel_data: list) -> List[ImportFileData]:
    return session.call('new_excel_data_array', p_excel_data)


@session.stored_procedure(modifying=True, autocommit=False)
def remove_uniskad_datafiles(p_id_datafile: int) -> int:
    return session.call('remove_uniskad_datafiles', p_id_datafile)


@session.stored_procedure(modifying=True, autocommit=False)
def remove_uniskad_datafiles_binary(p_id_datafile: int) -> bool:
    return session.call('remove_uniskad_datafiles_binary', p_id_datafile)


@session.stored_procedure(modifying=True, autocommit=False)
def remove_import_file_data(p_id_excel_file: int) -> int:
    return session.call('remove_import_file_data', p_id_excel_file)


@session.stored_procedure(modifying=True, autocommit=False)
def remove_import_file_state(p_id_excel_file: int) -> bool:
    return session.call('remove_import_file_state', p_id_excel_file)


@session.stored_procedure()
def get_import_file_data(p_id_excel_file: int) -> List[ImportFileData]:
    return session.call('get_import_file_data', p_id_excel_file)


@session.stored_procedure(description='Получение данных таблицы')
def get_import_file_data2(p_id_excel_file: int, file_version: int = 0) -> List[ImportFileData]:
    return session.call('get_import_file_data2', p_id_excel_file, file_version)


@timing_decorator
@session.stored_procedure(description='Получение данных таблицы')
def get_import_file_data_simple(p_id_excel_file: int, file_version: int = 0) -> List[ImportFileData]:
    return session.call('get_import_file_data_simple', p_id_excel_file, file_version)


@session.stored_procedure(modifying=True)
def new_upd_excel_data_record(import_file_data: tuple) -> int:
    return session.call('new_upd_excel_data_record', import_file_data)


@session.stored_procedure(modifying=True)
def new_upd_excel_data_array(import_file_data: list) -> bool:
    return session.call('new_upd_excel_data_array', import_file_data)


@session.stored_procedure(modifying=True)
def new_upd_project_data_array(import_file_data: list) -> bool:
    return session.call('new_upd_project_data_array', import_file_data)


@timing_decorator
@session.stored_procedure()
def get_sprav_names_all() -> List[SpravName]:
    return session.call('get_sprav_names_all')


@session.stored_procedure(modifying=True)
def new_sprav_names_record(sprav_names_obj: tuple) -> int:
    return session.call('new_sprav_names_record', sprav_names_obj)


@session.stored_procedure()
def get_id_name_sprav_names(p_param_name: str) -> int:
    return session.call('get_id_name_sprav_names', p_param_name)


@session.stored_procedure(modifying=True)
def set_flag_permanent_sprav_names(p_param_name: int, p_flag_permanent: bool = None) -> bool:
    return session.call('set_flag_permanent_sprav_names', p_param_name, p_flag_permanent)


@session.stored_procedure(modifying=True)
def set_flag_synonim_sprav_names(p_param_name: str, p_flag_synonim: bool, p_permanent_name: str = None) -> bool:
    return session.call('set_flag_synonim_sprav_names', p_param_name, p_flag_synonim, p_permanent_name)


@timing_decorator
@session.stored_procedure()
def get_sprav_eizm_all() -> List[SpravEizm]:
    return session.call('get_sprav_eizm_all')


@session.stored_procedure(modifying=True)
def new_upd_sprav_eizm_record(p_sprav_eizm_record: tuple) -> bool:
    return session.call('new_upd_sprav_eizm_record', p_sprav_eizm_record)


@session.stored_procedure(modifying=True)
def remove_sprav_eizm_record(p_id_eizm: int) -> int:
    return session.call('remove_sprav_eizm_record', p_id_eizm)


@session.stored_procedure()
def get_name_all_eizm(p_id_name: int) -> List[SpravEizm]:
    return session.call('get_name_all_eizm', p_id_name)


@session.stored_procedure(modifying=True)
def add_link_name_eizm(p_id_name: int, p_id_eizm: int) -> bool:
    return session.call('add_link_name_eizm', p_id_name, p_id_eizm)


@session.stored_procedure(modifying=True)
def add_link_name_eizm_array(p_id_name: int, p_id_eizm_list: list) -> bool:
    return session.call('add_link_name_eizm_array', p_id_name, p_id_eizm_list)


@session.stored_procedure(modifying=True)
def remove_link_name_eizm(p_id_name: int, p_id_eizm: int) -> bool:
    return session.call('remove_link_name_eizm', p_id_name, p_id_eizm)


@session.stored_procedure(modifying=True)
def update_sprav_names_record(p_sprav_eizm_record: tuple) -> bool:
    return session.call('update_sprav_names_record', p_sprav_eizm_record)


@session.stored_procedure(modifying=True)
def new_update_project_from_record(p_project: tuple) -> Project:
    return session.call('new_update_project_from_record', p_project)


@session.stored_procedure(modifying=True, description="Создание элемента дерева изделий")  # TODO поставил autocommit
def new_update_product_from_record(p_product: tuple) -> Product:
    return session.call('new_update_product_from_record', p_product)


@session.stored_procedure()
def get_user_projects() -> List[Project]:
    return session.call('get_user_projects')


@lru_cache
@session.stored_procedure()
def get_projecttypes_list() -> List[ProjectType]:
    return session.call('get_projecttypes_list')


@session.stored_procedure()
def get_project(p_project_id: int) -> List[Project]:
    return session.call('get_project', p_project_id)


@session.stored_procedure()
def get_project_children(p_project_id: int) -> List[Project]:
    return session.call('get_project_children', p_project_id)


@session.stored_procedure()
def get_user_menu_(mode: str, location: str) -> List[Menu]:
    return session.call('get_user_menu_', mode, location)


# @session.stored_procedure()
# def get_user_menu_(mode: str, location: str) -> List[Menu]:
#     return session.call('get_menus', mode, location)


@session.stored_procedure()
def get_all_user_menu_(p_role_id: int) -> List[Menu]:
    return session.call('get_all_user_menu_', p_role_id)


@session.stored_procedure(modifying=True)
def grant_remove_role_menu_link(p_id_role: int, p_id_menu: int, p_state: bool) -> bool:
    return session.call('grant_remove_role_menu_link', p_id_role, p_id_menu, p_state)


@session.stored_procedure(modifying=True)
def set_sesion_role(user_role_id: int) -> bool:
    return session.call('set_sesion_role', user_role_id)


@session.stored_procedure(description='Получение данных таблицы')
def get_project_data(p_project_id: int) -> List[ProjectData]:
    return session.call('get_project_data', p_project_id)


@session.stored_procedure(modifying=True)
def new_upd_project_data_record(p_project_data: tuple) -> ProjectData:
    return session.call('new_upd_project_data_record', p_project_data)


@session.stored_procedure(modifying=True)
def new_project_data_array(p_project_data: list) -> List[ProjectData]:
    return session.call('new_project_data_array', p_project_data)


@session.stored_procedure(modifying=True)
def import_workdata_file_curves_to_project(p_target_project_id: int,
                                           p_id_excel_file: int,
                                           p_file_version: int,
                                           p_curve_names: list) -> int:
    return session.call('import_workdata_file_curves_to_project',
                        p_target_project_id, p_id_excel_file,
                        p_file_version, p_curve_names)


@session.stored_procedure(modifying=True)
def delete_project(p_id_project: int, p_deleted: bool, p_cascade: bool, p_final_delete: bool = False) -> bool:
    return session.call('delete_project', p_id_project, p_deleted, p_cascade, p_final_delete)


@session.stored_procedure(modifying=True)
def get_product_types() -> List[ProductType]:
    return session.call('get_product_types')


@session.stored_procedure(modifying=True)
def new_import_file_data_version(p_id_excel_file: int, p_final_version: int, p_file_version: int) -> bool:
    return session.call('new_import_file_data_version', p_id_excel_file, p_final_version, p_file_version)


@session.stored_procedure(modifying=True)
def remove_import_file_data_version(p_id_excel_file: int, p_file_version: int) -> bool:
    return session.call('remove_import_file_data_version', p_id_excel_file, p_file_version)


@session.stored_procedure(modifying=True)
def get_import_file_data_versions(p_id_excel_file: int) -> List[ImportFileState]:
    return session.call('get_import_file_data_versions', p_id_excel_file)


@session.stored_procedure(modifying=True)
def add_upd_sprav_names_array(p_sprav_names: list) -> List[int]:
    return session.call('add_upd_sprav_names_array', p_sprav_names)


@session.stored_procedure(modifying=True)
def new_uniskaduser(p_new_user_id_prog: int, p_new_user_login: str, p_new_user_password: str, p_new_user_fam: str,
                    p_new_user_name: str, p_new_user_id_role: int = None, p_new_user_active: bool = None,
                    p_new_user_deleted: bool = None, p_new_user_password_fail_count: int = None,
                    p_new_user_default_password_fail_count: int = None) -> User:
    return session.call('new_uniskaduser', p_new_user_id_prog, p_new_user_login, p_new_user_password, p_new_user_fam,
                        p_new_user_name, p_new_user_id_role, p_new_user_active,
                        p_new_user_deleted, p_new_user_password_fail_count,
                        p_new_user_default_password_fail_count)


@session.stored_procedure(modifying=True)
def update_uniskaduser(p_user_id: int, p_new_user_id_prog: int, p_new_user_login: str,
                       p_new_user_fam: str,
                       p_new_user_name: str, p_new_user_id_role: int = None, p_new_user_active: bool = None,
                       p_new_user_deleted: bool = None, p_new_user_password_fail_count: int = None,
                       p_new_user_default_password_fail_count: int = None) -> User:
    return session.call('update_uniskaduser', p_user_id, p_new_user_id_prog, p_new_user_login,
                        p_new_user_fam,
                        p_new_user_name, p_new_user_id_role, p_new_user_active,
                        p_new_user_deleted, p_new_user_password_fail_count,
                        p_new_user_default_password_fail_count)


@session.stored_procedure(modifying=True)
def new_upd_uniskadrole(p_role: tuple) -> Role:
    return session.call('new_upd_uniskadrole', p_role)


@session.stored_procedure(modifying=True)
def del_restore_uniskaduser(p_user_id: int, p_deleted: bool, p_final_delete: bool) -> bool:
    return session.call('del_restore_uniskaduser', p_user_id, p_deleted, p_final_delete)


@session.stored_procedure(modifying=True)
def del_restore_uniskadrole(p_role_id: int, p_deleted: bool, p_final_delete: bool) -> bool:
    return session.call('del_restore_uniskadrole', p_role_id, p_deleted, p_final_delete)


@session.stored_procedure()
def get_xy_curve_data(p_project_id: int, curve_name: str) -> List[CurveData]:
    return session.call('get_xy_curve_data', p_project_id, curve_name, )


@session.stored_procedure(description='Получение данных полей')
def get_epure_data(test_ids: list, curve_names: list) -> List[CurveData]:
    return session.call('get_epure_data', test_ids, curve_names)


@session.stored_procedure()
def get_import_file_data_curves(p_project_id: int, ) -> List[ImportFileData]:
    return session.call('get_import_file_data_curves', p_project_id, )


@session.stored_procedure()
def get_import_file_data_curves_data(p_project_id: int, curve_names: list) -> List[ImportFileData]:
    return session.call('get_import_file_data_curves_data', p_project_id, curve_names)


@session.stored_procedure(modifying=True)
def new_update_project_from_record_with_props(p_project: tuple, p_prop_tuple: list) -> List[Project]:
    return session.call('new_update_project_from_record_with_props', p_project, p_prop_tuple)


@session.stored_procedure(modifying=True)
def new_update_project_from_record_array(p_projects: list) -> List[Project]:
    return session.call('new_update_project_from_record_array', p_projects)


@session.stored_procedure()
def get_project_data_curves(p_project_id: int) -> List[ProjectData]:
    return session.call('get_project_data_curves', p_project_id)


@session.stored_procedure()
def get_x_curve_data(p_project_id: int, curve_name: str) -> List[XCurveData]:
    return session.call('get_x_curve_data', p_project_id, curve_name, )


@session.stored_procedure()
def project_data_w_joins(p_project_data: list, ) -> List[ProjectData]:
    return session.call('project_data_w_joins', p_project_data)


@session.stored_procedure()
def import_file_data_w_joins(p_project_data: list, ) -> List[ImportFileData]:
    return session.call('import_file_data_w_joins', p_project_data)


@session.stored_procedure(modifying=True)
def del_restore_project_data_record(p_project_data: tuple, ) -> bool:
    return session.call('del_restore_project_data_record', p_project_data)


@session.stored_procedure(modifying=True)
def del_restore_project_data_array(p_project_data: list, ) -> bool:
    return session.call('del_restore_project_data_array', p_project_data)


@session.stored_procedure(modifying=True)
def del_restore_import_file_data_array(p_project_data: list, ) -> bool:
    return session.call('del_restore_import_file_data_array', p_project_data)


@session.stored_procedure(modifying=True)
def add_a_bunch_from_wd_to_p2(bunch_items: list, old_parent_id: int, new_parent_id: int) -> List[Project]:
    return session.call('add_a_bunch_from_wd_to_p2', bunch_items, old_parent_id, new_parent_id)


@session.stored_procedure(modifying=True)
def copy_tree_project_bunch(bunch_items: list, root_parent_id: int, new_root_parent_id: int) -> List[Project]:
    return session.call('copy_tree_project_bunch', bunch_items, root_parent_id,
                        new_root_parent_id)


@session.stored_procedure(modifying=False)
def get_main_folders_project_ids(p_project_id: int) -> List[int]:
    return session.call('get_main_folders_project_ids', p_project_id)


@session.stored_procedure(modifying=True)
def create_project(p_project_name: str) -> List[Project]:
    return session.call('create_project', p_project_name)


@session.stored_procedure(modifying=True)
def create_epure(p_epure_name: str, p_folder_id: int, p_param_list: str, p_oy_list: str, extra_param: str,
                 extra_param_values: str) -> List[Project]:
    return session.call('create_epure', p_epure_name, p_folder_id, p_param_list, p_oy_list, extra_param,
                        extra_param_values)


@session.stored_procedure(modifying=False)
def get_param_list_from_test_id_list(p_id_list: list) -> List[str]:
    return session.call('get_param_list_from_test_id_list', p_id_list)


@session.stored_procedure(modifying=True)
def add_project_prop_by_id(p_project_id: int, prop_name: str, prop_value: str) -> Project:
    return session.call('add_project_prop_by_id', p_project_id, prop_name, prop_value)


@session.stored_procedure(modifying=False)
def get_all_project_products(project_id: int) -> List[Project]:
    return session.call('get_all_project_products', project_id)


@session.stored_procedure(modifying=False)
def get_project_product_folder_off_the_folder(project_id: int) -> Project:
    return session.call('get_project_product_folder_off_the_folder', project_id)


@session.stored_procedure(modifying=False)
def get_project_test_params(project_id: int) -> List[ProjectData]:
    return session.call('get_project_test_params', project_id)


@session.stored_procedure(modifying=True)
def add_new_xy_graph(graph_folder_id: int, graph_name: str, x_curve: str, y_curve: str, group_by: str,
                     constraints: str) -> List[Project]:
    return session.call('add_new_xy_graph', graph_folder_id, graph_name, x_curve, y_curve, group_by, constraints)


@session.stored_procedure()
def get_settings_tree() -> List[SettingsItem]:
    return session.call('get_settings_tree')


@session.stored_procedure()
def get_user_default_values(prog_id, user_name) -> List[DefaultValue]:
    return session.call('get_user_default_values', prog_id, user_name)


@session.stored_procedure(modifying=True)
def add_link_user_role(user_id, id_role) -> bool:
    return session.call('add_link_user_role', user_id, id_role)


@session.stored_procedure(modifying=True)
def add_link_user_role_array(user_id, id_role_list) -> bool:
    return session.call('add_link_user_role_array', user_id, id_role_list)


@session.stored_procedure(modifying=True)
def unlink_user_role_array(user_id, id_role_list) -> bool:
    return session.call('unlink_user_role_array', user_id, id_role_list)


@session.stored_procedure(modifying=True)
def new_user_formula(p_user_formula: tuple) -> UserFormula:
    return session.call('new_user_formula', p_user_formula)


@session.stored_procedure(modifying=True)
def remove_user_formula(p_user_formula: tuple) -> bool:
    return session.call('remove_user_formula', p_user_formula)


@session.stored_procedure(modifying=True)
def set_point_prop(p_project_id: int,
                   p_curve_name: str,
                   p_date_time_izm: datetime.datetime,
                   p_prop_name: str,
                   p_prop_value: str) -> bool:
    return session.call('set_point_prop', p_project_id, p_curve_name, p_date_time_izm, p_prop_name, p_prop_value)


@session.stored_procedure()
def get_user_formula_list() -> List[UserFormula]:
    return session.call('get_user_formula_list')


@session.stored_procedure(modifying=True)
def pass_project_to_another_user(bunch_items: list,
                                 graph_id_list: list,
                                 root_id_up: int,
                                 user_id: int) -> List[Project]:
    return session.call('pass_project_to_another_user', bunch_items, graph_id_list, root_id_up,
                        user_id)


@session.stored_procedure(modifying=True)
def copy_project_test_table(p_project_id: int,
                            p_new_project_id: int) -> bool:
    return session.call('copy_project_test_table', p_project_id, p_new_project_id)


@session.stored_procedure(modifying=False, description='Получение данных третьего параметра')
def get_x_curves(p_project_id: int, test_id_list: list,
                 curve_name: str) -> List[ProjectData]:
    return session.call('get_x_curves', p_project_id, test_id_list, curve_name)


@session.stored_procedure(modifying=False)
def get_x_curves_array(p_project_id: int, test_id_list: list,
                       curve_name: list) -> List[ProjectData]:
    return session.call('get_x_curves_array', p_project_id, test_id_list, curve_name)


@session.stored_procedure(modifying=True)
def delete_plot_template(p_plot_template: tuple) -> bool:
    return session.call('delete_plot_template', p_plot_template)


@session.stored_procedure(modifying=True)
def new_upd_plot_template(p_plot_template: tuple) -> List[PlotTemplate]:
    return session.call('new_upd_plot_template', p_plot_template)


@session.stored_procedure(modifying=True)
def new_upd_custom_curve(p_custom_curve: tuple) -> CustomCurve:
    return session.call('new_upd_custom_curve', p_custom_curve)


@session.stored_procedure(modifying=True)
def remove_custom_curve(p_custom_curve_id: int) -> bool:
    return session.call('remove_custom_curve', p_custom_curve_id)


@session.stored_procedure(modifying=False)
def get_custom_curves(p_graph_project_id: int) -> List[CustomCurve]:
    return session.call('get_custom_curves', p_graph_project_id)


@session.stored_procedure(modifying=False)
def get_user_plot_templates() -> List[PlotTemplate]:
    return session.call('get_user_plot_templates')


@session.stored_procedure(modifying=True)
def add_new_xy_graphs_from_template(p_graph_folder_id: int, p_plot_template: int) -> List[Project]:
    return session.call('add_new_xy_graphs_from_template', p_graph_folder_id, p_plot_template)


@session.stored_procedure(modifying=False)
def get_params_values(p_param_list: list, project_id: int) -> List[ParamValues]:
    return session.call('get_params_values', p_param_list, project_id)


@session.stored_procedure(modifying=True)
def set_param_secret(p_param_name: str, p_flag_secret: bool) -> bool:
    return session.call('set_param_secret', p_param_name, p_flag_secret)


@session.stored_procedure(modifying=True)
def grant_role_secret_access(p_role_id: int, p_flag_secret: bool) -> bool:
    return session.call('grant_role_secret_access', p_role_id, p_flag_secret)


@timing_decorator
@session.stored_procedure(modifying=False)
def get_session_role_secret_grantness() -> bool:
    return session.call('get_session_role_secret_grantness')
