import sys, os, util_test, subprocess
import time

from ace_util import rerun_assert_match, rerun_assert_mismatch, diff_assert_mismatch
from json import load

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
num_nodes=int(os.getenv("EDGE_NODES",2))
pgdir=os.getenv("EDGE_HOME_DIR")

## Basic Functionality Tests for `ace table-rerun`

# First Call Table Diff to get a Diff File
found_mismatch, diff_file_local = diff_assert_mismatch("foo_diff_data", get_diff=True, quiet=True)
if not found_mismatch:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Non-Matching Diff")


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

# First run on non-matching info
found_mismatch, diff_file_local_2 = rerun_assert_mismatch("foo_diff_data", diff_file_local, get_diff=True)
if not found_mismatch:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Non-Matching Rerun")

with open(os.path.join(pgdir, diff_file_local), "r") as file1, open(os.path.join(pgdir, diff_file_local_2), "r") as file2:
    if not util_test.compare_structures(load(file1), load(file2)):
        util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Rerun didn't return same structure as table-diff")

# Make files match by changing the information in the second one
if not util_test.write_psql("UPDATE foo_diff_data SET employeename = 'Carol', employeemail = 'carol@pgedge.com' WHERE employeeid = 1",host,dbname,port+1,pw,usr) == 0:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Could not edit tables")
if not util_test.write_psql("UPDATE foo_diff_data SET employeename = 'Bob', employeemail = 'bob@pgedge.com' WHERE employeeid = 2",host,dbname,port+1,pw,usr) == 0:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Could not edit tables")

# Run with now matching info
if not rerun_assert_match("foo_diff_data", diff_file_local):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Matching Rerun by Update")

# Drop one of the rows from both tables
for n in range(1,num_nodes+1):
    if not util_test.write_psql("DELETE FROM foo_diff_data WHERE employeeid = 2",host,dbname,port+n-1,pw,usr) == 0:
        util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Could not delete from tables")

# Run with dropped row
if not rerun_assert_match("foo_diff_data", diff_file_local):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Matching Rerun by Delete")

# Recreate old environment for future tests
if not util_test.write_psql("INSERT INTO foo_diff_data values(2, 'Bob', 'bob@pgedge.com')",host,dbname,port,pw,usr) == 0:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Could not insert into tables")
if not util_test.write_psql("UPDATE foo_diff_data SET employeename = 'Alice', employeemail = 'alice@pgedge.com' WHERE employeeid = 1",host,dbname,port+1,pw,usr) == 0:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Could not edit tables")
if not util_test.write_psql("INSERT INTO foo_diff_data values(2, 'Carol', 'carol@pgedge.com')",host,dbname,port+1,pw,usr) == 0:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Could not insert into tables")

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
