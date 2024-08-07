-- Validate replicated functions, procedures, tables
-- No objects sould exist except tab7
\df add_column*
\df remove_column*
\df employee_insert_trigger
\d tab1_proc_on
\d tab2_func_on
\d tab3_anon_on
\d tab4_proc_off
\d tab5_func_off
\d tab6_anon_off
\d tab7_anon_off
\d tab_emp
\dn john
\dn alice

-- Turn off the allow_ddl_from_functions GUC so that these drops are not auto replicated
ALTER SYSTEM SET spock.allow_ddl_from_functions = off;
SELECT pg_reload_conf();
SELECT pg_sleep(0.5);
SHOW spock.allow_ddl_from_functions;

-- Drop tables
DO $$
BEGIN
  EXECUTE 'DROP TABLE tab7_anon_off';
  EXECUTE 'DROP SCHEMA alice';
END
$$;

-- Turn on the allow_ddl_from_functions GUC
ALTER SYSTEM SET spock.allow_ddl_from_functions = on;
SELECT pg_reload_conf();
