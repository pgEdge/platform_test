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

## Create an anonymous block that puts the cluster in repair mode and does an insert statement that will
## add a row to n1 that will not be replicated to n2 

anon_block = """
DO $$
BEGIN
    PERFORM spock.repair_mode('True');
    INSERT INTO pgbench_branches VALUES (2, 70000, null);
END $$;
"""

print(anon_block)

row = util_test.write_psql(f"{anon_block}",host,dbname,port1,pw,usr)
print(row)

## Look for our row on n1 and n2:

row1 = util_test.read_psql("SELECT * FROM pgbench_branches",host,dbname,port1,pw,usr)
print(row1)

row2 = util_test.read_psql("SELECT * FROM pgbench_branches",host,dbname,port2,pw,usr)
print(row2)

print("*"*100)

if "2, 70000, null" in str(row2) or "2, 70000, null" not in str(row1):
    
    util_test.EXIT_FAIL()
else:
    util_test.EXIT_PASS()

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)


