import sys, os, util_test, subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")


## Error Handling Tests for `ace table-rerun`

# First Call Table Diff to get a Diff File
cmd_node = f"ace table-diff {cluster} public.foo_diff_data"
res=util_test.run_cmd("table-diff", cmd_node, f"{home_dir}")
diff_file_local, diff_data = util_test.get_diff_data(res.stdout)

# Non-Existent Cluster Name
cmd_node = f"ace table-rerun notreal {diff_file_local} public.foo_diff_data"
res=util_test.run_cmd("table-rerun", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 0 or "cluster not found" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Wrong Cluster Name", 1) 
print("*" * 100)

# Non-Existent Diff File
cmd_node = f"ace table-rerun {cluster} notreal.json public.foo_diff_data"
res=util_test.run_cmd("table-rerun", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 0 or "Diff file notreal.json not found" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Wrong Cluster Name", 1) 
print("*" * 100)

# Non-Existent Table Name
cmd_node = f"ace table-rerun {cluster} {diff_file_local} public.foo_not_real"
res=util_test.run_cmd("table-rerun", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 0 or "Invalid table name 'public.foo_not_real'" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Wrong Cluster Name", 1) 
print("*" * 100)

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
