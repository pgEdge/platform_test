import sys, os, util_test, subprocess, getpass

# Print Script
print(f"Starting - {os.path.basename(__file__)}")

# Get Test Settings
util_test.set_env()
repo=os.getenv("EDGE_REPO")
num_nodes=int(os.getenv("EDGE_NODES",2))
home_dir=os.getenv("EDGE_HOME_DIR")
cluster_dir=os.getenv("EDGE_CLUSTER_DIR")
cluster_name=os.getenv("EDGE_CLUSTER")
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","lcusr")
pw=os.getenv("EDGE_PASSWORD","password")
db=os.getenv("EDGE_DB","demo")
host=os.getenv("EDGE_HOST","localhost")
repuser=os.getenv("EDGE_REPUSER","repuser")
repset=os.getenv("EDGE_REPSET","demo-repset")
spockpath=os.getenv("EDGE_SPOCK_PATH")
dbname=os.getenv("EDGE_DB","lcdb")


print("Our configuration settings are:")
print(repo)
print(num_nodes)
print(home_dir)
print(cluster_dir)
print(cluster_name)
print(port)
print(usr)
print(pw)
print(db)
print(host)
print(repset)
print(spockpath)
print(dbname)


print("The first print statement returns the OS user, the second the repuser from our environment variables:")
os_whoami=(os.popen('whoami').read())
print(f"The OS user is: {os_whoami}")
print(f"The repuser is: {repuser}");


#
# Check the information returned by pgedge info at the nc dir.
# 
command = "info"
res1=util_test.run_nc_cmd("Querying db guc-show for information about shared_preload_libraries.", command, f"{home_dir}")
print(res1)
print("*"*100)

#
# Check the information from cluster list-nodes.
#
command = (f"cluster list-nodes {cluster_name}")
res=util_test.run_nc_cmd("Exercise the list-nodes command", command, f"{home_dir}")
print(f"Command: {command}")
print(f"The list-nodes command returns = {res}\n")
print("*"*100)

#
# Check the information returned by pgedge info at the nc dir.
# 
list=(f"um list")
list_res=util_test.run_nc_cmd("Getting list of available packages", list, f"{home_dir}")
print(list_res.stdout)
print("*"*100)


#
# Check the information returned by pgedge status.
# 
command = "status"
res2=util_test.run_nc_cmd("Querying db guc-show for information about shared_preload_libraries.", command, f"{home_dir}")
print(res2)
print("*"*100)


#
# Confirm the values in the shared_preload_libraries parameter.
# 
command = "db guc-show shared_preload_libraries"
res3=util_test.run_nc_cmd("Querying db guc-show for information about shared_preload_libraries.", command, f"{home_dir}")
print(res3)
print("*"*100)

#
# Check the information returned by pgedge info from nc/pgedge/cluster/demo/n1/pgedge.
# 
list=(f"um list")
list_res2=util_test.run_nc_cmd("Getting list of available packages", list, f"{cluster_dir}/n1")
print(list_res2.stdout)
print("*"*100)


#
# Check the information returned by pgedge status from nc/pgedge/cluster/demo/n1/pgedge.
# 
command = "status"
res5=util_test.run_cmd("Querying db guc-show for information about shared_preload_libraries.", command, f"{cluster_dir}/n1")
print(res5)
print("*"*100)


#
# Confirm the values in the shared_preload_libraries parameter from nc/pgedge/cluster/demo/n1/pgpedge.
#
command = "db guc-show shared_preload_libraries"
res6=util_test.run_cmd("Querying db guc-show for information about shared_preload_libraries.", command, f"{cluster_dir}/n1")
print(res6)
print("*"*100)


#
# Check the information returned by pgedge info from nc/pgedge/cluster/demo/n2/pgedge.
#
list=(f"um list")
list_res3=util_test.run_nc_cmd("Getting list of available packages", list, f"{cluster_dir}/n2")
print(list_res3.stdout)
print("*"*100)


#
# Check the information returned by pgedge status from nc/pgedge/cluster/demo/n2/pgedge.
#
command = "status"
res8=util_test.run_cmd("Querying db guc-show for information about shared_preload_libraries.", command, f"{cluster_dir}/n2")
print(res8)
print("*"*100)


#
# Confirm the values in the shared_preload_libraries parameter from nc/pgedge/cluster/demo/n2/pgpedge.
#
command = "db guc-show shared_preload_libraries"
res9=util_test.run_cmd("Querying db guc-show for information about shared_preload_libraries.", command, f"{cluster_dir}/n2")
print(res9)
print("*"*100)

