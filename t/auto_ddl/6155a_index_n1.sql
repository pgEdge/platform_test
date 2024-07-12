-- Prepared statement for spock.tables to list tables and associated indexes
PREPARE spocktab AS SELECT nspname, relname, set_name FROM spock.tables WHERE relname LIKE '%' || $1 || '%' ORDER BY relid;

-----------------------------
-- INDEX tests
-----------------------------

-- Create a table for different types of indexes
CREATE TABLE product_catalog (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(100),
    product_tags TEXT[],
    location POINT,
    price DECIMAL
);

INSERT INTO product_catalog (product_id, product_name, product_tags, location, price)
VALUES 
    (1, 'Laptop', ARRAY['Electronics', 'Computers'], POINT(1, 1), 999.99),
    (2, 'Smartphone', ARRAY['Electronics', 'Mobile'], POINT(2, 2), 599.99),
    (3, 'Tablet', ARRAY['Electronics', 'Computers'], POINT(3, 3), 399.99);

-- Create various types of indexes
CREATE INDEX btree_product_catalog_idx ON product_catalog USING btree (product_id);
CREATE INDEX hash_product_catalog_idx ON product_catalog USING hash (product_name);
CREATE INDEX brin_product_catalog_idx ON product_catalog USING brin (price);
CREATE INDEX gin_product_catalog_idx ON product_catalog USING gin (product_tags);
CREATE INDEX gist_product_catalog_idx ON product_catalog USING gist (location);
CREATE INDEX spgist_product_catalog_idx ON product_catalog USING spgist (location);

-- Validate indexes
\di *product_catalog_*

\d product_catalog

-- Create a table with unique indexes
CREATE TABLE employee_directory (
    emp_id INT PRIMARY KEY,
    emp_name VARCHAR(100),
    emp_email VARCHAR(100)
);

INSERT INTO employee_directory (emp_id, emp_name, emp_email)
VALUES 
    (1, 'Alice', 'alice@example.com'),
    (2, 'Bob', 'bob@example.com'),
    (3, 'Charlie', 'charlie@example.com');

-- Create unique indexes with different options
CREATE UNIQUE INDEX unique_emp_id_idx ON employee_directory (emp_id) NULLS DISTINCT;
CREATE UNIQUE INDEX unique_emp_email_idx ON employee_directory (emp_email) NULLS NOT DISTINCT;

-- Validate indexes
\di *_emp_*

\d employee_directory

-- Create a table for functional indexes
CREATE TABLE sales_data (
    sale_id INT PRIMARY KEY,
    sale_date DATE,
    sale_amount DECIMAL,
    sale_region VARCHAR(50)
);

INSERT INTO sales_data (sale_id, sale_date, sale_amount, sale_region)
VALUES 
    (1, '2023-01-01', 100.0, 'North'),
    (2, '2023-01-02', 200.0, 'South'),
    (3, '2023-01-03', 150.0, 'East'),
    (4, '2023-01-04', 250.0, 'West');

-- Create functional index
CREATE UNIQUE INDEX func_sales_amount_idx ON sales_data ((sale_amount * 2));

-- Validate indexes
\di *sales_*

-- Altering Indexes
-- Create an index to alter
CREATE INDEX alter_sales_region_idx ON sales_data (sale_region);

-- Validate indexes
\di *sales*

-- Alter the index to rename it
ALTER INDEX alter_sales_region_idx RENAME TO renamed_sales_region_idx;

-- Create a conditional index
CREATE INDEX conditional_sales_idx ON sales_data (sale_amount) WHERE sale_amount > 150;

-- Create a index
CREATE INDEX partial_sales_idx ON sales_data (sale_date) INCLUDE (sale_region);

-- Validate  index
\di *sales*

\d sales_data

-- Create a table for concurrently created indexes
CREATE TABLE concurrent_idx_tbl (
    id INT,
    name VARCHAR(100)
);

INSERT INTO concurrent_idx_tbl (id, name)
VALUES 
    (1, 'First'),
    (2, 'Second'),
    (3, 'Third');

-- Create indexes concurrently, should only be created locally and will not replicate
CREATE INDEX CONCURRENTLY concurrent_idx_tbl_name_idx ON concurrent_idx_tbl (name);
CREATE UNIQUE INDEX CONCURRENTLY concurrent_unique_idx_tbl_id_idx ON concurrent_idx_tbl (id);

-- Validate concurrently created indexes
\di *concurrent*

\d concurrent_idx_tbl

-- DML to verify index usage
SELECT * FROM product_catalog WHERE product_id = 2;
SELECT * FROM employee_directory WHERE emp_email = 'bob@example.com';
SELECT * FROM sales_data WHERE sale_amount * 2 = 300.0;
SELECT * FROM sales_data WHERE sale_amount > 150;
SELECT * FROM concurrent_idx_tbl WHERE name = 'Second';

-- Validate replication sets for primary key-related tables
EXECUTE spocktab('product_catalog'); -- Expect product_catalog in default set
EXECUTE spocktab('employee_directory'); -- Expect employee_directory in default set
EXECUTE spocktab('sales_data'); -- Expect sales_data in default set
EXECUTE spocktab('concurrent_idx_tbl'); -- Expect sales_data in default set
