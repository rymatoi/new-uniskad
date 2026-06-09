from pathlib import Path


SQL = (Path(__file__).parents[1] / 'db/sql/import_workdata_file_curves_to_project.sql').read_text()


def test_db_import_sql_copies_legacy_keys_properties_and_validates_columns():
    assert 'FROM sc_ref.get_import_file_data2(p_id_excel_file, p_file_version)' in SQL
    assert 'data.excel_param_name = ANY(p_curve_names)' in SQL
    assert 'OR data.excel_param_name IS NULL' in SQL
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
