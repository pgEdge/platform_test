-- This file runs on n1 again to see all the table and their partitions have been dropped on n1 (as a result of drop statements)
-- being auto replicated via 6144b

--spock.tables should be empty
SELECT * FROM spock.tables ORDER BY relid;
-- none of these tables should exist.
\d sales_hash_1
\d sales_hash_2
\d sales_hash_3
\d sales_hash_4
\d sales_hash

/*
*/
\d products_hash
\d products_hash_1
\d products_hash_2
\d products_hash_3
\d products_hash_4
