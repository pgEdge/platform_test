import sys, os, util_test, subprocess
import psycopg

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

num_nodes=int(os.getenv("EDGE_NODES",2))
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","lcusr")
pw=os.getenv("EDGE_PASSWORD","password")
host=os.getenv("EDGE_HOST","localhost")
dbname=os.getenv("EDGE_DB","lcdb")
cluster_dir = os.getenv("EDGE_CLUSTER_DIR")

## Creates data for all future ace tests

## Assumes that basic environment is already set up as by
"""
t/setup_01_install.py
t/setup_02_nodecreate.py
t/setup_03_noderun.py
"""


for n in range(1,num_nodes+1):
    #CREATE table matching
    row = util_test.write_psql("CREATE TABLE IF NOT EXISTS foo (employeeID INT PRIMARY KEY,employeeName VARCHAR(40),employeeMail VARCHAR(40))",host,dbname,port,pw,usr)
    #INSERT data
    row = util_test.write_psql("INSERT INTO foo (employeeID,employeeName,employeeMail) VALUES(1,'Carol','carol@pgedge.com'),(2,'Bob','bob@pgedge.com')",host,dbname,port,pw,usr)


    #CREATE table - data diff
    row = util_test.write_psql("CREATE TABLE IF NOT EXISTS foo_diff_data (employeeID INT PRIMARY KEY,employeeName VARCHAR(40),employeeMail VARCHAR(40))",host,dbname,port,pw,usr)
    #INSERT data
    if n!=2:
        row = util_test.write_psql("INSERT INTO foo_diff_data (employeeID,employeeName,employeeMail) VALUES(1,'Carol','carol@pgedge.com'),(2,'Bob','bob@pgedge.com')",host,dbname,port,pw,usr)
    else:
        row = util_test.write_psql("INSERT INTO foo_diff_data (employeeID,employeeName,employeeMail) VALUES(1,'Alice','alice@pgedge.com'),(2,'Carol','carol@pgedge.com')",host,dbname,port,pw,usr)

    #CREATE table - row diff
    row = util_test.write_psql("CREATE TABLE IF NOT EXISTS foo_diff_row (employeeID INT PRIMARY KEY,employeeName VARCHAR(40),employeeMail VARCHAR(40))",host,dbname,port,pw,usr)
    #INSERT data
    row = util_test.write_psql("INSERT INTO foo_diff_row (employeeID,employeeName,employeeMail) VALUES(1,'Bob','bob@pgedge.com'),(2,'Carol','carol@pgedge.com')",host,dbname,port,pw,usr)
    if n==2:
        row = util_test.write_psql("INSERT INTO foo_diff_row (employeeID,employeeName,employeeMail) VALUES(3,'Alice','alice@pgedge.com')",host,dbname,port,pw,usr)


    #CREATE table - no primarykey
    row = util_test.write_psql("CREATE TABLE IF NOT EXISTS foo_nopk (employeeID INT ,employeeName VARCHAR(40),employeeMail VARCHAR(40))",host,dbname,port,pw,usr)
    #INSERT data
    row = util_test.write_psql("INSERT INTO foo_nopk (employeeID,employeeName,employeeMail) VALUES(1,'Carol','carol@pgedge.com'),(2,'Bob','bob@pgedge.com')",host,dbname,port,pw,usr)


    # Creates users Carol and Alice
    row = util_test.write_psql("CREATE USER alice WITH PASSWORD 'password'", host,dbname,port,pw,usr)
    row = util_test.write_psql("CREATE USER carol WITH PASSWORD 'password'", host,dbname,port,pw,usr)


    def create_database(conn: psycopg.Connection, db_name: str):
        cur = conn.cursor()
        try:
            cur.execute(f"CREATE DATABASE {db_name};")
            conn.commit()
            print(f"Created database {db_name}")
        except Exception as e:
            conn.rollback()
            util_test.exit_message(f"Error creating database: {e}")
        finally:
            cur.close()

    with psycopg.connect(dbname=dbname, user=usr, host=host, port=port, password=pw, autocommit=True) as conn:
        create_database(conn, "alicesdb")
        create_database(conn, "carolsdb")


    row = util_test.write_psql("GRANT ALL PRIVILEGES ON DATABASE alicesdb TO alice", host,dbname,port,pw,usr)
    row = util_test.write_psql("GRANT ALL PRIVILEGES ON SCHEMA public TO alice", host, "alicesdb", port, pw, usr)
    row = util_test.write_psql("CREATE TABLE foo(id serial primary key, data int);", host,"alicesdb",port,"password","alice")
    row = util_test.write_psql("INSERT INTO foo values (10, 0);", host, "alicesdb", port, "password", "alice")

    
    row = util_test.write_psql("GRANT ALL PRIVILEGES ON DATABASE carolsdb TO carol", host,dbname,port,pw,usr)
    row = util_test.write_psql("GRANT ALL PRIVILEGES ON SCHEMA public TO carol", host, "carolsdb", port, pw, usr)
    row = util_test.write_psql("CREATE TABLE foo(id serial primary key, data int);", host,"carolsdb",port,"password","carol")


    print(f"Created tables on n{n}")

    cmd_node = f"spock repset-add-table default 'public.foo' {dbname}"
    res=util_test.run_cmd("add tables to repset", cmd_node, f"{cluster_dir}/n{n}")

    print(f"Added tables to repset on n{n}")

    #DROP my_table if exists
    row = util_test.write_psql("DROP TABLE IF EXISTS my_table CASCADE",host,dbname,port,pw,usr)

    port = port + 1

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
