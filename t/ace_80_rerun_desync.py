import sys, os, util_test, subprocess
import time

from util_datagen import generate_table, remove_table, insert_into
from ace_util import diff_assert_match, diff_assert_mismatch, rerun_assert_match, rerun_assert_diff_count

import spock_1_setup
import spock_2_node_create
import spock_3_sub_create
import spock_4_repset_add_table
import spock_99_cleanup

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")

tries = 0
fails = 0
fail_info = list()

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
tries += 1
if not diff_assert_match(table_name):
    fails += 1
    fail_info.append(f"Fail - {os.path.basename(__file__)} - Matching Tables")


# Step 1:
os.environ["SPOCK_DELAY"] = "30"
spock_1_setup.run()
spock_2_node_create.run()
spock_3_sub_create.run()
spock_4_repset_add_table.run()


# Step 2:
start = time.time()
print(f"---- starting: {time.time()} = 0")
insert_into(table_name, form, 10, nodes=[1])
time.sleep(10.0 + start - time.time())


# Step 3:
print(f"---- Step 3: {time.time() - start}")
insert_into(table_name, form, 10, nodes=[1])
# time.sleep(10.0 + start - time.time())


# Step 4:
print(f"---- Step 4: {time.time() - start}")
found_mismatch, diff_file = diff_assert_mismatch(table_name, get_diff=True)
tries += 1
if not found_mismatch:
    fails += 1
    fail_info.append(f"Fail - {os.path.basename(__file__)} - 20 Diffs")


# Step 5:
print(f"---- Step 5 :{time.time() - start}")
tries += 1
if not rerun_assert_diff_count(table_name, diff_file, 20):
    fails += 1
    fail_info.append(f"Fail - {os.path.basename(__file__)} - Non-Matching Rerun (20)")
# time.sleep(25.0 + start - time.time())


# Step 6:
print(f"---- Step 6 :{time.time() - start}")
tries += 1
while not rerun_assert_diff_count(table_name, diff_file, 10):
    print(f"---- NOTE: still 20 diffs at {time.time() - start}")
    if time.time() - start > 50.0:
        fails += 1
        fail_info.append(f"Fail - {os.path.basename(__file__)} - Non-Matching Rerun (10)")
        break
if not fail_info: print(f"---- NOTE: down to 10 diffs")
# time.sleep(35.0 + start - time.time())


# Step 7:
print(f"---- Step 7 :{time.time() - start}")
tries += 1
while not rerun_assert_match(table_name, diff_file):
    print(f"---- NOTE: still 10 diffs at {time.time() - start}")
    if time.time() - start > 70.0:
        fails += 1
        fail_info.append(f"Fail - {os.path.basename(__file__)} - Matching Rerun")
        break

if not fail_info: print(f"---- NOTE: tables match at {time.time() - start}")


# Cleanup
os.environ.pop("SPOCK_DELAY")
spock_99_cleanup.run()
remove_table(table_name)


if fail_info:
    print(f"Failed {fails} out of {tries} cases")
    for fail in fail_info:
        print(f"\t{fail}")
    util_test.exit_message(f"Fail - {os.path.basename(__file__)}")


util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
