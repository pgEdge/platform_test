--This file will run on n2 and validate all the replicated tables data, structure and replication sets they're in
-- Prepared statement for spock.tables to list parent and child tables as parent table name will be contained in partition name
PREPARE spocktab AS SELECT nspname, relname, set_name FROM spock.tables WHERE relname LIKE '%' || $1 || '%' ORDER BY relid;

EXECUTE spocktab('sales_range'); -- Expect sales_range, sales_range_2022, sales_range_2021 in default set
EXECUTE spocktab('revenue_range'); -- Expect revenue_range, revenue_range_2023 in default and revenue_range_2021, revenue_range_2022 in default_insert_only set
EXECUTE spocktab('orders_range'); -- Expect orders_range, orders_range_2021, orders_range_2022 in default set

-- Validate final data
SELECT * FROM sales_range ORDER BY sale_id; -- Expect all rows
SELECT * FROM revenue_range ORDER BY rev_id; -- Expect all rows
SELECT * FROM orders_range ORDER BY order_id; -- Expect all rows
SELECT * FROM inventory_range_default ORDER BY product_id; -- Expect 2 rows
SELECT * FROM inventory_standalone ORDER BY product_id; -- Expect 1 row

-- Validate final structure
\d+ sales_range
\d+ sales_range_2021
\d+ sales_range_2022
\d+ sales_range_2023

\d+ revenue_range
\d+ revenue_range_2021
\d+ revenue_range_2022
\d orders_range

\d+ orders_range
\d+ orders_range_2021
\d+ orders_range_2022

\d+ inventory_range
\d+ inventory_range_2021
\d+ inventory_range_default
\d+ inventory_standalone

DROP TABLE sales_range CASCADE;
DROP TABLE revenue_range CASCADE;
DROP TABLE orders_range CASCADE;
DROP TABLE inventory_range CASCADE;
