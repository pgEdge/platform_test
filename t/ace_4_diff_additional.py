import os, util_test, subprocess, pathlib
# Get environment variables

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")

#Use the spock-diff command to compare the meta-data on two cluster nodes
cmd_node = f"ace diff-spock {cluster} all"
res=util_test.run_cmd("spock-diff", cmd_node, f"{home_dir}")
print(res)

#Use the diff-schemas command to compare the schemas in a cluster 
cmd_node = f"ace diff-schema {cluster} all public"
res=util_test.run_cmd("schema-diff", cmd_node, f"{home_dir}")
print(res)