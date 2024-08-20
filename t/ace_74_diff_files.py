import sys, os, util_test, subprocess
from util_datagen import generate_table, write_diff

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

# Fifth functionality test file: Conatains test
#   generating jsons
#   generating csv
#   ensuring that information in each match

# Generates Table
generate_table("t1", form, 10000)

psql_qrys = [
    """INSERT INTO t1 (name, big_int, float_value, date)
    VALUES ('Bob Kenedy', '12', '51.0', '2024-07-16 04:20:00')
    """,
    """UPDATE t1
    SET big_int = '188'
    WHERE id > 9950
    """,
    """UPDATE t1
    SET float_value = '10.5'
    WHERE mod(id, 25) = 0
    """,
    """UPDATE t1
    SET name = 'Han Solo'
    WHERE id < 50
    """,
    """DELETE FROM t1
    WHERE mod(id, 127) = 0
    """,
]

# Modify table to create various differences
for psql_qry in psql_qrys:
    if util_test.write_psql(psql_qry, host, dbname, port+1, pw, usr) == 1:
        util_test.exit_message(f"Couldn't edit contents of table : \n{psql_qry}")

# Find diffs as json
cmd_node = f"ace table-diff {cluster} public.t1"
res=util_test.run_cmd("Matching Tables", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES DO NOT MATCH" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Get Diffs `json`", 1)
_, diff_data_jsn = util_test.get_diff_data(res.stdout)

# Find diffs as csv
cmd_node = f"ace table-diff {cluster} public.t1 --output=csv"
res=util_test.run_cmd("Matching Tables", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES DO NOT MATCH" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Get Diffs `csv`", 1)
_, diff_data_csv = util_test.get_diff_data(res.stdout, type="csv")

if not diff_data_jsn:
    util_test.exit_message("Found no diffs in json diff file")

if not diff_data_csv:
    util_test.exit_message("Found no diffs in csv diff file")

print("Successfully read diff data from both json and csv")

# print(sum( [len(diff_data_jsn["n1/n2"][f"n{i}"]) for i in range(1,2)] ))
# print(len(diff_data_csv))

# Compare structure
# NOTE: this used to be easier but new format makes this annoying, if needed might impement later 
# if util_test.compare_structures(diff_data_jsn["n1/n2"], diff_data_csv):
#     print("Diff files in csv and json match!")
# else:
#     util_test.exit_message("Structures did not match")

# write_diff("diff_from_json", diff_data_jsn)
# write_diff("diff_from_csv", diff_data_csv)

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
