-- Create user schema for testing
CREATE SCHEMA test_schema;
SET search_path TO test_schema, public;

-- Create a base table with a primary key
CREATE TABLE test_tbl (
    id INT PRIMARY KEY,
    name VARCHAR(50),
    age INT
);

-- Create a base table without a primary key
CREATE TABLE test_tbl_no_pk (
    id INT,
    description TEXT
);

-- Insert data into base tables
INSERT INTO test_tbl (id, name, age) VALUES
(1, 'Alice', 30), (2, 'Bob', 25), (3, 'Carol', 35);
INSERT INTO test_tbl_no_pk (id, description) VALUES
(1, 'First description'), (2, 'Second description');

-- Create a simple view
CREATE VIEW view_test_1 AS
SELECT * FROM test_tbl;

-- Create a view with a WHERE clause
CREATE VIEW view_test_2 AS
SELECT * FROM test_tbl WHERE age > 30;

-- Create or replace a view
CREATE OR REPLACE VIEW view_test_1 AS
SELECT id, name, age FROM test_tbl WHERE age > 25;

-- Create a recursive view
CREATE OR REPLACE VIEW view_recursive AS 
WITH RECURSIVE cte AS (
    SELECT 1 AS n
    UNION ALL
    SELECT n + 1 FROM cte WHERE n < 5
)
SELECT * FROM cte;

-- Create a view with options
CREATE VIEW view_with_options WITH (security_barrier=true) AS
SELECT * FROM test_tbl;

-- Create a view with check option
CREATE VIEW view_with_check_option AS 
SELECT * FROM test_tbl WHERE age > 25 WITH LOCAL CHECK OPTION;

------------------------------
-- Create a materialized view
-------------------------------
CREATE MATERIALIZED VIEW mv_test_view AS
SELECT id, name, age FROM test_tbl WHERE age > 30;

-- Create a materialized view with "WITH NO DATA"
CREATE MATERIALIZED VIEW mv_test_view_nodata AS
SELECT id, name, age FROM test_tbl WHERE age > 30 WITH NO DATA;

-- Refresh the materialized view
REFRESH MATERIALIZED VIEW mv_test_view_nodata;

-- Create a materialized view with specific column names
CREATE MATERIALIZED VIEW mv_test_view_colnames (person_id, person_name, person_age) AS
SELECT id, name, age FROM test_tbl WHERE age > 30;

-- Create a materialized view using a specific method
CREATE MATERIALIZED VIEW mv_test_view_method AS 
SELECT id, name, age FROM test_tbl WHERE age > 30;

-- Create a materialized view with storage parameters
CREATE MATERIALIZED VIEW mv_test_view_storage WITH (fillfactor = 70) AS
SELECT id, name, age FROM test_tbl WHERE age > 30;

-- Create a materialized view in a specific tablespace
CREATE MATERIALIZED VIEW mv_test_view_tablespace TABLESPACE pg_default AS 
SELECT id, name, age FROM test_tbl WHERE age > 30;

-- Reset search_path to default
RESET search_path;

-- Create a simple view in the default schema
CREATE VIEW public.view_test_default AS
SELECT * FROM test_schema.test_tbl_no_pk;

-- Create or replace a view in the default schema
CREATE OR REPLACE VIEW public.view_test_default AS
SELECT id, description FROM test_schema.test_tbl_no_pk WHERE id > 1;

--creating views and materialized views that depend on other views
-- Create a view that depends on another view
CREATE VIEW test_schema.view_depends_on_default AS
SELECT id, description FROM public.view_test_default WHERE id > 1;

-- Create a materialized view that depends on a view in another schema
CREATE MATERIALIZED VIEW public.mv_depends_on_test_schema AS
SELECT id, name, age FROM test_schema.mv_test_view;

-- Create a new view that depends on the materialized view public.mv_depends_on_test_schema
CREATE VIEW public.view_depends_on_mv AS
SELECT id, name FROM public.mv_depends_on_test_schema WHERE age > 30;

-- Create a new materialized view that depends on a regular view
CREATE MATERIALIZED VIEW public.mv_depends_on_mv AS
SELECT id, name FROM public.view_depends_on_mv;

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
