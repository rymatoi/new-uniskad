from app.feature_flags import is_feature_enabled


def test_table_view_feature_flags_are_opt_in():
    assert not is_feature_enabled('UNISKAD_WORK_DATA_TABLE_VIEW', {})
    assert not is_feature_enabled('UNISKAD_PROJECT_TABLE_VIEW', {})
    assert is_feature_enabled('UNISKAD_WORK_DATA_TABLE_VIEW', {'UNISKAD_WORK_DATA_TABLE_VIEW': '1'})
    assert is_feature_enabled('UNISKAD_PROJECT_TABLE_VIEW', {'UNISKAD_PROJECT_TABLE_VIEW': 'true'})
