import sys, os, util_test, subprocess
from util_datagen import generate_table, remove_table, mod_and_repair, insert_into

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")

# WARNING: Full test takes super long
# run with 3 nodes and numbers+obj commented out took around 26 mins

# Fourth functionality test file: Conatains large loop for all combinations of
#   all possible dataypes
#   small / large table
#   serial / uuid / comp pkey
#   quoted / not quoted columns
#   edits in block / deletes throughout

sizes = [
      100,
    10000,
]

pkeys = [
    "serial",
    "uuid",
    "comp",
]

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

total_counter = 0
fails = list()

for size in sizes:
    for pkey in pkeys:

        if pkey == "serial":
            wheres = ["mod(id, 5) = 0", "id < " + str(size/10)]
        if pkey == "uuid":
            wheres = ["id < \'5\'"]
        if pkey == "comp":
            wheres = ["mod(id, 5) = 0", "id < " + str(size/10)]

        for quoted_cols in [False, True]:

            form = list()
            if quoted_cols:
                form = [(f"\"{col_name}\"", col_type) for col_name, col_type in basic_form]
            else:
                form = basic_form

            generate_table("t1", form, size, pkey)
            for column in form:

                for where in wheres:
                    total_counter += 2
                    code, msg = mod_and_repair(column, "t1", cluster, home_dir, where=where)
                    if code == 1:
                        fails.append(f"Fail - {os.path.basename(__file__)} - {msg}\n{size} : {pkey} : quotedcols={quoted_cols} : {column} : {where}")

                    code, msg = mod_and_repair(column, "t1", cluster, home_dir, action="delete", where=where)
                    if code == 1:
                        fails.append(f"Fail - {os.path.basename(__file__)} - {msg}\n{size} : {pkey} : quotedcols={quoted_cols} : {column} : {where}")

            remove_table("t1")

if fails:
    print(f"Failed {len(fails)} of {total_counter} tests:")
    for fail in fails:
        print(f"  {fail}")
    util_test.exit_message("")
else:
    print(f"Passed all {total_counter} mod_and_repairs!")

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
