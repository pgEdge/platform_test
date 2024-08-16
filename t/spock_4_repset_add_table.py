# This test case (and the other spock_# tests) expect to be run against a two node cluster.
# If it fails with an error: pg_reload_conf \n----------------\n t\n(1 row)\n\nSet GUC snowflake.node to 1\n[\n  {\n  ...
# you are probably running against a 3 node cluster.
# Per conversation with Cady, we may want to use a new setup script written in .py that uses the same
# logic as 8000a/8000b, but that uses the environment variable values. 

import os, util_test, subprocess

## Get Test Settings
util_test.set_env()

def run():
    # Get environment variables
    num_nodes = int(os.getenv("EDGE_NODES", 2))
    cluster_dir = os.getenv("EDGE_CLUSTER_DIR")
    db=os.getenv("EDGE_DB","lcdb")

    for n in range(1,num_nodes+1):
        ## Add Tables to Repset
        cmd_node = f"spock repset-add-table default '*' {db}"
        res=util_test.run_cmd("Repset Add Table", cmd_node, f"{cluster_dir}/n{n}")
        print(res)
        if res.returncode == 1 or "Adding table" not in res.stdout:
            util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Repset Add Table", 1) 

    ## Repset List Tables Test
    cmd_node = f"spock repset-list-tables public {db}"
    res=util_test.run_cmd("Repset List Tables", cmd_node, f"{cluster_dir}/n1")
    print(res)
    if res.returncode == 1 or "pgbench_accounts" not in res.stdout or "default" not in res.stdout:
        util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Repset List Tables", 1) 

    ## Sub Show Table Test
    cmd_node = f"spock sub-show-table sub_n1n2 pgbench_accounts {db}"
    res=util_test.run_cmd("Sub Show Table", cmd_node, f"{cluster_dir}/n1")
    print(res)
    if res.returncode == 1 or "pgbench_accounts" not in res.stdout:
        util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Sub Show Table", 1)

if __name__ == "__main__":
    ## Print Script
    print(f"Starting - {os.path.basename(__file__)}")
    run()
    util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0) 
