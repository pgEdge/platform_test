import sys, os, util_test, subprocess
import time

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

## Basic Functionality Tests for `ace spock-table-rerun`

# First Call Table Diff to get a Diff File
cmd_node = f"ace table-diff {cluster} public.foo_diff_data"
res=util_test.run_cmd("table-diff", cmd_node, f"{home_dir}")
diff_file_local, diff_data = util_test.get_diff_data(res.stdout)

# print(json.dumps(diff_data, indent=2))
# {
#   "n1/n2": {
#     "n1": [
#       {
#         "employeeid": "1",
#         "employeename": "Carol",
#         "employeemail": "carol@pgedge.com"
#       },
#       {
#         "employeeid": "2",
#         "employeename": "Bob",
#         "employeemail": "bob@pgedge.com"
#       }
#     ],
#     "n2": [
#       {
#         "employeeid": "1",
#         "employeename": "Alice",
#         "employeemail": "alice@pgedge.com"
#       },
#       {
#         "employeeid": "2",
#         "employeename": "Carol",
#         "employeemail": "carol@pgedge.com"
#       }
#     ]
#   }
# }

# Ensures that diff file names don't match
time.sleep(1)

# First run on non-matching info
cmd_node = f"ace table-rerun {cluster} {diff_file_local} public.foo_diff_data"
res=util_test.run_cmd("table-rerun", cmd_node, f"{home_dir}")
diff_file_local_2, diff_data_2 = util_test.get_diff_data(res.stdout)
util_test.printres(res)
if res.returncode == 1 or "FOUND DIFFS BETWEEN NODES" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Non-Matching Rerun", 1)
print("*" * 100)

if not util_test.compare_structures(diff_data, diff_data_2):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Rerun didn't return same structure as table-diff", 1)

# Make files match by changing the information in the second one
if not util_test.write_psql("UPDATE foo_diff_data SET employeename = 'Carol', employeemail = 'carol@pgedge.com' WHERE employeeid = 1",host,dbname,port+1,pw,usr) == 0:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Could not edit tables", 1)
if not util_test.write_psql("UPDATE foo_diff_data SET employeename = 'Bob', employeemail = 'bob@pgedge.com' WHERE employeeid = 2",host,dbname,port+1,pw,usr) == 0:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Could not edit tables", 1)

# Ensures that diff file names don't match
time.sleep(1)

# Run with now matching info
cmd_node = f"ace table-rerun {cluster} {diff_file_local} public.foo_diff_data"
res=util_test.run_cmd("table-rerun", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH OK" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Matching Rerun by Update", 1)
print("*" * 100)

# Drop one of the rows from both tables (TODO: make work with any amount of nodes in cluster)
if not util_test.write_psql("DELETE FROM foo_diff_data WHERE employeeid = 2",host,dbname,port,pw,usr) == 0:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Could not delete from tables", 1)
if not util_test.write_psql("DELETE FROM foo_diff_data WHERE employeeid = 2",host,dbname,port+1,pw,usr) == 0:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Could not delete from tables", 1)

# Ensures that diff file names don't match
time.sleep(1)

# Run with dropped row
cmd_node = f"ace table-rerun {cluster} {diff_file_local} public.foo_diff_data"
res=util_test.run_cmd("table-rerun", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH OK" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Matching Rerun by Delete", 1)
print("*" * 100)

# Recreate old environment for future tests
if not util_test.write_psql("INSERT INTO foo_diff_data values(2, 'Bob', 'bob@pgedge.com')",host,dbname,port,pw,usr) == 0:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Could not insert into tables", 1)
if not util_test.write_psql("UPDATE foo_diff_data SET employeename = 'Alice', employeemail = 'alice@pgedge.com' WHERE employeeid = 1",host,dbname,port+1,pw,usr) == 0:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Could not edit tables", 1)
if not util_test.write_psql("INSERT INTO foo_diff_data values(2, 'Carol', 'carol@pgedge.com')",host,dbname,port+1,pw,usr) == 0:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Could not insert into tables", 1)

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
