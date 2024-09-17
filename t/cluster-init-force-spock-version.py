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
spockver=("EDGE_SPOCK_VER","3.3.6")
dbname=os.getenv("EDGE_DB","lcdb")

cwd=os.getcwd()

## Set the number of nodes and spock version here to override the config.env variables:
num_nodes=3 
spockversion="3.3.6"

#print("*"*100)

print(f"home_dir = {home_dir}\n")
command = (f"cluster json-template {cluster_name} {dbname} {num_nodes} {usr} {pw} {pgv} {port}")
res=util_test.run_nc_cmd("This command should create a json file that defines a cluster", command, f"{home_dir}")
print(f"res = {res}\n")

# We're forcing the version of Spock in our .json file:
new_spock = (f"{spockversion}")
new_path_0 = (f"{cwd}/{cluster_dir}/n1")
new_path_1 = (f"{cwd}/{cluster_dir}/n2")
new_path_2 = (f"{cwd}/{cluster_dir}/n3")


with open(f"{cluster_dir}/{cluster_name}.json", 'r') as file:
    data = json.load(file)
    #print(data)
    data["pgedge"]["spock"]["spock_version"] = new_spock
    data["node_groups"][0]["path"] = new_path_0
    data["node_groups"][1]["path"] = new_path_1
    data["node_groups"][2]["path"] = new_path_2

newdata = json.dumps(data, indent=4)
with open(f"{cluster_dir}/{cluster_name}.json", 'w') as file:
    file.write(newdata)
    

command = (f"cluster init {cluster_name}")
init=util_test.run_nc_cmd("This command should initialize a cluster based on the json file", command, f"{home_dir}")
print(f"init = {init.stdout}\n")
print("*"*100)


# Needle and Haystack
# Confirm the command worked by looking for:

if "[FAILED]" not in str(init.stdout) or init.returncode == 1:

    util_test.EXIT_PASS()
else:
    util_test.EXIT_FAIL()



