import sys, os, util_test, subprocess, json

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
repuser=os.getenv("EDGE_REPUSER","susan")
repset=os.getenv("EDGE_REPSET","demo-repset")
spockpath=os.getenv("EDGE_SPOCK_PATH")
dbname=os.getenv("EDGE_DB","lcdb")

cwd=os.getcwd()
num_nodes=3
rm_node='n3'

#print("*"*100)

print(f"home_dir = {home_dir}\n")
command = (f"cluster list-nodes {cluster_name}")
res=util_test.run_nc_cmd("Exercise the list-nodes command", command, f"{home_dir}")
print(f"Command: {command}")
print(f"The list-nodes command returns = {res}\n")
print("*"*100)

# Needle and Haystack
# Confirm the command worked by looking for:

if "CompletedProcess" in str(res) and res.returncode == 0:
    
    util_test.EXIT_PASS()
else:
    util_test.EXIT_FAIL()




