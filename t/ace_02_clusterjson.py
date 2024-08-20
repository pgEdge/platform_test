import sys, os, util_test, subprocess
import json, datetime, getpass

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

cluster_name = os.getenv("EDGE_CLUSTER")
admin_name = os.getenv("EDGE_USERNAME")
admin_pswd = os.getenv("EDGE_PASSWORD")
db_name = os.getenv("EDGE_DB")
pg_vers = os.getenv("EDGE_INST_VERSION")
num_nodes=int(os.getenv("EDGE_NODES"))
start_port = int(os.getenv("EDGE_START_PORT"))
host_addr = os.getenv("EDGE_HOST")
cluster_dir = os.getenv("EDGE_CLUSTER_DIR")


## Creates json file to allow certain tests to work
filename = os.path.join(cluster_dir, f"{cluster_name}.json")

## Reads from existing cluster json (should already exist as by `cluster_1_gen_json.py`)
if not os.path.exists(filename):
    util_test.exit_message(f"Couldn't find cluster json by name : {filename}")

with open(filename, "r") as file:
    data = json.load(file)

## Modifies data to add addional databases and users
data["pgedge"]["databases"] += [
    {
        "db_name": "alicesdb",
        "db_user": "alice",
        "db_password": "password",
    },
    {
        "db_name": "carolsdb",
        "db_user": "alice",
        "db_password": "password",
    },
]

## Writes back to file
with open(filename, "w") as file:
    json.dump(data, file)
print(f"Edited contents of {filename}")

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)