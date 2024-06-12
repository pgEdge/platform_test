-- This file runs on n1 again to see all the table and their partitions have been dropped on n1 (as a result of drop statements)
-- being auto replicated via 6122b

--spock.tables should be empty
SELECT * FROM spock.tables ORDER BY relid;
-- none of these tables should exist.
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
