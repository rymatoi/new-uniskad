from pathlib import Path


SQL = (Path(__file__).parents[1] / 'db/sql/import_workdata_file_curves_to_project.sql').read_text()


def test_db_import_sql_copies_legacy_keys_properties_and_validates_columns():
    assert SQL.index('CREATE OR REPLACE FUNCTION sc_ref.get_project_data_import_stats') < SQL.index('CREATE OR REPLACE FUNCTION sc_ref.import_workdata_file_curves_to_project')
    assert "AS row_type_count" in SQL
    assert "AS row_npp_count" in SQL
    assert "AS column_type_count" in SQL
    assert "AS column_npp_count" in SQL
    assert "AS value_count" in SQL
    assert 'FROM sc_ref.get_import_file_data2(p_id_excel_file, p_file_version)' in SQL
    assert 'selected_names AS MATERIALIZED' in SQL
    assert 'SELECT DISTINCT unnest(p_curve_names)::varchar AS excel_param_name' in SQL
    assert 'raw_source_data AS MATERIALIZED' in SQL
    assert 'source_data AS MATERIALIZED' in SQL
    assert 'WHERE data.excel_param_name IS NULL' in SQL
    assert "data.param_prop_name IS DISTINCT FROM 'row_npp'" in SQL
    assert 'row_type.excel_param_name IS NOT DISTINCT FROM data.excel_param_name' in SQL
    assert "row_type.param_prop_name = 'type'" in SQL
    assert "row_type.prop_value = 'row'" in SQL
    assert 'OR EXISTS (' in SQL
    assert 'FROM selected_names sn' in SQL
    assert 'sn.excel_param_name = data.excel_param_name' in SQL
    assert 'data.excel_param_name = ANY(p_curve_names)' not in SQL
    assert "excel_param_name, 'name', NULL" in SQL
    assert "excel_param_name, 'is_secret', NULL" in SQL
    assert "excel_param_name, 'eizm_short', NULL" in SQL
    assert 'date_time_izm' in SQL
    assert 'zamer_n' in SQL
    assert 'rejim_zamer' in SQL
    assert 'npp' in SQL
    assert 'v_stats.column_type_count = 0 OR v_stats.column_npp_count = 0' in SQL
    assert 'v_stats.column_type_count <> v_stats.column_npp_count' in SQL
    assert 'v_stats.row_type_count <> v_stats.row_npp_count' in SQL
