import sys, os, util_test, subprocess, time

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
seconds=int(os.getenv("EDGE_SLEEP"))

port2 = port1+1
print(port2)
nc_dir=os.getenv("NC_DIR","nc")
home_dir = os.getenv("EDGE_HOME_DIR") 

## Check the information from cluster list-nodes.
command = (f"cluster list-nodes demo")
res=util_test.run_nc_cmd("Exercise the list-nodes command", command, f"{home_dir}")
print(f"Command: {command}")
print(f"The list-nodes command returns = {res}\n")
print("*"*100)

## Setup on n1 
## Create a table with three columns:
command1 = "CREATE TABLE case4 (bid integer PRIMARY KEY, bbalance integer, filler character(88))"
row1 = util_test.write_psql(command1,host,dbname,port1,pw,usr)
#print(f"The create table statement on n1 returns: {row1}")

## Add a row:
command2 = "INSERT INTO case4 VALUES (1, 11111, 'filler')"
print(f"{command2}")
row2 = util_test.write_psql(command2,host,dbname,port1,pw,usr)
#print(f"The insert statement on n1 returns: {row2}")

## Add it to the default repset:
command3 = f"spock repset-add-table default case4 {dbname}"
res3=util_test.run_cmd("Adding our table to the default repset", command3, f"{cluster_dir}/n1")
print(f"The repset-add-table command on n1 returns: {res3}")
print("*"*100)

## Setup on n2
## Create a table with the same name as the table on n1, but with two columns:
command4 = "CREATE TABLE case4 (bid integer PRIMARY KEY, bbalance integer)"
row4 = util_test.write_psql(command4,host,dbname,port2,pw,usr)
#print(f"The create table statement on n2 returns: {row4}")

## Add a row:
command5 = "INSERT INTO case4 VALUES (1, 11111)"
row5 = util_test.write_psql(command5,host,dbname,port2,pw,usr)
#print(f"The insert statement on n2 returns: {row5}")

## Add it to the default repset:
command6 = f"spock repset-add-table default case4 {dbname}"
res6=util_test.run_cmd("Adding our table to the default repset", command6, f"{cluster_dir}/n2")
print(f"The repset-add-table command on n2 returns: {res6}")
print("*"*100)

## Confirm with SELECT * FROM spock.tables.
row7 = util_test.read_psql("SELECT relname FROM spock.tables;",host,dbname,port1,pw,usr)
print(f"The n1 select * from spock.tables returns: {row7}")
print("*"*100)

## Check the values in case4 on n1.
row7 = util_test.read_psql("SELECT * FROM case4;",host,dbname,port1,pw,usr)
print(f"The n1 select * from case4 returns: {row7}")
print("*"*100)


## Confirm with SELECT * FROM spock.tables on n2.
row8 = util_test.read_psql("SELECT relname FROM spock.tables;",host,dbname,port2,pw,usr)
print(f"The n2 select * from spock.tables returns: {row8}")
print("*"*100)

## Check the values in case4 on n2.
row7 = util_test.read_psql("SELECT * FROM case4;",host,dbname,port2,pw,usr)
print(f"The n2 select * from case4 returns: {row7}")
print("*"*100)


## Enable AutoDDL (uses connection that allows ALTER SYSTEM SET) and reload configuration: 
n1enable = util_test.enable_autoddl(host, dbname, port1, pw, usr)
n2enable = util_test.enable_autoddl(host, dbname, port2, pw, usr)

## Check our variable values;
row = util_test.read_psql("SELECT name, setting FROM pg_settings WHERE NAME LIKE 'spock.%'",host,dbname,port1,pw,usr)
print(f"SELECT * FROM spock.exception_log on n1 returns: {row}")
print("*"*100)

## Check our variable values;
row = util_test.read_psql("SELECT name, setting FROM pg_settings WHERE NAME LIKE 'spock.%'",host,dbname,port2,pw,usr)
print(f"SELECT * FROM spock.exception_log on n2 returns: {row}")
print("*"*100)

## Drop the filler column from n1:
command1 = "ALTER TABLE case4 DROP COLUMN filler"
row1 = util_test.write_psql(command1,host,dbname,port1,pw,usr)
#print(f"We just dropped the filler column from n1: {row1}")
print("*"*100)

## Read from the spock.exception_log;
row = util_test.read_psql("SELECT remote_new_tup FROM spock.exception_log WHERE table_name = 'queue'",host,dbname,port1,pw,usr)
print(f"SELECT * FROM spock.exception_log on n1 returns: {row}")
print("*"*100)

## Read from the spock.exception_log;
row = util_test.read_psql("SELECT remote_new_tup FROM spock.exception_log WHERE table_name = 'queue';",host,dbname,port2,pw,usr)
print(f"SELECT * FROM spock.exception_log on n2 returns: {row}")
print("*"*100)


if 'ALTER TABLE case4 DROP COLUMN filler' in str(row):
    
    util_test.EXIT_PASS()
else:
    util_test.EXIT_FAIL()

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)


