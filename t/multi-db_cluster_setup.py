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

cwd=os.getcwd()

#print("*"*100)

print(f"home_dir = {home_dir}\n")
command = (f"cluster json-template {cluster_name} {dbname} {num_nodes} {usr} {pw} {pgv} {port}")
res=util_test.run_nc_cmd("This command should create a json file that defines a cluster", command, f"{home_dir}")
print(f"res = {res}\n")

## Before we can update the demo.json file, we need to add dictionary entries to hold the extra
#  database that QubeRT is using:

# load the demo.json file:
with open(f"{cluster_dir}/{cluster_name}.json", "r") as file:
    file_data = json.loads(file.read())

# add one extra database dictionary to the file:

new_dict = [{"username": "alice","password": "password","name": "alicesdb"},{"username": "lcusr","password": "password","name": "lcdb"}]

file_data["database"]["databases"]=new_dict

# write the file back
with open(f"{cluster_dir}/{cluster_name}.json", "w") as file:
    file.write(json.dumps(file_data))

# The following set of commands update the arrays specified in our json file that we just created.
# The first entry in the array is referred to as '0', then '1', etc.
# The QubeRT issue uses a three node cluster, but we're doing the same basic test with a two-node
# cluster.

new_address_0 = '127.0.0.1'
new_address_1 = '127.0.0.1'
new_port_0 = port
new_port_1 = port + 1
new_path_0 = (f"{cwd}/{cluster_dir}/n1")
new_path_1 = (f"{cwd}/{cluster_dir}/n2")

with open(f"{cluster_dir}/{cluster_name}.json", 'r') as file:
    data = json.load(file)
    #print(data)
    data["remote"]["os_user"] = repuser
    data["node_groups"]["remote"][0]["nodes"][0]["ip_address"] = new_address_0
    data["node_groups"]["remote"][1]["nodes"][0]["ip_address"] = new_address_1
    data["node_groups"]["remote"][0]["nodes"][0]["port"] = new_port_0
    data["node_groups"]["remote"][1]["nodes"][0]["port"] = new_port_1
    data["node_groups"]["remote"][0]["nodes"][0]["path"] = new_path_0
    data["node_groups"]["remote"][1]["nodes"][0]["path"] = new_path_1

newdata = json.dumps(data, indent=4)
with open(f"{cluster_dir}/{cluster_name}.json", 'w') as file:
    file.write(newdata)
    
command = (f"cluster init {cluster_name}")
init=util_test.run_nc_cmd("This command should initialize a cluster based on the json file", command, f"{home_dir}")
print(f"init = {init.stdout}\n")
print("*"*100)

print("We're about to start setting permissions")

## It looks like there is a bug, wherein the password for lcusr is lost/not set in a multi-db cluster setup.

value = util_test.write_psql("ALTER ROLE lcusr LOGIN PASSWORD 'password';","127.0.0.1","lcdb","6432","password","alice")
print(value)
print(res.stdout)

value = util_test.write_psql("ALTER ROLE lcusr LOGIN PASSWORD 'password';","127.0.0.1","lcdb","6433","password","alice")
print(value)
print(res.stdout)

## Set permissions for Alice and lcusr:

value = util_test.write_psql("ALTER ROLE alice WITH NOSUPERUSER;","127.0.0.1","alicesdb","6432","password","alice")
print(res.stdout,value)

value = util_test.write_psql("ALTER ROLE lcusr WITH NOSUPERUSER;","127.0.0.1","lcdb","6432","password","lcusr")
print(res.stdout,value)

value = util_test.write_psql("ALTER ROLE alice WITH NOSUPERUSER;","127.0.0.1","alicesdb","6433","password","alice")
print(res.stdout,value)

value = util_test.write_psql("ALTER ROLE lcusr WITH NOSUPERUSER;","127.0.0.1","lcdb","6433","password","lcusr")
print(res.stdout,value)

## Revoke connect:

value = util_test.write_psql("REVOKE CONNECT ON DATABASE alicesdb FROM PUBLIC;","127.0.0.1","alicesdb","6432","password","alice")
print(res.stdout,value)

value = util_test.write_psql("REVOKE CONNECT ON DATABASE lcdb FROM PUBLIC;","127.0.0.1","lcdb","6432","password","lcusr")
print(res.stdout,value)

value = util_test.write_psql("REVOKE CONNECT ON DATABASE alicesdb FROM PUBLIC;","127.0.0.1","alicesdb","6433","password","alice")
print(res.stdout,value)

value = util_test.write_psql("REVOKE CONNECT ON DATABASE lcdb FROM PUBLIC;","127.0.0.1","lcdb","6433","password","lcusr")
print(res.stdout,value)

## Create Alice's table on nodes 1 and 2: 

value = util_test.write_psql("CREATE TABLE IF NOT EXISTS alicestable (employeeID INT PRIMARY KEY,employeeName VARCHAR(40),employeeMail VARCHAR(40));","127.0.0.1","alicesdb","6432","password","alice")
print(res.stdout,value)

value = util_test.write_psql("INSERT INTO alicestable VALUES (1,'a', 'b');","127.0.0.1","alicesdb","6432","password","alice")
print(res.stdout,value)

value = util_test.write_psql("CREATE TABLE IF NOT EXISTS alicestable (employeeID INT PRIMARY KEY,employeeName VARCHAR(40),employeeMail VARCHAR(40));","127.0.0.1","alicesdb","6433","password","alice")
print(res.stdout,value)

value = util_test.write_psql("INSERT INTO alicestable VALUES (1,'a', 'b');","127.0.0.1","alicesdb","6433","password","alice")
print(res.stdout,value)

## Create lcusr's table on nodes 1 and 2:

value = util_test.write_psql("CREATE TABLE IF NOT EXISTS lcusrstable (employeeID INT PRIMARY KEY,employeeName VARCHAR(40),employeeMail VARCHAR(40));","127.0.0.1","lcdb","6432","password","lcusr")
print(res.stdout,value)

value = util_test.write_psql("INSERT INTO lcusrstable VALUES (1,'a', 'b');","127.0.0.1","lcdb","6432","password","lcusr")
print(value)
print(res.stdout)

value = util_test.write_psql("CREATE TABLE IF NOT EXISTS lcusrstable (employeeID INT PRIMARY KEY,employeeName VARCHAR(40),employeeMail VARCHAR(40));","127.0.0.1","lcdb","6433","password","lcusr")
print(res.stdout,value)

value = util_test.write_psql("INSERT INTO lcusrstable VALUES (1,'a', 'b');","127.0.0.1","lcdb","6433","password","lcusr")
print(value)
print(res.stdout)


## Query the tables:

value = util_test.write_psql("SELECT * FROM alicestable;","127.0.0.1","alicesdb","6432","password","alice")
print(res.stdout,value)

value = util_test.write_psql("SELECT * FROM alicestable;","127.0.0.1","alicesdb","6433","password","alice")
print(res.stdout,value)

value = util_test.write_psql("SELECT * FROM lcusrstable;","127.0.0.1","lcdb","6432","password","lcusr")
print(res.stdout,value)

value = util_test.write_psql("SELECT * FROM lcusrstable;","127.0.0.1","lcdb","6433","password","lcusr")
print(res.stdout,value)

## Confirm that alice cannot query lcusr's tables, and vice versa:

value = util_test.write_nofail_psql("SELECT * FROM lcusrstable;","127.0.0.1","lcdb","6432","password","alice")
print(res.stdout,value)

value = util_test.write_nofail_psql("SELECT * FROM lcusrstable;","127.0.0.1","lcdb","6433","password","alice")
print(res.stdout,value)

value = util_test.write_nofail_psql("SELECT * FROM alicestable;","127.0.0.1","alicesdb","6432","password","lcusr")
print(res.stdout,value)

value = util_test.write_nofail_psql("SELECT * FROM alicestable;","127.0.0.1","alicesdb","6433","password","lcusr")
print(res.stdout,value)



