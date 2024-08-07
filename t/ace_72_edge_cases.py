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

# Third functionality test file: Conatains test for
#   no pkey
#   non-matching but similar schema (INT / BIGINT)
#   non-matching but similar schema (INT / REAL)

form1 = [
    ("name", "VARCHAR(255)"),
    ("info", "TEXT"),
    ("big_int", "INTEGER"),
    ("float_value", "REAL"),
]

form2 = [
    ("name", "VARCHAR(255)"),
    ("info", "TEXT"),
    ("big_int", "BIGINT"),
    ("float_value", "REAL"),
]

form3 = [
    ("name", "VARCHAR(255)"),
    ("info", "TEXT"),
    ("big_int", "REAL"),
    ("float_value", "REAL"),
]

# Generates Tables
generate_table("t1", form1, 10000, pkey="none") # no pkey

generate_table("t2", form1,     0, pkey="uuid") # non-matching (int / bigint)
generate_table("t2", form2,     0, pkey="uuid", nodes=[2])
insert_into(   "t2", form1, 10000, pkey="uuid")

generate_table("t3", form1,     0, pkey="uuid") # non-matching (int / real)
generate_table("t3", form3,     0, pkey="uuid", nodes=[2])
insert_into(   "t3", form1, 10000, pkey="uuid")

# Ensures that tables have schema diffs
for table_name in ["t2", "t3"]:
    psql_stat = f"""
    SELECT
        column_name,
        data_type
    FROM
        information_schema.columns
    WHERE
        table_name = '{table_name}';
    """

    print(f"---------- {table_name} SCHEMA ----------")
    print("--- N1 ---")
    ret = util_test.read_psql(psql_stat, host, dbname, port, pw, usr)
    print(ret)
    print("--- N2 ---")
    ret = util_test.read_psql(psql_stat, host, dbname, port+1, pw, usr)
    print(ret)
    print()

# Assert that all tables match
# cmd_node = f"ace table-diff {cluster} public.t1"
# res=util_test.run_cmd("Matching Tables", cmd_node, f"{home_dir}")
# util_test.printres(res)
# if res.returncode == 1 or "TABLES MATCH OK" not in res.stdout:
#     util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Matching Tables (t1)", 1)
# print("*" * 100)

cmd_node = f"ace table-diff {cluster} public.t2"
res=util_test.run_cmd("Matching Tables", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH OK" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Matching Tables (t2)", 1)
print("*" * 100)

cmd_node = f"ace table-diff {cluster} public.t3"
res=util_test.run_cmd("Matching Tables", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH OK" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Matching Tables (t3)", 1)
print("*" * 100)

# Some mod and repairs to test functionality
column1 = ("big_int", "INTEGER")
column2 = ("float_value", "REAL")

code, msg = mod_and_repair(column1, "t2", cluster, home_dir, where="float_value < 0")
if code == 1:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - {msg}: t2 mod big int")

code, msg = mod_and_repair(column1, "t3", cluster, home_dir, where="float_value < 0")
if code == 1:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - {msg}: t3 mod big int")

code, msg = mod_and_repair(column2, "t2", cluster, home_dir, where="big_int < 0")
if code == 1:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - {msg}: t2 mod float")

code, msg = mod_and_repair(column2, "t3", cluster, home_dir, where="big_int < 0")
if code == 1:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - {msg}: t3 mod float")

# Removes Table
remove_table("t1")
remove_table("t2")
remove_table("t3")

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
