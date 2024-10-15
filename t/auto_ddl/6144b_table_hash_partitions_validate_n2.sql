--This file will run on n2 and validate all the replicated tables data, structure and replication sets they're in
-- Prepared statement for spock.tables to list parent and child tables as parent table name will be contained in partition name
PREPARE spocktab AS SELECT nspname, relname, set_name FROM spock.tables WHERE relname LIKE '%' || $1 || '%' ORDER BY relid;

-- Validate structure and data after adding new partition
\d sales_hash_1
\d sales_hash_2
\d sales_hash_3
\d sales_hash_4
\d sales_hash
EXECUTE spocktab('sales_hash'); -- Expect all partitions to be listed
SELECT * FROM sales_hash ORDER BY sale_id; -- Expect 4 rows
--exercise ddl on n2
DROP TABLE sales_hash CASCADE;

\d products_hash
\d products_hash_1
\d products_hash_2
\d products_hash_3
\d products_hash_4

EXECUTE spocktab('products_hash'); -- Expect the replication set to be default
SELECT * FROM products_hash ORDER BY product_id; -- Expect 4 rows
--exercise ddl on n2
DROP TABLE products_hash CASCADE;
