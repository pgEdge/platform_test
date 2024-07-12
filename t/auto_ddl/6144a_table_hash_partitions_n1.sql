-- Prepared statement for spock.tables to list parent and child tables as parent table name will be contained in partition name
PREPARE spocktab AS SELECT nspname, relname, set_name FROM spock.tables WHERE relname LIKE '%' || $1 || '%' ORDER BY relid;

-----------------------------
-- Hash Partitioning
-----------------------------

-- Create a hash partitioned table with primary key
CREATE TABLE sales_hash (
    sale_id INT,
    sale_date DATE,
    sale_amount DECIMAL,
    PRIMARY KEY (sale_id, sale_date)
) PARTITION BY HASH (sale_id);

-- Add partitions to the sales_hash table
CREATE TABLE sales_hash_1 PARTITION OF sales_hash
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE sales_hash_2 PARTITION OF sales_hash
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE sales_hash_3 PARTITION OF sales_hash
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE sales_hash_4 PARTITION OF sales_hash
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);

-- Insert data into the sales_hash table
INSERT INTO sales_hash (sale_id, sale_date, sale_amount) VALUES
(1, '2023-01-01', 100.0),
(2, '2023-01-02', 200.0),
(3, '2023-01-03', 150.0),
(4, '2023-01-04', 250.0);

EXECUTE spocktab('sales_hash'); -- Expect both parent and child tables in default repset
SELECT * FROM sales_hash ORDER BY sale_id; -- Expect 4 rows

-- Validate structure and data after adding new partition
\d sales_hash_1
\d sales_hash_2
\d sales_hash_3
\d sales_hash_4
\d sales_hash
EXECUTE spocktab('sales_hash'); -- Expect all partitions to be listed
SELECT * FROM sales_hash ORDER BY sale_id; -- Expect 4 rows

-- Create a hash partitioned table without primary key
CREATE TABLE products_hash (
    product_id INT,
    product_date DATE,
    product_name TEXT
) PARTITION BY HASH (product_id);

-- Add partitions to the products_hash table
CREATE TABLE products_hash_1 PARTITION OF products_hash
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE products_hash_2 PARTITION OF products_hash
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE products_hash_3 PARTITION OF products_hash
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE products_hash_4 PARTITION OF products_hash
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);

-- Insert data into the products_hash table
INSERT INTO products_hash (product_id, product_date, product_name) VALUES
(1, '2023-01-01', 'Laptop'),
(2, '2023-01-02', 'Shirt'),
(3, '2023-01-03', 'Smartphone'),
(4, '2023-01-04', 'Tablet');

-- Validate structure and data
\d+ products_hash
EXECUTE spocktab('products_hash'); -- Expect both parent and child tables in default_insert_only set
SELECT * FROM products_hash ORDER BY product_id; -- Expect 4 rows

-- Alter the products_hash table to add a primary key
ALTER TABLE products_hash ADD PRIMARY KEY (product_id, product_date);

-- Validate structure and data after adding primary key
\d products_hash
\d products_hash_1
\d products_hash_2
\d products_hash_3
\d products_hash_4
/*TO FIX:
commenting this test case due to https://github.com/orgs/pgEdge/projects/6/views/7?filterQuery=category%3AAutoDDL+&visibleFields=%5B%22Title%22%2C%22Assignees%22%2C%22Status%22%2C77649763%5D&pane=issue&itemId=69962278
only the parent table moves to default repset, all partitions continue to stay in default_insert_only
*/
EXECUTE spocktab('products_hash'); -- Expect the replication set to change to default
SELECT * FROM products_hash ORDER BY product_id; -- Expect 4 rows
