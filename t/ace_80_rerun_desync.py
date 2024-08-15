import sys, os, util_test, subprocess
import time

from util_datagen import generate_table, remove_table, insert_into

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
cmd_node = f"ace table-diff {cluster} public.{table_name}"
res=util_test.run_cmd("table-diff", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH OK" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Matching Tables", 1)
print()


# Step 1: (I will just be importing the spock scrips which might cause strange behavior)
os.environ["SPOCK_DELAY"] = "15"

import spock_1_setup
import spock_2_node_create
import spock_3_sub_create
import spock_4_repset_add_table


# Step 2:
insert_into("t1", form, 10, nodes=[1])
time.sleep(5.0)


# Step 3:
insert_into("t1", form, 10, nodes=[1])
time.sleep(5.0)


# Step 4:
cmd_node = f"ace table-diff {cluster} public.{table_name}"
res=util_test.run_cmd("table-diff", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "FOUND 20 DIFFERNCES" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - 20 Diffs", 1)
diff_file_local, diff_data = util_test.get_diff_data(res.stdout)
print()


# Step 5:
cmd_node = f"ace table-rerun {cluster} {diff_file_local} public.{table_name}"
res=util_test.run_cmd("table-rerun", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "FOUND 20 DIFFERNCES" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Non-Matching Rerun", 1)
print()
time.sleep(6.0)


# Step 6:
cmd_node = f"ace table-rerun {cluster} {diff_file_local} public.{table_name}"
res=util_test.run_cmd("table-rerun", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "FOUND 10 DIFFERNCES" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Non-Matching Rerun", 1)
print()
time.sleep(5.0)


# Step 7:
cmd_node = f"ace table-rerun {cluster} {diff_file_local} public.{table_name}"
res=util_test.run_cmd("table-rerun", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH OK" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Non-Matching Rerun", 1)
print()


# Cleanup
remove_table("t1")
os.environ.pop("SPOCK_DELAY")
import spock_99_cleanup


util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
