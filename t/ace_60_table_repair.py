import sys, os, util_test, subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")

# num_nodes=int(os.getenv("EDGE_NODES",2))
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","lcusr")
pw=os.getenv("EDGE_PASSWORD","password")
host=os.getenv("EDGE_HOST","localhost")
dbname=os.getenv("EDGE_DB","lcdb")

## Basic Functionality Tests for `ace spock-table-repair`

# First Call Table Diff to get a Diff File
cmd_node = f"ace table-diff {cluster} public.foo_diff_data"
res=util_test.run_cmd("table-diff", cmd_node, f"{home_dir}")
diff_file_local, diff_data = util_test.get_diff_data(res.stdout)

# Calls table repair on the above to fix the data, using n1 as the source of truth
cmd_node = f"ace table-repair {cluster} {diff_file_local} n1 public.foo_diff_data"
res=util_test.run_cmd("table-repair", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or f"Successfully applied diffs to public.foo_diff_data in cluster {cluster}" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Table Repair", 1)
print("*" * 100)

# Calls table diff again to see that there should be no differences
cmd_node = f"ace table-diff {cluster} public.foo_diff_data"
res=util_test.run_cmd("table-diff", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH OK" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Matching Diff by Repair", 1)
print("*" * 100)

# Recreate old environment for future tests
if not util_test.write_psql("UPDATE foo_diff_data SET employeename = 'Alice', employeemail = 'alice@pgedge.com' WHERE employeeid = 1",host,dbname,port+1,pw,usr) == 0:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Could not edit tables", 1)
if not util_test.write_psql("UPDATE foo_diff_data SET employeename = 'Carol', employeemail = 'carol@pgedge.com' WHERE employeeid = 2",host,dbname,port+1,pw,usr) == 0:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Could not edit tables", 1)

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
