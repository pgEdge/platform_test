import sys, os, util_test, subprocess
from util_datagen import generate_table, remove_table, mod_and_repair, insert_into

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")

port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","lcusr")
pw=os.getenv("EDGE_PASSWORD","password")
host=os.getenv("EDGE_HOST","localhost")
dbname=os.getenv("EDGE_DB","lcdb")
num_nodes=int(os.getenv("EDGE_NODES",2))

form = [
    ("name", "VARCHAR(255)"),
    ("big_int", "BIGINT"),
    ("float_value", "REAL"),
    ("date", "TIMESTAMP"),
]

# Second functionality test file: Conatains test for diffs found
#   block at the start
#   block in the middle
#   block at the end
#   evenly distributed (sparse)
#   evenly distributed (dense)
#   extra rows at end
#   extra rows in middle (tested with uuid)
#   mismatched block-rows

# Generates Tables
generate_table("t1", form, 25000)
generate_table("t2", form, 10000, pkey="uuid")

total_counter = 0
fails = list()

# Assert that all tables match
cmd_node = f"ace table-diff {cluster} public.t1"
res=util_test.run_cmd("Matching Tables", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH OK" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Matching Tables (t1)", 1)
print("*" * 100)

cmd_node = f"ace table-diff {cluster} public.t2"
res=util_test.run_cmd("Matching Tables", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH OK" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Matching Tables (t2)", 1)
print("*" * 100)

# Start Checks
column = ("float_value", "REAL")

# Start
total_counter += 1
code, msg = mod_and_repair(column, "t1", cluster, home_dir, where="id < 2000")
if code == 1:
    fails.append(f"Fail - {os.path.basename(__file__)} - {msg}: block at start")

# Middle
total_counter += 1
code, msg = mod_and_repair(column, "t1", cluster, home_dir, where="10000 < id and id < 12000")
if code == 1:
    fails.append(f"Fail - {os.path.basename(__file__)} - {msg}: block in middle")

# End
total_counter += 1
code, msg = mod_and_repair(column, "t1", cluster, home_dir, where="23000 < id")
if code == 1:
    fails.append(f"Fail - {os.path.basename(__file__)} - {msg}: block at end")

# Even (sparse)
total_counter += 1
code, msg = mod_and_repair(column, "t1", cluster, home_dir, where="mod(id, 27) = 0")
if code == 1:
    fails.append(f"Fail - {os.path.basename(__file__)} - {msg}: even sparse")

# Even (dense)
total_counter += 1
code, msg = mod_and_repair(column, "t1", cluster, home_dir)
if code == 1:
    fails.append(f"Fail - {os.path.basename(__file__)} - {msg}: even dense")

# Lines Inserted to the End
total_counter += 1
insert_into("t1", form, 2000, nodes=[1])
code, msg = mod_and_repair(column, "t1", cluster, home_dir, where="false")
if code == 1:
    fails.append(f"Fail - {os.path.basename(__file__)} - {msg}: lines inserted at end")

# Lines Inserted into Middle
total_counter += 1
insert_into("t2", form, 2000, nodes=[1], pkey="uuid")
insert_into("t2", form, 13000, pkey="uuid")
code, msg = mod_and_repair(column, "t2", cluster, home_dir, where="false")
if code == 1:
    fails.append(f"Fail - {os.path.basename(__file__)} - {msg}: lines inserted at middle")

# Note that this was tested with uuid primary key, using this test method with serials creates a problem where huge parts of
# the table are offset from eachother. The intent here was to simlulate the case where some lines are not replaicated but
# replication continues after. In this case with either serials or snowflake sequences the specific key is copied over so
# the offset issue doesn't happen. As a result uuids more accuratly simulate the times and work that would happen in this case.

# Mismatched Block Rows
total_counter += 1
code, msg = mod_and_repair(column, "t1", cluster, home_dir, action="delete", where="mod(id, 10) = 0")
if code == 1:
    fails.append(f"Fail - {os.path.basename(__file__)} - {msg}: mismatched block rows")

# Removes Table
remove_table("t1")
remove_table("t2")

if fails:
    print(f"Failed {len(fails)} of {total_counter} tests:")
    for fail in fails:
        print(f"  {fail}")
    util_test.exit_message("")
else:
    print(f"Passed all {total_counter} mod_and_repairs!")

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
