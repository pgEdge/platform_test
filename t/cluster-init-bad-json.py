import sys, os, util_test,subprocess

# Print Script
print(f"Starting - {os.path.basename(__file__)}")

# Get Test Settings
util_test.set_env()
repo=os.getenv("EDGE_REPO")
pgv=os.getenv("EDGE_INST_VERSION")
num_nodes=int(os.getenv("EDGE_NODES",2))
home_dir=os.getenv("EDGE_HOME_DIR")
cluster_dir=os.getenv("EDGE_CLUSTER_DIR")
cluster_name=os.getenv("EDGE_CLUSTER","demo")
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","lcusr")
pw=os.getenv("EDGE_PASSWORD","password")
host=os.getenv("EDGE_HOST","localhost")
repuser=os.getenv("EDGE_REPUSER","repuser")
repset=os.getenv("EDGE_REPSET","demo-repset")
spockpath=os.getenv("EDGE_SPOCK_PATH")
dbname=os.getenv("EDGE_DB","lcdb")

tmpcluster = "holdings"
file_name = (f"{tmpcluster}.json")

#
# Use cluster json-template to create a template file:
# 
print(f"home_dir = {home_dir}\n")
command = (f"cluster json-template {tmpcluster} {dbname} {num_nodes} {usr} {pw} {pgv} {port}")
res=util_test.run_nc_cmd("This command should create a json file", command, f"{home_dir}")
print(f"res = {res}\n")
print("*"*100)

#
# Use cluster init to initialize the cluster defined in the template file.
# This will throw an error because both ports in the json file are the same.
# 
command = (f"cluster init {tmpcluster}")
res=util_test.run_nc_cmd("This command attempts to initialize the cluster", command, f"{home_dir}")
print(f"res = {res.stdout}\n")
print("*"*100)

if res.returncode == 1 and "ERROR" in res.stdout:
    print("This case returns: ERROR: Cannot install over a non-empty 'pgedge' directory. The JSON file is unmodified, so it installs twice into the same port")
    util_test.py.EXIT_PASS

