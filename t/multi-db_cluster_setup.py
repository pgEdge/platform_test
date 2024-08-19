# Following a two-node model to recreate the QubeRT issue

import sys, os, util_test, subprocess, json

# Print Script
print(f"Starting - {os.path.basename(__file__)}")

# Get Test Settings
util_test.set_env()
repo=os.getenv("EDGE_REPO")
pgv=os.getenv("EDGE_INST_VERSION")
num_nodes=2
home_dir=os.getenv("EDGE_HOME_DIR")
cluster_dir=os.getenv("EDGE_CLUSTER_DIR")
cluster_name=os.getenv("EDGE_CLUSTER","demo")
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","lcusr")
pw=os.getenv("EDGE_PASSWORD","password")
host=os.getenv("EDGE_HOST","localhost")
repuser=os.getenv("EDGE_REPUSER","susan")
repset=os.getenv("EDGE_REPSET","demo-repset")
spockpath=os.getenv("EDGE_SPOCK_PATH")
dbname=os.getenv("EDGE_DB","lcdb")
node_name="n1"
cwd=os.getcwd()
#print("*"*100)

print(f"home_dir = {home_dir}\n")
command = (f"cluster json-template {cluster_name} {dbname} {num_nodes} {usr} {pw} {pgv} {port}")
res=util_test.run_nc_cmd("This command should create a json file that defines a cluster", command, f"{home_dir}")
print(f"res = {res}\n")

## Before we can update the demo.json file, we need to add dictionary entries to hold the extra
#  database that the customer is using:

# load the demo.json file:
with open(f"{cluster_dir}/{cluster_name}.json", "r") as file:
    file_data = json.loads(file.read())

# Add an extra database dictionary to the .json file:

new_dict = [{"db_user": "alice","db_password": "password","db_name": "alicesdb"},{"db_user": "lcusr","db_password": "password","db_name": "lcdb"}]

file_data["pgedge"]["databases"]=new_dict

print(f"The database definition contains: {file_data}")

# write the file back
with open(f"{cluster_dir}/{cluster_name}.json", "w") as file:
    file.write(json.dumps(file_data))

# The following set of commands update the arrays specified in our json file that we just created.
# The first entry in the array is referred to as '0', then '1', etc.
# The QubeRT issue uses a three node cluster, but we're doing the same basic test with a two-node
# cluster.

new_path_0 = (f"{cwd}/{cluster_dir}/n1")
new_path_1 = (f"{cwd}/{cluster_dir}/n2")

with open(f"{cluster_dir}/{cluster_name}.json", 'r') as file:
    data = json.load(file)
    #print(data)
    data["node_groups"][0]["path"] = new_path_0
    data["node_groups"][1]["path"] = new_path_1

newdata = json.dumps(data, indent=4)
print(f"Our demo.json file is updated: {newdata}")

with open(f"{cluster_dir}/{cluster_name}.json", 'w') as file:
    file.write(newdata)
    
command = (f"cluster init {cluster_name}")
init=util_test.run_nc_cmd("This command should initialize a cluster based on the json file", command, f"{home_dir}")
print(f"init = {init.stdout}\n")
print("*"*100)

###
print("We're about to start setting permissions")
###

## Before using psql, we'll source environment variables:
node_num = "n1"
res=util_test.source_pg_env(cluster_dir, pgv, node_num);
print("*"*100)

## It looks like there is a bug, wherein the password for lcusr is lost/not set in a multi-db cluster setup.

node_num = "n1"
res=util_test.source_pg_env(cluster_dir, pgv, node_num);

value = util_test.write_psql("ALTER ROLE lcusr LOGIN PASSWORD 'password';","127.0.0.1","lcdb","6432","password","alice")
print(value)

value = util_test.write_psql("ALTER ROLE lcusr LOGIN PASSWORD 'password';","127.0.0.1","lcdb","6433","password","alice")
print(value)

## Create a database superuser (we're about to take superuser privs away from lcusr, so use dbsuperuser to log in for diagnostics):

value = util_test.write_psql("CREATE ROLE dbsuperuser WITH SUPERUSER LOGIN PASSWORD 'password';","127.0.0.1","lcdb","6432","password","alice")

print(f"We're creating a database superuser here: {value}")

value = util_test.write_psql("CREATE  ROLE dbsuperuser WITH SUPERUSER LOGIN PASSWORD 'password';","127.0.0.1","alicesdb","6433","password","alice")
print(f"We're creating a database superuser here: {value}")



## Set permissions for Alice and lcusr:

value = util_test.write_psql("ALTER ROLE alice WITH NOSUPERUSER;","127.0.0.1","alicesdb","6432","password","alice")

value = util_test.write_psql("ALTER ROLE lcusr WITH NOSUPERUSER;","127.0.0.1","lcdb","6432","password","lcusr")

value = util_test.write_psql("ALTER ROLE alice WITH NOSUPERUSER;","127.0.0.1","alicesdb","6433","password","alice")

value = util_test.write_psql("ALTER ROLE lcusr WITH NOSUPERUSER;","127.0.0.1","lcdb","6433","password","lcusr")

## Revoke connect:

value = util_test.write_psql("REVOKE CONNECT ON DATABASE alicesdb FROM PUBLIC;","127.0.0.1","alicesdb","6432","password","alice")

value = util_test.write_psql("REVOKE CONNECT ON DATABASE lcdb FROM PUBLIC;","127.0.0.1","lcdb","6432","password","lcusr")

value = util_test.write_psql("REVOKE CONNECT ON DATABASE alicesdb FROM PUBLIC;","127.0.0.1","alicesdb","6433","password","alice")

value = util_test.write_psql("REVOKE CONNECT ON DATABASE lcdb FROM PUBLIC;","127.0.0.1","lcdb","6433","password","lcusr")


## Create Alice's table on nodes 1 and 2: 

value = util_test.write_psql("CREATE TABLE IF NOT EXISTS alicestable (employeeID INT PRIMARY KEY,employeeName VARCHAR(40),employeeMail VARCHAR(40));","127.0.0.1","alicesdb","6432","password","alice")

value = util_test.write_psql("INSERT INTO alicestable VALUES (1,'a', 'b');","127.0.0.1","alicesdb","6432","password","alice")

value = util_test.write_psql("CREATE TABLE IF NOT EXISTS alicestable (employeeID INT PRIMARY KEY,employeeName VARCHAR(40),employeeMail VARCHAR(40));","127.0.0.1","alicesdb","6433","password","alice")

value = util_test.write_psql("INSERT INTO alicestable VALUES (1,'a', 'b');","127.0.0.1","alicesdb","6433","password","alice")


## Create lcusr's table on nodes 1 and 2:

value = util_test.write_psql("CREATE TABLE IF NOT EXISTS lcusrstable (employeeID INT PRIMARY KEY,employeeName VARCHAR(40),employeeMail VARCHAR(40));","127.0.0.1","lcdb","6432","password","lcusr")

value = util_test.write_psql("INSERT INTO lcusrstable VALUES (1,'a', 'b');","127.0.0.1","lcdb","6432","password","lcusr")
print(value)

value = util_test.write_psql("CREATE TABLE IF NOT EXISTS lcusrstable (employeeID INT PRIMARY KEY,employeeName VARCHAR(40),employeeMail VARCHAR(40));","127.0.0.1","lcdb","6433","password","lcusr")

value = util_test.write_psql("INSERT INTO lcusrstable VALUES (1,'a', 'b');","127.0.0.1","lcdb","6433","password","lcusr")
print(value)

## Query the tables:

value = util_test.write_psql("SELECT * FROM alicestable;","127.0.0.1","alicesdb","6432","password","alice")

value = util_test.write_psql("SELECT * FROM alicestable;","127.0.0.1","alicesdb","6433","password","alice")

value = util_test.write_psql("SELECT * FROM lcusrstable;","127.0.0.1","lcdb","6432","password","lcusr")

value = util_test.write_psql("SELECT * FROM lcusrstable;","127.0.0.1","lcdb","6433","password","lcusr")

## Confirm that alice cannot query lcusr's tables, and vice versa:

value = util_test.write_nofail_psql("SELECT * FROM lcusrstable;","127.0.0.1","lcdb","6432","password","alice")

print(f"This command should show a failure to connect: ")

value = util_test.write_nofail_psql("SELECT * FROM lcusrstable;","127.0.0.1","lcdb","6433","password","alice")
print(f"This command should show a failure to connect: ")

value = util_test.write_nofail_psql("SELECT * FROM alicestable;","127.0.0.1","alicesdb","6432","password","lcusr")
print(f"This command should show a failure to connect: ")

value = util_test.write_nofail_psql("SELECT * FROM alicestable;","127.0.0.1","alicesdb","6433","password","lcusr")
print(f"This command should show a failure to connect: ")


print(f"home_dir = {home_dir}\n")
command2 = (f"cluster replication-check {cluster_name}")
res2=util_test.run_nc_cmd("This command should tell us about our cluster", command2, f"{home_dir}")
print(f"res2 = {res2}\n")



## Check for needles in the haystack; this scenario only works for our current download version.
#
# res2 should include: "There were one or more errors while connecting to databases" or "relation "public.lcusrstable" does not exist"
#

if res2.returncode != 0:

    util_test.EXIT_FAIL()
       
