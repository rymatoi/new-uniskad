PROJECT_TABLE = (
    'id_record',
    'project_id',
    'project_id_up',
    'project_type',
    'project_prop',
    'project_prop_value',
    'project_author',
    'project_owner',
    'creation_date',
    'npp',
    'deleted'
)

PROJECT_DATA = (
    'id_record',
    'project_id',
    'id_excel_file',
    'file_version',
    'excel_param_name',
    'param_prop_name',
    'date_time_izm',
    'zamer_n',
    'rejim_zamer',
    'prop_value',
    'deleted',
    'npp',
)

PRODUCT = (
    'id_record',
    'id_prod',
    'id_up_prod',
    'id_ptype',
    'prod_prop',
    'prod_prop_value',
    'creation_date',
    'npp',
    'deleted'
)

IMPORT_FILE_DATA = (
    'id_record',
    'id_excel_file',
    'file_version',
    'param_prop_name',
    'date_time_izm',
    'zamer_n',
    'rejim_zamer',
    'prop_value',
    'deleted',
    'npp',
    'id_name'
)

SPRAV_NAMES = (
    'id_name',
    'param_name',
    'param_id_eizm',
    'flag_synonim',
    'flag_permanent',
    'param_descr',
    'id_permanent_name',
    'accuracy'
)

USER_FORMULA = (
    'id_record',
    'id_up',
    'param_formula',
    'x_vals',
    'user_id',
    'id',
    'prop_name',
    'prop_value'
)
