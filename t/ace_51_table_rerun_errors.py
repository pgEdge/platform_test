import sys, os, util_test, subprocess
import json

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")
pg_dir = os.getenv("EDGE_HOME_DIR")

## Error Handling Tests for `ace table-rerun`

# First Call Table Diff to get a Diff File
cmd_node = f"ace table-diff {cluster} public.foo_diff_data"
res=util_test.run_cmd("table-diff", cmd_node, f"{home_dir}")
diff_file_local, diff_data = util_test.get_diff_data(res.stdout)

# Non-Existent Cluster Name
cmd_node = f"ace table-rerun notreal {diff_file_local} public.foo_diff_data"
res=util_test.run_cmd("table-rerun", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 0 or "cluster not found" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Wrong Cluster Name", 1) 
print("*" * 100)

# Non-Existent Diff File
cmd_node = f"ace table-rerun {cluster} notreal.json public.foo_diff_data"
res=util_test.run_cmd("table-rerun", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 0 or "Diff file notreal.json not found" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Wrong File Name", 1) 
print("*" * 100)

# Non-Existent Table Name
cmd_node = f"ace table-rerun {cluster} {diff_file_local} public.foo_not_real"
res=util_test.run_cmd("table-rerun", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 0 or "Invalid table name 'public.foo_not_real'" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Wrong Table Name", 1) 
print("*" * 100)

# Non-Existent Database Name
cmd_node = f"ace table-rerun {cluster} {diff_file_local} public.foo_diff_data --dbname=not_real"
res=util_test.run_cmd("table-rerun", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 0 or "Database 'not_real' not found in cluster 'demo'" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Wrong Database Name", 1) 
print("*" * 100)

# Un-authorized Database Name
cmd_node = f"ace table-rerun {cluster} {diff_file_local} public.foo_diff_data --dbname=carolsdb"
res=util_test.run_cmd("table-rerun", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 0 or "Invalid table name 'public.foo_diff_data'" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Unauthorzied Database Name", 1) 
print("*" * 100)

# Diff File Not JSON
diff_path = os.path.join(pg_dir, "diffs")
if not os.path.exists(diff_path):
    os.mkdir(diff_path)

txt_local = os.path.join("diffs", "text.txt")
txt_path = os.path.join(diff_path, "text.txt")
if not os.path.exists(txt_path):
    with open(txt_path, "w") as file:
        file.write("This is the story of a girl\n")
        file.write("Who cried a river and drowned the whole world\n")
        file.write("And while she looks so sad in photographs\n")
        file.write("I absolutely love her\n")

cmd_node = f"ace table-rerun {cluster} {txt_local} public.foo_diff_data"
res=util_test.run_cmd("table-rerun", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 0 or "Could not load diff file as JSON" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Wrong Cluster Name", 1) 
print("*" * 100)

# Diff File Not Proper
json_local = os.path.join("diffs", "text.json")
json_path = os.path.join(diff_path, "text.json")
if not os.path.exists(json_path):
    with open(json_path, "w") as file:
        file.write(json.dumps({
            "Monica": "in my life",
            "Erica": "by my side",
            "Rita": "all I need",
            "Tina": "what I see",
            "Sandra": "in the sun",
            "Mary": "all night long",
            "Jessica": "here I am"
        }))

cmd_node = f"ace table-rerun {cluster} {json_local} public.foo_diff_data"
res=util_test.run_cmd("table-rerun", cmd_node, f"{home_dir}")
util_test.printres(res)
if res.returncode == 0 or "Contents of diff file improperly formatted" not in res.stdout:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Wrong Cluster Name", 1) 
print("*" * 100)

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
