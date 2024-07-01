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

## Creates information to write to json
data = {
    "name": cluster_name,
    "style": "localhost",
    "create_date": datetime.datetime.now().strftime('%Y-%m-%d'),
    "localhost": {
        "os_user": getpass.getuser(),
        "ssh_key": "",
    },
    "database": {
        "databases": [
            {
                "username": admin_name,
                "password": admin_pswd,
                "name": db_name,
            },
            {
                "username": "alice",
                "password": "password",
                "name": "alicesdb",
            },
            {
                "username": "alice",
                "password": "password",
                "name": "carolsdb",
            },
        ],
        "pg_version": pg_vers,
        "auto_ddl": "off",
    },
    "node_groups": {
        "localhost": [
            {
                "nodes": [
                    {
                        "name": f"n{n}",
                        "is_active": True,
                        "ip_address": host_addr,
                        "port": start_port + n - 1,
                        "path": os.path.join(cluster_dir, f"n{n}")

                    }
                ]
            }
            for n in range(1,num_nodes+1)
        ]
    }
}

## Creates json file to allow certain tests to work
filename = os.path.join(cluster_dir, f"{cluster_name}.json")
with open(filename, "w") as file:
    json.dump(data, file)

print(f"Wrote data to {filename}")

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)