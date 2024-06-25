import sys, os, util_test, subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")

## Error Handling Tests for `ace table-repair`

# First Call Table Diff to get a Diff File
cmd_node = f"ace table-diff {cluster} public.foo_diff_data"
res=util_test.run_cmd("table-diff", cmd_node, f"{home_dir}")
diff_file_local, diff_data = util_test.get_diff_data(res.stdout)

# Non-Existent Cluster Name
cmd_node = f"ace table-repair notreal {diff_file_local} n1 public.foo_diff_data"
res=util_test.run_cmd("table-repair", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 0 or "cluster not found" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Table Repair", 1)
print("*" * 100)

# Non-Existent Diff File
cmd_node = f"ace table-repair {cluster} notreal.json n1 public.foo_diff_data"
res=util_test.run_cmd("table-repair", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 0 or "Diff file notreal.json does not exist" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Table Repair", 1)
print("*" * 100)

# Non-Existent Node
cmd_node = f"ace table-repair {cluster} {diff_file_local} w1 public.foo_diff_data"
res=util_test.run_cmd("table-repair", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 0 or "Source of truth node w1 not present in cluster" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Table Repair", 1)
print("*" * 100)

# Non-Existent Table
cmd_node = f"ace table-repair {cluster} {diff_file_local} n1 public.foo_not_real"
res=util_test.run_cmd("table-repair", cmd_node, f"{home_dir}")
print(res)
if res.returncode == 0 or "Invalid table name 'public.foo_not_real'" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Table Repair", 1)
print("*" * 100)

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
