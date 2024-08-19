-- Prepared statement for spock.tables to list tables and associated indexes
PREPARE spocktab AS SELECT nspname, relname, set_name FROM spock.tables WHERE relname LIKE '%' || $1 || '%' ORDER BY relid;


-- Turn on the allow_ddl_from_functions GUC
ALTER SYSTEM SET spock.allow_ddl_from_functions = on;
SELECT pg_reload_conf();
SELECT pg_sleep(0.5);
SHOW spock.allow_ddl_from_functions;

-- Create simple tables
CREATE TABLE tab1_proc_on (id INT PRIMARY KEY, col1 TEXT, col2 INT);
CREATE TABLE tab2_func_on (id INT PRIMARY KEY, col1 TEXT, col2 INT, col3 TEXT, col4 INT, col5 TEXT, col6 INT, col7 TEXT, col8 INT);
-- Create tables within anonymous blocks
DO $$
BEGIN
  EXECUTE 'CREATE TABLE tab3_anon_on (id INT, col1 TEXT, col2 INT)';
  EXECUTE 'CREATE TABLE tab6_anon_off (id INT PRIMARY KEY, col1 TEXT, col2 INT)';
END
$$;
CREATE TABLE tab4_proc_off (id INT PRIMARY KEY, col1 TEXT, col2 INT);
CREATE TABLE tab5_func_off (id INT PRIMARY KEY, col1 TEXT, col2 INT, col3 TEXT, col4 INT, col5 TEXT, col6 INT, col7 TEXT, col8 INT);

-- Insert sample data
INSERT INTO tab1_proc_on (id, col1, col2) VALUES (1, 'data1', 100);
INSERT INTO tab2_func_on (id, col1, col2, col3, col4, col5, col6, col7, col8) VALUES (1, 'data2', 200, 'data3', 300, 'data4', 400, 'data5', 500);
INSERT INTO tab3_anon_on (id, col1, col2) VALUES (1, 'data1', 100);
INSERT INTO tab4_proc_off (id, col1, col2) VALUES (1, 'data1', 100);
INSERT INTO tab5_func_off (id, col1, col2, col3, col4, col5, col6, col7, col8) VALUES (1, 'data2', 200, 'data3', 300, 'data4', 400, 'data5', 500);
INSERT INTO tab6_anon_off (id, col1, col2) VALUES (1, 'data1', 100);

-- Create procedure that internally executes a DDL to add columns dynamically to the passed table
CREATE OR REPLACE PROCEDURE add_column_to_table_proc(
    table_name VARCHAR(50),
    varname VARCHAR(50),
    vartype VARCHAR(50),
    IN OUT success BOOLEAN
) AS $$
BEGIN
    EXECUTE 'ALTER TABLE ' || table_name || ' ADD COLUMN ' || varname || ' ' || vartype;
    success := true;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Error: %', SQLERRM;
        success := false;
END;
$$ LANGUAGE plpgsql;

-- Create function that internally exdcutes a DDL to drop columns dynamically from the passed table
CREATE OR REPLACE FUNCTION remove_column_from_table(
    table_name VARCHAR(50),
    column_name VARCHAR(50)
) RETURNS BOOLEAN AS $$
BEGIN
    EXECUTE 'ALTER TABLE ' || table_name || ' DROP COLUMN ' || column_name;
    RETURN TRUE;
EXCEPTION
    WHEN OTHERS THEN
        RETURN FALSE;
END;
$$ LANGUAGE plpgsql;

-- Create the tab_emp table
CREATE TABLE tab_emp (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    salary NUMERIC
);

-- Create a trigger function
CREATE OR REPLACE FUNCTION employee_insert_trigger()
RETURNS TRIGGER AS $$
BEGIN
    EXECUTE 'CREATE SCHEMA ' || NEW.name;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create the trigger to execute the function after an insert
CREATE TRIGGER employee_insert_trigger
AFTER INSERT
ON tab_emp
FOR EACH ROW
EXECUTE FUNCTION employee_insert_trigger();

EXECUTE spocktab('tab'); 

-- Add a primary key to the table tab3 within an anonymous block
DO $$
BEGIN
  EXECUTE 'ALTER TABLE tab3_anon_on ADD PRIMARY KEY (id)';
END
$$;


-- Execute the procedure to add columns
CALL add_column_to_table_proc('tab1_proc_on', 'new_col1', 'CHAR', true);
CALL add_column_to_table_proc('tab1_proc_on', 'new_col2', 'BOOL', true);

-- Execute the function to drop columns
SELECT remove_column_from_table('tab2_func_on', 'col3');
SELECT remove_column_from_table('tab2_func_on', 'col5');

-- Trigger DDL execution via trigger, that should create a schema named john and auto replicate it
INSERT INTO tab_emp (id, name, salary) VALUES (1, 'John', 50000);

EXECUTE spocktab('tab'); 

------
-- Turning allow_ddl_from_functions GUC off
------

-- Turn off the allow_ddl_from_functions GUC
ALTER SYSTEM SET spock.allow_ddl_from_functions = off;
SELECT pg_reload_conf();
SELECT pg_sleep(0.5);
SHOW spock.allow_ddl_from_functions;

-- Run anonymous block to create tab7
DO $$
BEGIN
  EXECUTE 'CREATE TABLE tab7_anon_off (id INT, col1 TEXT, col2 INT)';
  EXECUTE 'ALTER TABLE tab6_anon_off DROP COLUMN id';
END
$$;

-- Execute the procedure to add columns
CALL add_column_to_table_proc('tab4_proc_off', 'new_col1', 'CHAR', true);
CALL add_column_to_table_proc('tab4_proc_off', 'new_col2', 'BOOL', true);

-- Execute the function to drop columns
SELECT remove_column_from_table('tab5_func_off', 'col3');
SELECT remove_column_from_table('tab5_func_off', 'col5');

-- Trigger DDL execution via trigger
INSERT INTO tab_emp (id, name, salary) VALUES (2, 'Alice', 60000);

-- Validate table structures and schemas
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