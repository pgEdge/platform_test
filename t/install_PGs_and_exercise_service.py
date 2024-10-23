## This script finds all of the available versions of PG and installs each version with the setup command. 

import sys, os, util_test, subprocess, json

# Print Script
print(f"Starting - {os.path.basename(__file__)}")

# Get Test Settings
util_test.set_env()
repo=os.getenv("EDGE_REPO")
pgv=os.getenv("EDGE_INST_VERSION")
num_nodes=int(os.getenv("EDGE_NODES",2))
home_dir=os.getenv("EDGE_HOME_DIR")
cluster_dir=os.getenv("EDGE_CLUSTER_DIR")
cluster_name=os.getenv("EDGE_CLUSTER","demo")
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","lcusr")
pw=os.getenv("EDGE_PASSWORD","password")
host=os.getenv("EDGE_HOST","localhost")
repuser=os.getenv("EDGE_REPUSER","susan")
repset=os.getenv("EDGE_REPSET","demo-repset")
spockpath=os.getenv("EDGE_SPOCK_PATH")
dbname=os.getenv("EDGE_DB","lcdb")

## Create the variables we'll be using in this script:
components = []
versions = ""
## Service options tested by this script are:
services = ["status","stop","start","restart","reload","enable","disable","config"]
#print("*"*100)

## We'll call find_pg_versions to return a list of Postgres {versions} available through UM.
versions,components=util_test.find_pg_versions(home_dir)

## Then loop through the versions and install each version with the setup command:
for version in versions:
    ## Find a free port for the PG installation; call get_avail_port and pass in the port number:
    free_port=util_test.get_avail_ports(port)
    install_pg=(f"setup -U {usr} -d {dbname} -P {pw} --port={free_port} --pg_ver={version}")
    print(f"The setup command executing now is: {install_pg}")
    installed_res=util_test.run_nc_cmd("Installing Postgres versions available", install_pg, f"{home_dir}")
    print(installed_res)

    ## Increase the port value by 1 before installing the next version of Postgres:
    port = port + 1 

    ## Check to see if the installation was successful
    if installed_res.returncode == 0:
        print(f"Command succeeded for Postgres {version}:{installed_res.stdout}")

for component in components:
    for svc in services:
        ## Exercise the installed Postgres services
        print(f"component: {component}")
        print(f"svc: {svc}")
        command = (f"service {svc} --component={component}")
        exercise_svc=util_test.run_nc_cmd("Exercising the service", command, f"{home_dir}")
        print(f"The command to exercise the service contains: {exercise_svc}")


