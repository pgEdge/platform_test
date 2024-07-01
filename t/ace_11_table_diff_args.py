import sys, os, util_test, subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")
db_name = os.getenv("EDGE_DB")

## Additional Arguments Functionality Tests for `ace table-diff`

# Blocks Rows Given
cmd_node = f"ace table-diff {cluster} public.foo --block_rows=1001"
res=util_test.run_cmd("block_rows > 1000", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Block Rows", 1)
print("*" * 100)

# Max CPU Ratio Given
cmd_node = f"ace table-diff {cluster} public.foo --max_cpu_ratio=1"
res=util_test.run_cmd("max_cpu_ratio is 1", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Max CPU Ratio", 1)
print("*" * 100)

# Max CPU float < 1
cmd_node = f"ace table-diff {cluster} public.foo --max_cpu_ratio=0.5"
res=util_test.run_cmd("max-cpu float < 1", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH OK" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Max CPU Ratio < 1", 1) 
print("*" * 100)

# Output Format Given
cmd_node = f"ace table-diff {cluster} public.foo --output=json"
res=util_test.run_cmd("output in json form", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Output JSON", 1)
print("*" * 100)

# Database Given (1)
cmd_node = f"ace table-diff {cluster} public.foo --dbname={db_name}"
res=util_test.run_cmd("Main databse explicitly given", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "TABLES MATCH" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Database Given", 1)
print("*" * 100)

# Database Given (2)
cmd_node = f"ace table-diff {cluster} public.foo --dbname=alicesdb"
res=util_test.run_cmd("Main databse explicitly given", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 1 or "ALL TABLES ARE EMPTY" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Database Given New User", 1)
print("*" * 100)

## TO DO - ydiff error
#cmd_node = f"ace table-diff {cluster} public.foo --output=csv"
#res=util_test.run_cmd("output in csv form", cmd_node, f"{home_dir}")
#util_test.printres(res)
#if res.returncode == 1 or "TABLES DO NOT MATCH" not in res.stdout:
#    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Output CSV", 1)

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
