import sys, os, util_test, subprocess
from ace_util import diff_assert_match, diff_assert_mismatch, diff_assert_fail
import ace_util

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")

## Basic Functionality Tests for `ace table-diff`


# Matching Tables
if not diff_assert_match("foo"):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Tables Match")
print("*" * 100)

# Non-Matching Tables
if not diff_assert_mismatch("foo_diff_data"):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Table Mismatch", 1)
print("*" * 100)

# Different Rows
if not diff_assert_mismatch("foo_diff_row"):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Diff Rows", 1)
print("*" * 100)

# No Primary Keys
if not diff_assert_fail("foo_nopk", ace_util.DIFF_ERR_NOPKEY):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - No pk", 1)
print("*" * 100)


util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
