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

quoted_col_form = [
    ("\"customerIndex\"", "INTEGER"),
    ("value", "REAL"),
]

# First functionality test file: Conatains test for
#   most datatypes
#   large and small tables
#   regular and composite pkeys
#   finding and fixing diffs in above
#   quoted col names

# Generates Small and Large Table
generate_table("t1", basic_form,   100)
generate_table("t2", basic_form, 10000)
generate_table("t3", basic_form,   100, pkey="comp")
generate_table("t4", basic_form, 10000, pkey="comp")

total_counter = 0
fails = list()

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
        total_counter += 1
        code, msg = mod_and_repair(column, table_name, cluster, home_dir, where="small_int < -80")
        if code == 1:
            fails.append(f"Fail - {os.path.basename(__file__)} - {msg} on {column} in {table_name}")

# Removes Tables
remove_table("t1")
remove_table("t2")
remove_table("t3")
remove_table("t4")

# Generates table with quoted column name
generate_table("t1", quoted_col_form, 10000)

# Assert that tables matches
cmd_node = f"ace table-diff {cluster} public.t1"
res=util_test.run_cmd("Matching Tables", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH OK" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Matching Tables", 1)
print("*" * 100)

total_counter += 1
code, msg = mod_and_repair(("\"customerIndex\"", "INTEGER"), "t1", cluster, home_dir, where="mod(id,15) = 0")
if code == 1:
    fails.append(f"Fail - {os.path.basename(__file__)} - {msg} on \'customerIndex\' in t1")

remove_table("t1")

if fails:
    print(f"Failed {len(fails)} of {total_counter} tests:")
    for fail in fails:
        print(f"  {fail}")
    util_test.exit_message("")
else:
    print(f"Passed all {total_counter} mod_and_repairs!")

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
