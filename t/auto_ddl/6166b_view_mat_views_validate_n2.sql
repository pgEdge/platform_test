-- Validations on n2
-- Validate structure and data in views

-- Validations
-- Validate structure and data in views
-- Validation for view_test_1
\d+ test_schema.view_test_1
-- Expect 2 rows: Alice, Carol
SELECT * FROM test_schema.view_test_1 ORDER BY id; 

-- Validation for view_test_2
\d+ test_schema.view_test_2
-- Expect 1 row: Carol
SELECT * FROM test_schema.view_test_2 ORDER BY id; 

-- Validation for view_recursive
\d+ test_schema.view_recursive
-- Expect 5 rows: 1, 2, 3, 4, 5
SELECT * FROM test_schema.view_recursive ORDER BY n; 

-- Validation for view_with_options
\d+ test_schema.view_with_options
-- Expect 3 rows: Alice, Bob, Carol
SELECT * FROM test_schema.view_with_options ORDER BY id; 

-- Validation for view_with_check_option
\d+ test_schema.view_with_check_option
-- Expect 2 rows: Alice, Carol
SELECT * FROM test_schema.view_with_check_option ORDER BY id; 

-- Validation for mv_test_view
\d+ test_schema.mv_test_view
-- Expect 1 row: Carol
SELECT * FROM test_schema.mv_test_view ORDER BY id; 

-- Validation for mv_test_view_nodata
\d+ test_schema.mv_test_view_nodata
-- Expect 1 row: Carol
SELECT * FROM test_schema.mv_test_view_nodata ORDER BY id; 

-- Validation for mv_test_view_colnames
\d+ test_schema.mv_test_view_colnames
-- Expect 1 row: Carol
SELECT * FROM test_schema.mv_test_view_colnames ORDER BY person_id; 

-- Validation for mv_test_view_method
\d+ test_schema.mv_test_view_method
-- Expect 1 row: Carol
SELECT * FROM test_schema.mv_test_view_method ORDER BY id; 

-- Validation for mv_test_view_storage
\d+ test_schema.mv_test_view_storage
-- Expect 1 row: Carol
SELECT * FROM test_schema.mv_test_view_storage ORDER BY id; 

-- Validation for mv_test_view_tablespace
\d+ test_schema.mv_test_view_tablespace
-- Expect 1 row: Carol
SELECT * FROM test_schema.mv_test_view_tablespace ORDER BY id; 

-- Validation for view_test_default
\d+ public.view_test_default
-- Expect 1 row: Second description
SELECT * FROM public.view_test_default ORDER BY id; 

-- Validation for view_depends_on_default
\d+ test_schema.view_depends_on_default
-- Expect 1 row: Second description
SELECT * FROM test_schema.view_depends_on_default ORDER BY id; 

-- Validation for mv_depends_on_test_schema
\d+ public.mv_depends_on_test_schema
-- Expect 1 row: Carol
SELECT * FROM public.mv_depends_on_test_schema ORDER BY id; 

-- Validation for view_depends_on_mv
\d+ public.view_depends_on_mv
-- Expect 1 row: Carol
SELECT * FROM public.view_depends_on_mv ORDER BY id; 

-- Validation for mv_depends_on_mv
\d+ public.mv_depends_on_mv
-- Expect 1 row: Carol
SELECT * FROM public.mv_depends_on_mv ORDER BY id; 

-- Drop views and materialized views

-- Drop the materialized view in the public schema that depends on a view in the test_schema
DROP MATERIALIZED VIEW IF EXISTS public.mv_depends_on_test_schema CASCADE;

-- Drop the view in the test_schema that depends on another view in the public schema
DROP VIEW test_schema.view_depends_on_default CASCADE;

-- Drop all other views and materialized views
DROP VIEW IF EXISTS test_schema.view_test_1, 
                          test_schema.view_test_2, 
                          test_schema.view_recursive, 
                          test_schema.view_with_options, 
                          test_schema.view_with_check_option, 
                          public.view_test_default CASCADE;

DROP MATERIALIZED VIEW IF EXISTS test_schema.mv_test_view, 
                                test_schema.mv_test_view_colnames, 
                                test_schema.mv_test_view_method, 
                                test_schema.mv_test_view_storage, 
                                test_schema.mv_test_view_tablespace CASCADE;

-- Drop the tables used for views and materialized views
DROP TABLE IF EXISTS test_schema.test_tbl CASCADE;
DROP TABLE IF EXISTS test_schema.test_tbl_no_pk CASCADE;

-- Drop the schema
DROP SCHEMA test_schema CASCADE;
