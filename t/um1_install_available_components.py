import sys, os, util_test, subprocess, json

# Print Script
print(f"Starting - {os.path.basename(__file__)}")

# Get Test Settings
util_test.set_env()
repo=os.getenv("EDGE_REPO")
cluster_dir=os.getenv("EDGE_CLUSTER_DIR")
home_dir=os.getenv("EDGE_HOME_DIR")
port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","lcusr")
pw=os.getenv("EDGE_PASSWORD","password")
dbname=os.getenv("EDGE_DB","lcdb")
version=os.getenv("EDGE_INST_VERSION","14")


# Get a list of available packages - the list is returned in a json string:
get_list=("um list --json")
res=util_test.run_nc_cmd("Getting list of available packages", get_list, f"{home_dir}")
print(f"{home_dir}{get_list}")


# Break the json string into a list:
res = json.loads(res.stdout)


# Loop through the results and install each available component:
for i, inner_list in enumerate(res): 
    comp=(res[i].get("component"))
    if(comp==f"pg{version}"):
        #print("pg{version}")
        install_comp=(f"um install {comp} -U {usr} -P {pw} -d {dbname}")
        installed_res=util_test.run_nc_cmd("Getting list of available packages", install_comp, f"{home_dir}")
        #print("installed_res is",installed_res)
        print("*" * 100)
        
        init_comp=(f"init {comp} -P {pw}")
        init_res=util_test.run_nc_cmd("init {comp}", init_comp, f"{home_dir}")
        #print("init_res is",init_res)
        print("*" *100)
        
        start_comp=(f"start {comp}")
        start_res=util_test.run_nc_cmd("start pg{version}", start_comp, f"{home_dir}")
        #print("start_res is",start_res)
        print("*" * 100)
    else:
        install_comp=(f"um install {comp} -U {usr} -P {pw} -d {dbname}")
        installed_res=util_test.run_nc_cmd("Getting list of available packages", install_comp, f"{home_dir}")
        print("installed_res is",installed_res)
        print("*" * 100)
        continue
       
    
    
#List the installed components:
list=(f"um list")
list_res=util_test.run_nc_cmd("Getting list of available packages", list, f"{home_dir}")
print(list_res.stdout)

'''

# Needle and Haystack
#Check for a returncode to confirm results:

if installed_res.returncode != 0:
    util_test.EXIT_FAIL
else:
    util_test.EXIT_PASS


# Loop through the results and install each available component:
for i, inner_list in enumerate(res): 
    #print(i,inner_list)
    comp=(res[i].get("component"))
    print(comp)
    if(comp=="pg14"):
        print(comp)
        install_comp=(f"um install {comp} -U {usr} -P {pw} -d {dbname}")
        installed_res=util_test.run_nc_cmd("Getting list of available packages", install_comp, f"{home_dir}")
        # List the installed components:
        list=(f"um list")
        list_res=util_test.run_nc_cmd("Getting list of available packages", list, f"{home_dir}")
        print(list_res.stdout)
    
if installed_res.returncode != 0:
    util_test.EXIT_FAIL
else:
    util_test.EXIT_PASS


   
------------------------------------------------------------------------------------------------------------------------------------
# Get a list of available packages - the list is returned in a json string:
get_list=("um list --json")
res=util_test.run_nc_cmd("Getting list of available packages", get_list, f"{home_dir}")
print(f"{home_dir}{get_list}")
#print(f"{res}")

# Break the json string into a list:
res = json.loads(res.stdout)

# Loop through the results and install each available component:
for i, inner_list in enumerate(res): 
    comp=(res[i].get("component"))
    install_comp=(f"um install {comp} -U {usr} -P {pw} -d {dbname}")
    installed_res=util_test.run_nc_cmd("Getting list of available packages", install_comp, f"{home_dir}")

# List the installed components:
list=(f"um list")
list_res=util_test.run_nc_cmd("Getting list of available packages", list, f"{home_dir}")
print(list_res.stdout)


# Needle and Haystack
#Check for a returncode to confirm results:

if installed_res.returncode != 0:
    util_test.EXIT_FAIL
else:
    util_test.EXIT_PASS

------------------------------------------------------------------------------------------------------------
        config_comp=(f"config {comp} --autostart=on")
        config_res=util_test.run_nc_cmd("config {comp}", config_comp, f"{home_dir}")
        print("config_res is",config_res)
        print("*" * 100)
-------------------------------------------------------------------------------------------------------------------
 else:
        print(comp)
        install_comp=(f"um install {comp} -U {usr} -P {pw} -d {dbname}")
        installed_res=util_test.run_nc_cmd("installing packages", install_comp, f"{home_dir}")
        print("installed_res is",installed_res)
        print("*" * 100)
        ------------------------------------------------------------------------------------------------------------------------
        else:
       print(f"pg{version} not available")
       print("so installing",comp)
       install_comp=(f"um install {comp} -U {usr} -P {pw} -d {dbname}")
       installed_res=util_test.run_nc_cmd("Getting list of available packages", install_comp, f"{home_dir}")
       print("installed_res is",installed_res.stdout)
       print("*" * 100)
       ------------------------------------------------------------------------------------------------------------------------
       install_comp=(f"um install {comp} -U {usr} -P {pw} -d {dbname}")
        installed_res=util_test.run_nc_cmd("Getting list of available packages", install_comp, f"{home_dir}")
        print("installed_res is",installed_res)
        print("*" * 100)
        ------------------------------------------------------------
else:
        install_comp=(f"um install {comp} -U {usr} -P {pw} -d {dbname}")
        installed_res=util_test.run_nc_cmd("Getting list of available packages", install_comp, f"{home_dir}")
        print("installed_res is",installed_res)
        print("*" * 100)
       
'''
    
