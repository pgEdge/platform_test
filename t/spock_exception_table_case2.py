import sys, os, util_test,subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()
#
repo=os.getenv("EDGE_REPO")
num_nodes=int(os.getenv("EDGE_NODES",2))
cluster_dir=os.getenv("EDGE_CLUSTER_DIR")
port1=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","admin")
pw=os.getenv("EDGE_PASSWORD","password1")
db=os.getenv("EDGE_DB","demo")
host=os.getenv("EDGE_HOST","localhost")
repuser=os.getenv("EDGE_REPUSER","pgedge")
repset=os.getenv("EDGE_REPSET","demo-repset")
spockpath=os.getenv("EDGE_SPOCK_PATH")
dbname=os.getenv("EDGE_DB","lcdb")

port2=port1+1
print(port2)

## pgbench-install on n1
## CONFIRM that if a database name and repset name are provided, pgbench is installed as expected and the transactions are added to the repset
cmd_node = f"app pgbench-install {dbname} -r default"
res=util_test.run_cmd("running pgbench-install including repsetname", cmd_node, f"{cluster_dir}/n1")
print(f"The installation on n1 returns: {res}")
print("*"*100) 

## pgbench-install in n2
## CONFIRM that if a database name and repset name are provided, pgbench is installed as expected and the transactions are added to the repset
cmd_node = f"app pgbench-install {dbname} -r default"
res=util_test.run_cmd("running pgbench-install including repsetname", cmd_node, f"{cluster_dir}/n2")
print(f"The installation on n2 returns: {res}")
print("*"*100)

## Use needle/haystack to confirm pgbench is installed on n1
## confirm with SELECT * FROM spock.tables.
row = util_test.read_psql("SELECT * FROM spock.tables",host,dbname,port1,pw,usr).strip("[]")
check=util_test.contains((row),"default")
print(f"The n1 check returns: {row}")
print("*"*100)

## Use needle/haystack to confirm pgbench is installed on n2.
## confirm with SELECT * FROM pgbench_branches on n2.
row = util_test.read_psql("SELECT * FROM pgbench_branches",host,dbname,port2,pw,usr)
#check=util_test.contains((row),"default")
print(f"The n2 check returns: {row}")
print("*"*100)

## Add two rows that should be replicated from n1 to n2:

row = util_test.write_psql("INSERT INTO pgbench_branches VALUES(11, 11000, null)",host,dbname,port1,pw,usr)
print(f"We inserted bid 11 on n1: {row}")
print("*"*100)

row = util_test.write_psql("INSERT INTO pgbench_branches VALUES(22, 22000, null)",host,dbname,port1,pw,usr)
print(f"We inserted bid 22 on n1: {row}")
print("*"*100)

## Look for our rows on n1 and n2:

row1 = util_test.read_psql("SELECT * FROM pgbench_branches",host,dbname,port1,pw,usr)
print(f"Node n1 should contain bid 1/11/22: {row1}")

row2 = util_test.read_psql("SELECT * FROM pgbench_branches",host,dbname,port2,pw,usr)
print(f"Node n2 should contain bid 1/11/22: {row2}")

print("*"*100)

## Create an anonymous block that puts the cluster in repair mode and does an insert statement that will
## add a row to n2 that will not be replicated to n1:

anon_block = """
DO $$
BEGIN
    PERFORM spock.repair_mode('True');
    INSERT INTO pgbench_branches VALUES (33, 33000, null);
END $$;
"""

print(anon_block)
row = util_test.write_psql(f"{anon_block}",host,dbname,port2,pw,usr)
print(row)

## Check the rows on n1 and n2:

row1 = util_test.read_psql("SELECT * FROM pgbench_branches",host,dbname,port1,pw,usr)
print(f"We're in repair mode - n1 now contains 1/11/22: {row1}")

row2 = util_test.read_psql("SELECT * FROM pgbench_branches",host,dbname,port2,pw,usr)
print(f"We're in repair mode - n2 now contains 1/11/22/33: {row2}")

print("*"*100)

## Node n2 has three rows; bid 33 is not replicated to n1, so an update should end up in the exception log table:
row = util_test.write_psql("UPDATE pgbench_branches SET filler = 'trouble' WHERE bid = 33",host,dbname,port2,pw,usr)
print(f"We're in repair mode - the update to bid 33 on n2 returns: {row}")
print("*"*100)

## Read from the spock.exception_log on n1;
row = util_test.read_psql("SELECT remote_new_tup FROM spock.exception_log",host,dbname,port1,pw,usr).strip("[]")
print(f"SELECT * FROM spock.exception_log returns: {row}")
print("*"*100)

## Demonstrate that replication continues
row = util_test.write_psql("UPDATE pgbench_branches SET filler = 'replication check' WHERE bid = 11",host,dbname,port2,pw,usr)
print(f"The update to bid 11 on n1 returns: {row}")
print("*"*100)

## Show that the row update made it to n2 without causing a death spiral:
row = util_test.read_psql("SELECT * FROM pgbench_branches",host,dbname,port2,pw,usr).strip("[]")
print(f"bid 11 should be updated on n2, pgbench branches contains: {row}")
print("*"*100)

## Read from the spock.exception_log on n1 (the update from of bid3 should be here);
row = util_test.read_psql("SELECT remote_new_tup FROM spock.exception_log",host,dbname,port1,pw,usr)
print(f"SELECT * FROM spock.exception_log on n1 returns: {row}")
print("*"*100)


if '"value": 33, "attname": "bid", "atttype": "int4"' in str(row):
    
    util_test.EXIT_PASS()
else:
    util_test.EXIT_FAIL()

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)


