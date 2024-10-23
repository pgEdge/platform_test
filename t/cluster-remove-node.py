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
rm_node='n3'

print(f"home_dir = {home_dir}\n")

# The first two commands should fail with bad cluster and node names:

command = (f"cluster remove-node {repuser} {rm_node}")
res=util_test.run_nc_cmd("This command should fail with a bad cluster name", command, f"{home_dir}")
print(f"Failing command: {command}")
print(f"The failing command returns = {res}\n")
print("*"*100)
if res.returncode == 0:
    util_test.EXIT_FAIL()
print("*"*100)

command1 = (f"cluster remove-node {cluster_name} {repuser}")
res1=util_test.run_nc_cmd("This command should fail with a bad node name", command1, f"{home_dir}")
print(f"Failing command: {command1}")
print(f"The failing command returns = {res1}\n")
print("*"*100)
print(f"The returncode when you don't provide a valid node number is: {res1.returncode}")
if res1.returncode == 1:
    print("This test provides a non-existant node number. For now, we're considering this acceptable behavior")
    util_test.EXIT_FAIL()    
print("*"*100)

# This is the successful command:

command2 = (f"cluster remove-node {cluster_name} {rm_node}")
res2=util_test.run_nc_cmd("This command should remove node n3 and succeed", command2, f"{home_dir}")
print(f"Successful command: {command2}")
print(f"The successful remove-node command returns = {res2}\n")
print("*"*100)
print("This test case only removes the replication artifacts.  The PG installation, data directory, and n3 subdir will remain")

# Needle and Haystack
# Confirm the command worked by looking for:

if "Dropping subscriptions" in str(res2) and res2.returncode == 0:

    util_test.EXIT_PASS()
else:
    util_test.EXIT_FAIL()

