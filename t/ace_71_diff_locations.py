import sys, os, util_test, subprocess
from util_datagen import generate_table, remove_table, mod_and_repair

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
#   extra rows in middle
#   extra rows at end

# Generates Table
generate_table("t1", form, 25000)

# Assert that all tables match
cmd_node = f"ace table-diff {cluster} public.t1"
res=util_test.run_cmd("Matching Tables", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH OK" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Matching Tables", 1)
print("*" * 100)

# Start Checks
column = ("float_value", "REAL")

# Start
code, msg = mod_and_repair(column, "t1", cluster, home_dir, where="id < 2000")
if code == 1:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - {msg}: block at start")

# Middle
code, msg = mod_and_repair(column, "t1", cluster, home_dir, where="10000 < id and id < 12000")
if code == 1:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - {msg}: block in middle")

# End
code, msg = mod_and_repair(column, "t1", cluster, home_dir, where="23000 < id")
if code == 1:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - {msg}: block at end")

# Even (sparse)
code, msg = mod_and_repair(column, "t1", cluster, home_dir, where="mod(id, 27) = 0")
if code == 1:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - {msg}: even sparse")

# Even (dense)
code, msg = mod_and_repair(column, "t1", cluster, home_dir)
if code == 1:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - {msg}: even dense")

# Removes Table
remove_table("t1")

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
