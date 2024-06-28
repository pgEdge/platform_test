import sys, os, util_test, subprocess

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")

## Error Handling Tests for `ace table-diff`

# Non-Existent Cluster Name
cmd_node = f"ace table-diff dem public.foo"
res=util_test.run_cmd("non-existent cluster name", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 0 or "cluster not found" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - cluster not found", 1) 
print("*" * 100)

# Non-Existent Table Name
cmd_node = f"ace table-diff {cluster} public.fo"
res=util_test.run_cmd("misspelled table name", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 0 or "Invalid table name 'public.fo'" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Invalid Table", 1) 
print("*" * 100)

# Non-Existent Schema Name
cmd_node = f"ace table-diff {cluster} pablic.foo"
res=util_test.run_cmd("misspelled table name", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 0 or "Invalid table name 'pablic.foo'" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Invalid Table", 1) 
print("*" * 100)

# Non Existent Database Name
cmd_node = f"ace table-diff {cluster} public.foo --dbname=not_real"
res=util_test.run_cmd("non-existent database name", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 0 or f"Database 'not_real' not found in cluster '{cluster}'" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Database Name", 1)
print("*" * 100)

# Block Rows < 1000
cmd_node = f"ace table-diff {cluster} public.foo --block_rows=999"
res=util_test.run_cmd("block_rows < 1000", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 0 or "Block row size should be >= 1000" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Block Rows", 1) 
print("*" * 100)
    
# Max CPU ratio > 1
cmd_node = f"ace table-diff {cluster} public.foo --max_cpu_ratio=2"
res=util_test.run_cmd("cpu ratio > 1", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 0 or "Invalid value range for ACE_MAX_CPU_RATIO or --max_cpu_ratio" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Block Rows", 1)
print("*" * 100)

# Max CPU is String
cmd_node = f"ace table-diff {cluster} public.foo --max_cpu_ratio=ONE"
res=util_test.run_cmd("invalid_cpu_ratio", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 0 or "Invalid values for ACE_MAX_CPU_RATIO" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Max CPU Ratio", 1) 
print("*" * 100)
    
# Unsupported Output Format
cmd_node = f"ace table-diff {cluster} public.foo --output=html"
res=util_test.run_cmd("output in html format", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 0 or "table-diff currently supports only csv and json output formats" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Output HTML", 1)

# Max CPU float > 1
cmd_node = f"ace table-diff {cluster} public.foo --max_cpu_ratio=1.5"
res=util_test.run_cmd("max-cpu float > 1", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 0 or "Invalid value range for ACE_MAX_CPU_RATIO or --max_cpu_ratio" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Max CPU Ratio > 1", 1)
print("*" * 100)

# Same Nodename (note that this case errors because the removal of repeated nodes leaves one node being compared)
cmd_node = f"ace table-diff {cluster} public.foo --nodes=n1,n1"
res=util_test.run_cmd("table-diff", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 0 or "Ignoring duplicate node names" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Same Nodename", 1)
print("*" * 100)

# Unauthorized Database Name

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
