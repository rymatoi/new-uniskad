-- Deploy this file after the application update.  The import deliberately uses
-- get_import_file_data2 so its source rows are identical to the legacy Python
-- fallback (including row/column/cell formatting properties and lookup names).
CREATE OR REPLACE FUNCTION sc_ref.get_project_data_import_stats(p_project_id integer)
RETURNS TABLE (
    row_type_count bigint,
    row_npp_count bigint,
    column_type_count bigint,
    column_npp_count bigint,
    value_count bigint
)
LANGUAGE sql
STABLE
AS $function$
    SELECT
        count(*) FILTER (WHERE param_prop_name = 'type' AND prop_value = 'row'),
        count(*) FILTER (WHERE param_prop_name = 'row_npp'),
        count(*) FILTER (WHERE param_prop_name = 'type' AND prop_value = 'column'),
        count(*) FILTER (WHERE param_prop_name = 'column_npp'),
        count(*) FILTER (WHERE param_prop_name = 'value')
    FROM sc_ref.project_data
    WHERE project_id = p_project_id AND deleted = false;
$function$;

CREATE OR REPLACE FUNCTION sc_ref.import_workdata_file_curves_to_project(
    p_target_project_id integer,
    p_id_excel_file integer,
    p_file_version integer,
    p_curve_names varchar[]
)
RETURNS integer
LANGUAGE plpgsql
AS $function$
DECLARE
    v_inserted_rows integer;
    v_stats record;
BEGIN
    WITH selected_names AS MATERIALIZED (
        SELECT DISTINCT unnest(p_curve_names)::varchar AS excel_param_name
    ), source_data AS MATERIALIZED (
        SELECT data.*
        FROM sc_ref.get_import_file_data2(p_id_excel_file, p_file_version) AS data
        WHERE data.excel_param_name IS NULL
           OR EXISTS (
               SELECT 1
               FROM selected_names sn
               WHERE sn.excel_param_name = data.excel_param_name
           )
    ), project_rows AS (
        -- Copy every selected source record unchanged.  Null excel_param_name +
        -- non-null date_time_izm is the ProjectTableModel column key; selected
        -- names + null dates are row keys; both values form cell keys.
        SELECT
            p_target_project_id AS project_id,
            id_excel_file,
            file_version,
            excel_param_name,
            param_prop_name,
            date_time_izm,
            zamer_n,
            rejim_zamer,
            prop_value,
            false AS deleted,
            npp
        FROM source_data

        UNION ALL

        -- These are the extra records made by the legacy Python loop whenever
        -- it encounters a row type record.
        SELECT p_target_project_id, id_excel_file, file_version,
               excel_param_name, 'name', NULL, zamer_n, rejim_zamer,
               excel_param_name, false, npp
        FROM source_data
        WHERE param_prop_name = 'type' AND prop_value = 'row'

        UNION ALL

        SELECT p_target_project_id, id_excel_file, file_version,
               excel_param_name, 'is_secret', NULL, zamer_n, rejim_zamer,
               is_secret::text, false, npp
        FROM source_data
        WHERE param_prop_name = 'type' AND prop_value = 'row' AND is_secret

        UNION ALL

        SELECT p_target_project_id, id_excel_file, file_version,
               excel_param_name, 'eizm_short', NULL, zamer_n, rejim_zamer,
               COALESCE(eizm_short::text, 'None'), false, npp
        FROM source_data
        WHERE param_prop_name = 'type' AND prop_value = 'row'
    )
    INSERT INTO sc_ref.project_data (
        project_id, id_excel_file, file_version, excel_param_name,
        param_prop_name, date_time_izm, zamer_n, rejim_zamer, prop_value,
        deleted, npp
    )
    SELECT * FROM project_rows;

    GET DIAGNOSTICS v_inserted_rows = ROW_COUNT;

    SELECT * INTO v_stats
    FROM sc_ref.get_project_data_import_stats(p_target_project_id);

    -- Raise inside this statement so PostgreSQL rolls the malformed import back
    -- before the application invokes the legacy fallback.
    IF v_inserted_rows > 0 AND (
           v_stats.column_type_count = 0 OR v_stats.column_npp_count = 0 OR
           v_stats.column_type_count <> v_stats.column_npp_count OR
           v_stats.row_type_count <> v_stats.row_npp_count
       ) THEN
        RAISE EXCEPTION
            'WorkData import produced invalid ProjectData metadata for project %: row_type_count=%, row_npp_count=%, column_type_count=%, column_npp_count=%',
            p_target_project_id, v_stats.row_type_count, v_stats.row_npp_count,
            v_stats.column_type_count, v_stats.column_npp_count;
    END IF;

    RETURN v_inserted_rows;
END;
$function$;
