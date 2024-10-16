-- Prepared statement for spock.tables to list parent and child tables as parent table name will be contained in partition name
PREPARE spocktab AS SELECT nspname, relname, set_name FROM spock.tables WHERE relname LIKE '%' || $1 || '%' ORDER BY relid;

--------------------------------
-- Range Partitioned Tables
--------------------------------

-- Create a range partitioned table with primary key
CREATE TABLE sales_range (
    sale_id INT,
    sale_date DATE,
    amount DECIMAL,
    PRIMARY KEY (sale_id, sale_date)
) PARTITION BY RANGE (sale_date);

-- Add partitions to the range partitioned table
CREATE TABLE sales_range_2021 PARTITION OF sales_range
    FOR VALUES FROM ('2021-01-01') TO ('2022-01-01');
CREATE TABLE sales_range_2022 PARTITION OF sales_range
    FOR VALUES FROM ('2022-01-01') TO ('2023-01-01');

-- Insert data into range partitioned table
INSERT INTO sales_range (sale_id, sale_date, amount) VALUES
(1, '2021-03-15', 150.00), 
(2, '2021-07-21', 200.00), 
(3, '2022-02-10', 250.00);

-- Validate structure and data
EXECUTE spocktab('sales_range'); -- Expect both parent and child tables in default set
SELECT * FROM sales_range ORDER BY sale_id; -- Expect 3 rows sorted by sale_id

-- Create another range partitioned table without primary key
CREATE TABLE revenue_range (
    rev_id INT,
    rev_date DATE,
    revenue DECIMAL
) PARTITION BY RANGE (rev_date);

-- Add partitions to the new range partitioned table
CREATE TABLE revenue_range_2021 PARTITION OF revenue_range
    FOR VALUES FROM ('2021-01-01') TO ('2022-01-01');
CREATE TABLE revenue_range_2022 PARTITION OF revenue_range
    FOR VALUES FROM ('2022-01-01') TO ('2023-01-01');

-- Insert data into the new range partitioned table
INSERT INTO revenue_range (rev_id, rev_date, revenue) VALUES
(101, '2021-04-12', 300.00),
(102, '2022-05-18', 400.00);

-- Validate structure and data

EXECUTE spocktab('revenue_range'); -- Expect both parent and child tables in default_insert_only set
SELECT * FROM revenue_range ORDER BY rev_id; -- Expect 2 rows sorted by rev_id

-- Alter table to add a new partition
CREATE TABLE sales_range_2023 PARTITION OF sales_range
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');
\d+ sales_range_2023
EXECUTE spocktab('sales_range'); -- Expect sales_range_2023 in default set

-- Add a primary key to a range partitioned table that initially didn't have one
ALTER TABLE revenue_range ADD PRIMARY KEY (rev_id, rev_date);
\d revenue_range

EXECUTE spocktab('revenue_range'); -- Expect revenue_range and all child partitions to move to default set

-- Add another partition to the modified table
CREATE TABLE revenue_range_2023 PARTITION OF revenue_range
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');
\d+ revenue_range_2023
EXECUTE spocktab('revenue_range'); -- Expect revenue_range_2023 in default set

-- Insert data into the newly added partitions
INSERT INTO sales_range (sale_id, sale_date, amount) VALUES
(4, '2023-03-22', 300.00);
INSERT INTO revenue_range (rev_id, rev_date, revenue) VALUES
(103, '2023-07-15', 500.00);

-- Create an additional range partitioned table with indexes and keys
CREATE TABLE orders_range (
    order_id INT,
    order_date DATE,
    customer_id INT,
    total DECIMAL,
    PRIMARY KEY (order_id, order_date)
) PARTITION BY RANGE (order_date);

-- Add partitions to the orders_range table
CREATE TABLE orders_range_2021 PARTITION OF orders_range
    FOR VALUES FROM ('2021-01-01') TO ('2022-01-01');
CREATE TABLE orders_range_2022 PARTITION OF orders_range
    FOR VALUES FROM ('2022-01-01') TO ('2023-01-01');

-- Insert data into the orders_range table
INSERT INTO orders_range (order_id, order_date, customer_id, total) VALUES
(1001, '2021-06-15', 1, 500.00),
(1002, '2022-01-10', 2, 1000.00);

-- Validate structure and data
EXECUTE spocktab('orders_range'); -- Expect both parent and child tables in default set
SELECT * FROM orders_range ORDER BY order_id; -- Expect 2 rows 

-- Drop a partition
ALTER TABLE sales_range DETACH PARTITION sales_range_2023;
EXECUTE spocktab('sales_range'); --should still have the repset assigned
DROP TABLE sales_range_2023;
EXECUTE spocktab('sales_range'); -- validate sales_range_2023 to be removed 

-- Create a range partitioned table with default partition
CREATE TABLE inventory_range (
    product_id INT,
    product_date DATE,
    quantity BIGINT,
    PRIMARY KEY (product_id, product_date)
) PARTITION BY RANGE (product_date);

-- Add partitions to the inventory_range table
CREATE TABLE inventory_range_2021 PARTITION OF inventory_range
    FOR VALUES FROM ('2021-01-01') TO ('2022-01-01');
CREATE TABLE inventory_range_default PARTITION OF inventory_range
    DEFAULT;

-- Insert data into the inventory_range table
INSERT INTO inventory_range (product_id, product_date, quantity) VALUES
(1, '2021-06-15', 50),
(2, '2022-02-10', 100); -- Should go to default partition

-- Validate structure and data
EXECUTE spocktab('inventory_range'); -- Expect both parent and child tables in default set
SELECT * FROM inventory_range ORDER BY product_id; -- Expect 2 rows

-- Alter the inventory_range table to add a new column and change data type
ALTER TABLE inventory_range ADD COLUMN price DECIMAL;
ALTER TABLE inventory_range ALTER COLUMN quantity TYPE BIGINT;

-- Add a constraint to the inventory_range_2021 partition
ALTER TABLE inventory_range_2021 ADD CONSTRAINT chk_quantity CHECK (quantity >= 0);

-- Insert data that falls outside the defined range
INSERT INTO inventory_range (product_id, product_date, quantity) VALUES
(3, '2025-01-01', 150); -- Should go to default partition

-- Attaching and detaching partitions

-- Create a standalone table with matching columns and types, with NOT NULL constraints and without a primary key
CREATE TABLE inventory_standalone (
    product_id INT NOT NULL,
    product_date DATE NOT NULL,
    quantity BIGINT,
    price DECIMAL
);

-- Insert data into the standalone table
INSERT INTO inventory_standalone (product_id, product_date, quantity, price) VALUES
(4, '2023-03-15', 200, 19.99);

-- Attach the standalone table as a partition
ALTER TABLE inventory_range ATTACH PARTITION inventory_standalone FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

-- Validate structure and data
EXECUTE spocktab('inventory'); -- Expect inventory_standalone to be listed
SELECT * FROM inventory_standalone ORDER BY product_id; -- Expect 1 row

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
