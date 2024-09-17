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

print("*"*100)
nc_dir=os.getenv("NC_DIR","nc")
print(nc_dir)
home_dir = os.getenv("EDGE_HOME_DIR")
print(home_dir)

# Check the information from cluster list-nodes.
#
command = (f"cluster list-nodes demo")
res=util_test.run_nc_cmd("Exercise the list-nodes command", command, f"{home_dir}")
print(f"Command: {command}")
print(f"The list-nodes command returns = {res}\n")
print("*"*100)

## Setup on n1:
## Create a table:
command1 = "CREATE TABLE case2 (bid integer PRIMARY KEY, bbalance integer, filler character(88))"
row1 = util_test.write_psql(command1,host,dbname,port1,pw,usr)

## Add a row:
command2 = "INSERT INTO case2 VALUES (1, 11111, 'filler')"
print(f"{command2}")
row2 = util_test.write_psql(command2,host,dbname,port1,pw,usr)

## Add it to the default repset:
command3 = f"spock repset-add-table default case2 {dbname}"
res3=util_test.run_cmd("Adding our table to the default repset", command3, f"{cluster_dir}/n1")
print(f"The repset-add-table command on n1 returns: {res3}")

print("*"*100)

## Setup on n2:
## Create a table:
command4 = "CREATE TABLE case2 (bid integer PRIMARY KEY, bbalance integer, filler character(88))"
row4 = util_test.write_psql(command4,host,dbname,port2,pw,usr)

## Add a row:
command5 = "INSERT INTO case2 VALUES (1, 11111, 'filler')"
row5 = util_test.write_psql(command5,host,dbname,port2,pw,usr)

## Add it to the default repset:
command6 = f"spock repset-add-table default case2 {dbname}"
res6=util_test.run_cmd("Adding our table to the default repset", command6, f"{cluster_dir}/n2")
print(f"The repset-add-table command on n2 returns: {res6}")

print("*"*100)

## Confirm with SELECT * FROM spock.tables.
row7 = util_test.read_psql("SELECT relname FROM spock.tables;",host,dbname,port1,pw,usr)
print(f"The n1 select * from spock.tables returns: {row7}")
print("*"*100)

## Confirm with SELECT * FROM spock.tables on n2.
row8 = util_test.read_psql("SELECT relname FROM spock.tables;",host,dbname,port2,pw,usr)
print(f"The n2 select * from spock.tables returns: {row8}")
print("*"*100)


## Add two rows that should be replicated from n1 to n2:

row = util_test.write_psql("INSERT INTO case2 VALUES(11, 11000, null)",host,dbname,port1,pw,usr)
print(f"We inserted bid 11 on n1: {row}")
print("*"*100)

row = util_test.write_psql("INSERT INTO case2 VALUES(22, 22000, null)",host,dbname,port1,pw,usr)
print(f"We inserted bid 22 on n1: {row}")
print("*"*100)

## Look for our rows on n1 and n2:

row1 = util_test.read_psql("SELECT * FROM case2",host,dbname,port1,pw,usr)
print(f"Node n1 should contain bid 1/11/22: {row1}")

row2 = util_test.read_psql("SELECT * FROM case2",host,dbname,port2,pw,usr)
print(f"Node n2 should contain bid 1/11/22: {row2}")

print("*"*100)

## Create an anonymous block that puts the cluster in repair mode and does an insert statement that will
## add a row to n2 that will not be replicated to n1:

anon_block = """
DO $$
BEGIN
    PERFORM spock.repair_mode('True');
    INSERT INTO case2 VALUES (33, 33000, null);
END $$;
"""

print(anon_block)
row = util_test.write_psql(f"{anon_block}",host,dbname,port2,pw,usr)
print(row)

## Check the rows on n1 and n2:

row1 = util_test.read_psql("SELECT * FROM case2",host,dbname,port1,pw,usr)
print(f"We're in repair mode - n1 now contains 1/11/22: {row1}")

row2 = util_test.read_psql("SELECT * FROM case2",host,dbname,port2,pw,usr)
print(f"We're in repair mode - n2 now contains 1/11/22/33: {row2}")

print("*"*100)

## Node n2 has three rows; bid 33 is not replicated to n1, so an update should end up in the exception log table:
row = util_test.write_psql("UPDATE case2 SET filler = 'trouble' WHERE bid = 33",host,dbname,port2,pw,usr)
print(f"We're in repair mode - the update to bid 33 on n2 returns: {row}")
print("*"*100)

## Read from the spock.exception_log on n1;
#row = util_test.read_psql("SELECT remote_new_tup FROM spock.exception_log",host,dbname,port1,pw,usr).strip("[]")
#print(f"SELECT * FROM spock.exception_log returns: {row}")
#print("*"*100)

## Demonstrate that replication continues
row = util_test.write_psql("UPDATE case2 SET filler = 'replication check' WHERE bid = 11",host,dbname,port2,pw,usr)
print(f"The update to bid 11 on n1 returns: {row}")
print("*"*100)

## Show that the row update made it to n2 without causing a death spiral:
row = util_test.read_psql("SELECT * FROM case2",host,dbname,port2,pw,usr).strip("[]")
print(f"bid 11 should be updated on n2, case2 contains: {row}")
print("*"*100)

## Read from the spock.exception_log on n1 (the update of bid3 should be here);
row = util_test.read_psql("SELECT remote_new_tup FROM spock.exception_log WHERE table_name = 'case2';",host,dbname,port1,pw,usr)
print(f"SELECT * FROM spock.exception_log on n1 returns: {row}")
print("*"*100)


if '"value": 33, "attname": "bid", "atttype": "int4"' in str(row):
    
    util_test.EXIT_PASS()
else:
    util_test.EXIT_FAIL()

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)

