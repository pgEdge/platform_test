import sys, os, util_test, subprocess
import time

from util_datagen import generate_table, remove_table, insert_into
from ace_util import diff_assert_match, diff_assert_mismatch, rerun_assert_match, rerun_assert_diff_count

import spock_1_setup
import spock_2_node_create
import spock_3_sub_create
import spock_4_repset_add_table

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")

# This file exists to test table-rerun as a way to notice that network delay has caused
# table-diff to report errors where there are none. The steps for this are as follows
#   1: set up a replicating cluster with 15s delay added to the subscriptions
#   2: insert 10 values into n1, wait 5s
#   3: insert 10 values into n1, wait 5s
#   4: run table-diff  (expect 20 diffs)
#   5: run table-rerun (expect 20 diffs), wait 6s
#   6: run table-rerun (expect 10 diffs), wait 5s
#   7: run table-rerun (expect tables match)


# Start by generating a basic table to use
table_name = "t1"
form = [
    ("name", "VARCHAR(255)"),
    ("val_1", "BIGINT"),
    ("val_2", "BIGINT"), ]
generate_table(table_name, form, 10000)

# Assert that this is replicated throughout
if not diff_assert_match(table_name):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Matching Tables")


# Step 1:
os.environ["SPOCK_DELAY"] = "25"
spock_1_setup.run()
spock_2_node_create.run()
spock_3_sub_create.run()
spock_4_repset_add_table.run()


# Step 2:
start = time.time()
print(time.time())
insert_into("t1", form, 10, nodes=[1])
time.sleep(5.0 + start - time.time())


# Step 3:
print(time.time())
insert_into("t1", form, 10, nodes=[1])
time.sleep(10.0 + start - time.time())


# Step 4:
print(time.time())
found_mismatch, diff_file = diff_assert_mismatch(table_name, get_diff=True)
if not found_mismatch:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - 20 Diffs")


# Step 5:
print(time.time())
if not rerun_assert_diff_count(table_name, diff_file, 20):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Non-Matching Rerun")
time.sleep(16.0 + start - time.time())


# Step 6:
print(time.time())
if not rerun_assert_diff_count(table_name, diff_file, 10):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Non-Matching Rerun")
time.sleep(21.0 + start - time.time())


# Step 7:
print(time.time())
if not rerun_assert_match(table_name, diff_file):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Matching Rerun")


# Cleanup
remove_table("t1")
os.environ.pop("SPOCK_DELAY")
import spock_99_cleanup


util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
