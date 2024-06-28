import sys, os, util_test, subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")

## Basic Functionality Tests for `ace table-diff`

# Matching Tables
cmd_node = f"ace table-diff {cluster} public.foo"
res=util_test.run_cmd("table-diff", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH OK" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Matching Tables", 1)
print("*" * 100)

# Non-Matching Tables
cmd_node = f"ace table-diff {cluster} public.foo_diff_data"
res=util_test.run_cmd("table-diff", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES DO NOT MATCH" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Diff Data", 1)
print("*" * 100)

# Different Rows
cmd_node = f"ace table-diff {cluster} public.foo_diff_row"
res=util_test.run_cmd("table-diff", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES DO NOT MATCH" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Diff Rows", 1)
print("*" * 100)

# No Primary Keys
cmd_node = f"ace table-diff {cluster} public.foo_nopk"
res=util_test.run_cmd("table-diff", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 0 or "No primary key found" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - No pk", 1)
print("*" * 100)

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
