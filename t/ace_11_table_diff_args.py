import sys, os, util_test, subprocess
from ace_util import diff_assert_match

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")
db_name = os.getenv("EDGE_DB")

## Additional Arguments Functionality Tests for `ace table-diff`


# Blocks Rows Given
if not diff_assert_match("foo", args={"--block_rows": 1001}):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Block Rows")
print("*" * 100)

# Max CPU float < 1
if not diff_assert_match("foo", args={"--max_cpu_ratio": 0.5}):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Max CPU Ratio < 1", 1) 
print("*" * 100)

# Output Format Given
if not diff_assert_match("foo", args={"--output": "json"}):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Output JSON", 1)
print("*" * 100)

# Database Given (1)
if not diff_assert_match("foo", args={"--dbname": db_name}):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Database Given", 1)
print("*" * 100)

# Database Given (2)
if not diff_assert_match("foo", args={"--dbname": "alicesdb"}):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Database Given New User", 1)
print("*" * 100)


util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
