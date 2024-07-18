import sys, os, util_test, subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")
repset = "default"

## Basic Functionality Tests for `ace repset-diff`

# Note: relies on populated repset to run so cannot be run in ace_basic
#       can run successfully in ace_long

# Matching Repsets
cmd_node = f"ace repset-diff {cluster} {repset}"
res=util_test.run_cmd("repset-diff", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH OK" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Matching Repsets", 1)
print("*" * 100)

# Non-Matching Repsets
# cmd_node = f"ace repset-diff {cluster} {repset}"
# res=util_test.run_cmd("repset-diff", cmd_node, f"{home_dir}")
# util_test.printres(res)
# if res.returncode == 1 or "TABLES DO NOT MATCH" not in res.stdout:
#     util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Diff Data", 1)
# print("*" * 100)

## Additional Arguments Functionality Tests for `ace repset-diff`

# Blocks Rows Given
cmd_node = f"ace repset-diff {cluster} {repset} --block_rows=1001"
res=util_test.run_cmd("block_rows > 1000", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Block Rows", 1)
print("*" * 100)

# Max CPU Ratio Given
cmd_node = f"ace repset-diff {cluster} {repset} --max_cpu_ratio=1"
res=util_test.run_cmd("max_cpu_ratio is 1", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Max CPU Ratio", 1)
print("*" * 100)

# Max CPU float < 1
cmd_node = f"ace repset-diff {cluster} {repset} --max_cpu_ratio=0.5"
res=util_test.run_cmd("max-cpu float < 1", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH OK" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Max CPU Ratio < 1", 1) 
print("*" * 100)

# Output Format Given
cmd_node = f"ace repset-diff {cluster} {repset} --output=json"
res=util_test.run_cmd("output in json form", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Output JSON", 1)
print("*" * 100)

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
