-- Prepared statement for spock.tables to list tables and associated indexes
PREPARE spocktab AS SELECT nspname, relname, set_name FROM spock.tables WHERE relname LIKE '%' || $1 || '%' ORDER BY relid;

-- Validate and drop indexes on n2

-- Validate indexes on product_catalog
\di *product_catalog_*
\d product_catalog
-- Validate specific index
SELECT * FROM product_catalog WHERE product_id = 2; -- Expect 1 row with product_id = 2

-- Validate indexes on employee_directory
\di *_emp_*
\d employee_directory
-- Validate specific index
SELECT * FROM employee_directory WHERE emp_email = 'bob@example.com'; -- Expect 1 row with emp_email = 'bob@example.com'

-- Validate indexes on sales_data
\di *sales*
\d sales_data
-- Validate specific index
SELECT * FROM sales_data WHERE sale_amount * 2 = 300.0; -- Expect 1 row with sale_amount = 150.0

-- Validate concurrently created indexes on concurrent_idx_tbl, should not exist as they weren't replicated
\di *concurrent*
\d concurrent_idx_tbl
-- Validate specific index
SELECT * FROM concurrent_idx_tbl WHERE name = 'Second'; -- Expect 1 row with name = 'Second'

-- Drop indexes on product_catalog
DROP INDEX btree_product_catalog_idx;
DROP INDEX hash_product_catalog_idx;
DROP INDEX brin_product_catalog_idx;
DROP INDEX gin_product_catalog_idx;
DROP INDEX gist_product_catalog_idx;
DROP INDEX spgist_product_catalog_idx;

-- Drop indexes on employee_directory
DROP INDEX unique_emp_id_idx;
DROP INDEX unique_emp_email_idx;

-- Drop indexes on sales_data
DROP INDEX func_sales_amount_idx;
DROP INDEX renamed_sales_region_idx;
DROP INDEX conditional_sales_idx;
DROP INDEX partial_sales_idx;

-- Drop concurrently created indexes on concurrent_idx_tbl
DROP INDEX CONCURRENTLY concurrent_idx_tbl_name_idx; --error (since this did not replicate to n2)
DROP INDEX CONCURRENTLY concurrent_unique_idx_tbl_id_idx; --error (since this did not replicate to n2)

-- Validate replication sets for primary key-related tables
EXECUTE spocktab('product_catalog'); -- Expect product_catalog in default set
EXECUTE spocktab('employee_directory'); -- Expect employee_directory in default set
EXECUTE spocktab('sales_data'); -- Expect sales_data in default set
EXECUTE spocktab('concurrent_idx_tbl'); -- Expect sales_data in default set

DROP TABLE product_catalog CASCADE;
DROP TABLE sales_data CASCADE;
DROP TABLE employee_directory CASCADE;
DROP TABLE concurrent_idx_tbl CASCADE;