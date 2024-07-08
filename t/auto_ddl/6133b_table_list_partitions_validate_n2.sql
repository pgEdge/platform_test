--This file will run on n2 and validate all the replicated tables data, structure and replication sets they're in
-- Prepared statement for spock.tables to list parent and child tables as parent table name will be contained in partition name
PREPARE spocktab AS SELECT nspname, relname, set_name FROM spock.tables WHERE relname LIKE '%' || $1 || '%' ORDER BY relid;

\d+ sales_list_east
\d+ sales_list_west
\d+ sales_list_north
\d+ sales_list
EXECUTE spocktab('sales_list'); -- Expect the new partition to be listed
SELECT * FROM sales_list ORDER BY sale_id; -- Expect 4 rows
--exercise ddl on n2
DROP TABLE sales_list CASCADE;
/*
https://github.com/orgs/pgEdge/projects/6/views/7?filterQuery=category%3AAutoDDL+&visibleFields=%5B%22Title%22%2C%22Assignees%22%2C%22Status%22%2C77649763%5D&pane=issue&itemId=69962278
\d+ products_list
\d+ products_list_clothing
\d+ products_list_electronics
EXECUTE spocktab('products_list'); -- Expect all to be in default repset
SELECT * FROM products_list ORDER BY product_id; -- Expect 3 rows
--exercise ddl on n2
DROP TABLE products_list CASCADE;
*/
