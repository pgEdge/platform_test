import sys, os, util_test, subprocess
import json

from ace_util import rerun_assert_fail, diff_assert_mismatch
import ace_util

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")
pg_dir = os.getenv("EDGE_HOME_DIR")

## Error Handling Tests for `ace table-rerun`

# First Call Table Diff to get a Diff File
found_mismatch, diff_file_local = diff_assert_mismatch("foo_diff_data", get_diff=True)
if not found_mismatch:
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Non-Matching Diff")

# Non-Existent Cluster Name
if not rerun_assert_fail("", "", ace_util.DIFF_ERR_NOCLUSTER, call_override=f"ace table-rerun notreal {diff_file_local} public.foo_diff_data"):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Wrong Cluster Name")

# Non-Existent Diff File
if not rerun_assert_fail("foo_diff_data", "notreal.json", ace_util.DIFF_ERR_NODFILE.format( file_name="notreal.json" )):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Wrong File Name")

# Non-Existent Table Name
if not rerun_assert_fail("foo_not_real", diff_file_local, ace_util.DIFF_ERR_NOTABLE.format( table_name="public.foo_not_real" )):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Wrong Table Name")

# Non-Existent Database Name
if not rerun_assert_fail("foo_diff_data", diff_file_local, ace_util.DIFF_ERR_NODB.format( db_name = "not_real", cluster = cluster ), args={"--dbname": "not_real"}):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Wrong Database Name")

# Un-authorized Database Name
if not rerun_assert_fail("foo_diff_data", diff_file_local, ace_util.DIFF_ERR_NOTABLE.format( table_name="public.foo_diff_data" ), args={"--dbname": "carolsdb"}):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Unauthorzied Database Name")

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

if not rerun_assert_fail("foo_diff_data", txt_local, ace_util.DIFF_ERR_NOTJSON):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Wrong Cluster Name")

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

if not rerun_assert_fail("foo_diff_data", json_local, ace_util.DIFF_ERR_DFILEFORM):
    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Wrong Cluster Name")

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
