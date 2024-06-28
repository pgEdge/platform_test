import sys, os, util_test, subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")

## Error Handling Tests for `ace schema-diff`

# Non-Existent Cluster Name
cmd_node = f"ace schema-diff not_real all public"
res=util_test.run_cmd("Invalid Node Name", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 0 or "cluster not found" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Wrong Cluster Name", 1) 
print("*" * 100)

# Non-Existent Node Name
cmd_node = f"ace spock-diff {cluster} fake1,fake2 public"
res=util_test.run_cmd("Invalid Node Name", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 0 or "Specified nodename \"fake1\" not present in cluster" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Wrong Node Names", 1) 
print("*" * 100)

# Non-Existent Schema Name
cmd_node = f"ace schema-diff {cluster} all not_real"
res=util_test.run_cmd("unqualified-schema", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 0 or "Schema not_real does not exist" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Wrong Schema Name", 1) 
print("*" * 100)

# Only One Node Given
cmd_node = f"ace spock-diff {cluster} n1 public"
res=util_test.run_cmd("Invalid Node Name", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 0 or "spock-diff needs at least two nodes to compare" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - One Node", 1) 
print("*" * 100)

# Same Node Given Twice
# cmd_node = f"ace spock-diff {cluster} n1,n1 public"
# res=util_test.run_cmd("Invalid Node Name", cmd_node, f"{home_dir}")
# util_test.printres(res)
# if res.returncode == 0 or "spock-diff needs at least two nodes to compare" not in res.stdout:
#     util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Similar Node Names", 1) 
# print("*" * 100)

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
