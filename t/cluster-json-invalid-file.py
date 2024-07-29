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


## We're going to use names that aren't used by other tests to avoid confusion.
#  This test will also be self-contained...

here = os.getcwd()
tmpcluster = "resources"
file_name = (f"{tmpcluster}.json")
print(here)
print(file_name)
#

# Create a json file that we'll truncate with os.truncate:
print(f"home_dir = {home_dir}\n")
command = (f"cluster json-template {tmpcluster} {dbname} {num_nodes} {usr} {pw} {pgv} {port}")
res=util_test.run_nc_cmd("This command should create a json file that defines a cluster", command, f"{home_dir}")
print(f"res = {res}\n")
print("*"*100)

if res.returncode == 1:
    util_test.EXIT_FAIL

# Corrupt the file with os.truncate:

path=(f"{here}/{home_dir}/cluster/{tmpcluster}/{file_name}")
file_info = os.truncate(path, 150)
print(f"Our test json is located at = {path}")
print(f"After the call to os.truncate the json file contains:")
json = print(open(path).read())

if res.returncode == 1:
    util_test.EXIT_FAIL

# Confirm that if the json template is invalid, cluster json-validate will catch the error:
# 
print(f"home_dir = {home_dir}\n")
command = (f"cluster json-validate {tmpcluster}")
results=util_test.run_nc_cmd("This command should validate a json file that defines a cluster", command, f"{home_dir}")
print(results)
print("*"*100)


if "Expecting property name" in str(results) or results.returncode == 1:

    util_test.EXIT_PASS()
else:
    util_test.EXIT_FAIL()
