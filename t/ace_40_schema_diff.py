import sys, os, util_test, subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")

## Basic Functionality Tests for `ace schema-diff`

# Matching Information
cmd_node = f"ace schema-diff {cluster} all public"
res=util_test.run_cmd("schema-diff", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "SCHEMAS ARE THE SAME" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Matching Schema", 1)
print("*" * 100)

# Non-Matching Information
# cmd_node = f"ace schema-diff {cluster} all public"
# res=util_test.run_cmd("schema-diff", cmd_node, f"{home_dir}")
# util_test.printres(res)
# if res.returncode == 1 or "SCHEMAS ARE THE SAME" not in res.stdout:
#     util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Non-Matching Schema", 1)
# print("*" * 100)


util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
