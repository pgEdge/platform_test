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
command = (f"cluster replication-check {cluster_name}")
res=util_test.run_nc_cmd("This command should tell us about our cluster", command, f"{home_dir}")
print(f"res = {res}\n")


print(f"home_dir = {home_dir}\n")
command2 = (f"ace table-diff demo public.alicestable --dbname=alicesdb")
res2=util_test.run_nc_cmd("Running an ace command", command2, f"{home_dir}")
print(f"Checking alicestable with ace = {res2}\n")


print(f"home_dir = {home_dir}\n")
command3 = (f"ace table-diff demo public.lcusrstable --dbname=lcdb")
res3=util_test.run_nc_cmd("Running an ace command", command3, f"{home_dir}")
print(f"Checking lcusrstable with ace = {res3}\n")

