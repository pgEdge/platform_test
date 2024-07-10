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

# Generates Small and Large Table
basic_form = [
    ("name", "VARCHAR(255)"),
    ("info", "TEXT"),
    ("small_int", "INTEGER"),
    ("big_int", "BIGINT"),
    ("float_value", "REAL"),
    ("numbers", "FLOAT[]"),
    ("obj", "JSONB"),
    ("date", "TIMESTAMP"),
]

generate_table("t1", basic_form,   100)
generate_table("t2", basic_form, 10000)
generate_table("t3", basic_form,   100, comp_pkey=True)
generate_table("t4", basic_form, 10000, comp_pkey=True)

# Assert that all tables match
cmd_node = f"ace table-diff {cluster} public.t1"
res=util_test.run_cmd("Matching Tables", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH OK" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Matching Tables", 1)
print("*" * 100)

cmd_node = f"ace table-diff {cluster} public.t2"
res=util_test.run_cmd("Matching Tables", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH OK" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Matching Tables", 1)
print("*" * 100)

# Assert that all tables match (comp-pkey)
cmd_node = f"ace table-diff {cluster} public.t3"
res=util_test.run_cmd("Matching Tables", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH OK" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Matching Tables Comp", 1)
print("*" * 100)

cmd_node = f"ace table-diff {cluster} public.t4"
res=util_test.run_cmd("Matching Tables", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH OK" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Matching Tables Comp", 1)
print("*" * 100)

for table_name in ["t2", "t4"]:
    for column in basic_form:
        code, msg = mod_and_repair(column, table_name, cluster, home_dir, where="small_int < -80")
        if code == 1:
            util_test.exit_message(f"Fail - {os.path.basename(__file__)} - {msg} on {column} in {table_name}")

# Removes Tables
remove_table("t1")
remove_table("t2")
remove_table("t3")
remove_table("t4")

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
