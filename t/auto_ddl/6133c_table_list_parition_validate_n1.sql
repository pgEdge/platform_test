-- This file runs on n1 again to see all the table and their partitions have been dropped on n1 (as a result of drop statements)
-- being auto replicated via 6133b

--spock.tables should be empty
SELECT * FROM spock.tables ORDER BY relid;
-- none of these tables should exist.
\d sales_list_east
\d sales_list_west
\d sales_list_north
\d sales_list

/*
\d+ products_list
\d+ products_list_clothing
\d+ products_list_electronics
*/