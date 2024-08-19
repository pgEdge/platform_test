import sys, os, util_test, subprocess, json, shutil, pprint

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


## Get the current working directory
current_directory = os.getcwd()
print(f"Current Working Directory: {current_directory}")

## Meet prerequisite: add export PGBACKREST_REPO1_CIPHER_PASS=YourCipherPassHere to ~/.bashrc

# Check the ~/.bashrc file for the pgBackRest command and add it if it's missing:
export_pgbackrest = 'export PGBACKREST_REPO1_CIPHER_PASS=YourCipherPassHere'
bashrc_path = os.path.expanduser('~/.bashrc')

# Read the .bashrc file
with open(bashrc_path, 'r') as file:
    lines = file.readlines()

# Check if the line is already in the file and add it if it is not
if export_pgbackrest + '\n' not in lines:
    # If not, append it to the file
    with open(bashrc_path, 'a') as file:
        file.write(export_pgbackrest + '\n')
    print(f"pgBackRest export statement added to {bashrc_path}.")
else:
    print("The pgBackRest export statement is already in the .bashrc file.")


## Meet prerequisite: Delete any pgBackRest artifacts with: rm -rf /etc/pgbackrest

directory = '/etc/pgbackrest'
print(directory)

if os.path.exists(directory):
    shutil.rmtree(directory)
    print(f'Directory {directory} removed successfully.')
else:
    print(f'Directory {directory} does not exist.')

## Create the json file for n4:

data = {'json_version': 1.0, 'node_groups': [{'ssh': {'os_user': 'ec2-user', 'private_key': ''}, 'name': 'n4', 'is_active': 'on', 'public_ip': '127.0.0.1', 'private_ip': '127.0.0.1',
'port': '6435', 'path': '/home/ec2-user/work/platform_test/nc/pgedge/cluster/demo/n4'}]}

file_name = 'n4.json'

## Write the node description to the JSON file
with open(file_name, 'w') as json_file:
    json.dump(data, json_file, indent=4)

## Move the n4.json file to home_dir:

source = (f"n4.json")
target = (f"{home_dir}/n4.json")
#print(f"home_dir = {home_dir}\n")
print(f"We need to copy that file to: {home_dir}")
shutil.move(source, target)
print("*"*100)


## Then invoke cluster add-node:

data_source = "n1"
data_target = "n4"

command = (f"cluster add-node {cluster_name} {data_source} {data_target}")
init=util_test.run_nc_cmd("This command should initialize a cluster based on the json file", command, f"{home_dir}")
#print(f"init = {init.stdout}\n")
print("*"*100)


## Needle and Haystack - Confirm the command worked by looking for:

check=util_test.contains((init.stdout),"sub_n4n2")
print("*"*100)

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)

