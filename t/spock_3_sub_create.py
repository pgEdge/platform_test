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
    port=int(os.getenv("EDGE_START_PORT",6432))
    repuser=os.getenv("EDGE_REPUSER","pgedge")
    pw=os.getenv("EDGE_PASSWORD","lcpasswd")
    db=os.getenv("EDGE_DB","lcdb")
    host=os.getenv("EDGE_HOST","localhost")
    spock_delay=os.getenv("SPOCK_DELAY", None)

    port_array = []
    for n in range(1,num_nodes+1):
        port_array.append(port)
        port = port + 1

    for n in range(1,num_nodes+1):
        for z in range(1,num_nodes+1):
            if n!=z:
                ## Create Subs
                cmd_node = f"spock sub-create sub_n{n}n{z} 'host=127.0.0.1 port={port_array[z-1]} user={repuser} dbname={db}' {db}"

                if spock_delay is not None:
                    try:
                        spock_delay = int(spock_delay)
                        cmd_node += f" -a={spock_delay}"

                    except Exception as e:
                        print(f"Error in getting spock_delay: {e}")

                res=util_test.run_cmd("Sub Create", cmd_node, f"{cluster_dir}/n{n}")
                print(res)
                if res.returncode == 1 or "sub_create" not in res.stdout:
                    util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Sub Create", 1) 

    ## Sub Show Status Test
    cmd_node = f"spock sub-show-status sub_n1n2 {db}"
    res=util_test.run_cmd("Sub Show Status", cmd_node, f"{cluster_dir}/n1")
    print(res)
    if res.returncode == 1 or "replicating" not in res.stdout:
        util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Sub Show Status", 1) 

    ## Node List Test
    cmd_node = f"spock node-list {db}"
    res=util_test.run_cmd("Node List", cmd_node, f"{cluster_dir}/n1")
    print(res)
    if res.returncode == 1 or "n2" not in res.stdout:
        util_test.exit_message(f"Fail - {os.path.basename(__file__)} - Node List", 1) 

if __name__ == "__main__":
    ## Print Script
    print(f"Starting - {os.path.basename(__file__)}")
    run()
    util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0) 
