import sys, os, util_test, subprocess, json

# Print Script
print(f"Starting - {os.path.basename(__file__)}")

# Get Test Settings
util_test.set_env()
repo=os.getenv("EDGE_REPO")
cluster_dir=os.getenv("EDGE_CLUSTER_DIR")
home_dir=os.getenv("EDGE_HOME_DIR")
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","lcusr")
pw=os.getenv("EDGE_PASSWORD","password")
dbname=os.getenv("EDGE_DB","lcdb")

# Get a list of available packages - the list is returned in a json string:
get_list=("um list --json")
res=util_test.run_nc_cmd("Getting list of available packages", get_list, f"{home_dir}")
# Break the json string into a list:
res = json.loads(res.stdout)

# Loop through the results and remove each component:
for i, inner_list in enumerate(res): 
    comp=(res[i].get("component"))
    remove_comp=(f"um remove {comp} --rm-data")
    remove_res=util_test.run_nc_cmd("Removing components", remove_comp, f"{home_dir}")

# UM List the components:
list=(f"um list")
list_res=util_test.run_nc_cmd("Getting list of packages", list, f"{home_dir}")
print(list_res.stdout)


# Needle and Haystack
#Check for a returncode to confirm results:

if remove_res.returncode != 0:
    util_test.EXIT_FAIL
else:
    util_test.EXIT_PASS


