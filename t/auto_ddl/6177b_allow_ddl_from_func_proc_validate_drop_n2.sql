-- Prepared statement for spock.tables to list tables and associated indexes
PREPARE spocktab AS SELECT nspname, relname, set_name FROM spock.tables WHERE relname LIKE '%' || $1 || '%' ORDER BY relid;

-- Turn on the allow_ddl_from_functions GUC
ALTER SYSTEM SET spock.allow_ddl_from_functions = on;
SELECT pg_reload_conf();
SELECT pg_sleep(0.5);
SHOW spock.allow_ddl_from_functions;

-- Validate replicated functions, procedures, tables
\df add_column*
\df remove_column*
\df employee_insert_trigger
\d+ tab1_proc_on
\d+ tab2_func_on
\d+ tab3_anon_on
\d+ tab4_proc_off
\d+ tab5_func_off
\d+ tab6_anon_off
\d+ tab7_anon_off
\d+ tab_emp
\dn john
\dn alice
EXECUTE spocktab('tab'); 
-- Drop tables 
DO $$
BEGIN
  EXECUTE 'DROP TABLE tab1_proc_on';
  EXECUTE 'DROP TABLE tab2_func_on';
  EXECUTE 'DROP TABLE tab3_anon_on';
  EXECUTE 'DROP TABLE tab4_proc_off';
  EXECUTE 'DROP TABLE tab5_func_off';
  EXECUTE 'DROP TABLE tab6_anon_off';
  EXECUTE 'DROP TABLE tab_emp CASCADE';
  EXECUTE 'DROP PROCEDURE add_column_to_table_proc';
  EXECUTE 'DROP FUNCTION remove_column_from_table';
  EXECUTE 'DROP FUNCTION employee_insert_trigger';
  EXECUTE 'DROP SCHEMA john';
END
$$;

DO $$
BEGIN
  EXECUTE 'DROP TABLE tab7_anon_off'; --should not exist
END
$$;
--should error out
DROP SCHEMA alice;