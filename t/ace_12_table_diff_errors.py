import sys, os, util_test, subprocess
from ace_util import diff_assert_fail
import ace_util

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")

## Error Handling Tests for `ace table-diff


# Non-Existent Cluster Name
if not diff_assert_fail("", ace_util.DIFF_ERR_NOCLUSTER, call_override="ace table-diff dem public.foo"):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - cluster not found", 1) 
print("*" * 100)

# Non-Existent Table Name
if not diff_assert_fail("fo", ace_util.DIFF_ERR_NOTABLE.format( table_name = "public.fo" )):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Invalid Table", 1) 
print("*" * 100)

# Non-Existent Schema Name
if not diff_assert_fail("", ace_util.DIFF_ERR_NOTABLE.format( table_name = "pablic.foo" ), call_override=f"ace table-diff {cluster} pablic.foo"):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Invalid Table", 1) 
print("*" * 100)

# Non Existent Database Name
if not diff_assert_fail("foo", ace_util.DIFF_ERR_NODB.format( db_name = "not_real", cluster = cluster ), args={"--dbname": "not_real"}):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Database Name", 1)
print("*" * 100)

# Block Rows < 1000
if not diff_assert_fail("foo", ace_util.DIFF_ERR_SMALLBR, args={"--block_rows": 999}):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Block Rows", 1) 
print("*" * 100)

# Max CPU ratio > 1
if not diff_assert_fail("foo", ace_util.DIFF_ERR_CPURANGE, args={"--max_cpu_ratio": 2}):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Block Rows", 1)
print("*" * 100)

# Max CPU is String
if not diff_assert_fail("foo", ace_util.DIFF_ERR_CPUTYPE, args={"--max_cpu_ratio": "ONE"}):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Max CPU Ratio", 1)
print("*" * 100)

# Max CPU float > 1
if not diff_assert_fail("foo", ace_util.DIFF_ERR_CPURANGE, args={"--max_cpu_ratio": 1.5}):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Max CPU Ratio > 1", 1)
print("*" * 100)

# Unsupported Output Format
if not diff_assert_fail("foo", ace_util.DIFF_ERR_OUTPUTF, args={"--output": "html"}):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Output HTML", 1)
print("*" * 100)

# Same Nodename (note that this case errors because the removal of repeated nodes leaves one node being compared)
if not diff_assert_fail("foo", ace_util.DIFF_ERR_DUPNODE, args={"--nodes": "n1,n1"}):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Same Nodename", 1)
print("*" * 100)

# Unauthorized Database Name
if not diff_assert_fail("foo", ace_util.DIFF_ERR_NOTABLE.format( table_name = "public.foo" ), args={"--dbname": "carolsdb"}):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Database Unauthorized", 1)
print("*" * 100)


util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
