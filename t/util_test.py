import sys, os, psycopg, json, subprocess, shutil, re
from dotenv import load_dotenv

EXIT_PASS = 0
EXIT_FAIL = 1

## Utility Functions
def set_env():
    load_dotenv('t/lib/config.env')


## abruptly terminate with a codified message
def exit_message(p_msg, p_rc=1):
    if p_rc == 0:
       print(f"INFO {p_msg}")
    else:
       print(f"ERROR {p_msg}")
    sys.exit(p_rc)

# ************************************************************************************************************** 
## Run a pgEdge command
# **************************************************************************************************************
# This function runs a pgedge command; to run a test, define the command in cmd_node, and then choose a variation:
#   * the n(node_number) directory, : res=util_test.run_cmd("add tables to repset", cmd_node, f"{cluster_dir}/n{n}")
#   * the home directory (where home_dir is nc): res=util_test.run_cmd("Testing schema-diff", cmd_node, f"{home_dir}")

def run_cmd(msg, cmd, node_path):
    print(cmd)
    result = subprocess.run(f"{node_path}/pgedge/pgedge {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result

# ************************************************************************************************************** 
## Run a pgEdge command from home
# **************************************************************************************************************
# This function runs a pgedge command; to run a test, define the command in cmd_node, and then choose a variation:
#   * the n(node_number) directory, : res=util_test.run_cmd("add tables to repset", cmd_node, f"{cluster_dir}/n{n}")
#   * the home directory (where home_dir is nc): res=util_test.run_cmd("Testing schema-diff", cmd_node, f"{home_dir}")

def run_nc_cmd(msg, cmd, node_path):
    print(cmd)
    result = subprocess.run(f"{node_path}/pgedge {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result

# **************************************************************************************************************
# This function removes the directory specified in the path variable; specify the complete path and directory name
# Note that this will remove a directory with contents - to remove a single file, use the remove_file command!
# **************************************************************************************************************

def remove_directory(path):
    print(path)
    shutil.rmtree(f"{path}")



# **************************************************************************************************************
# This function removes the file specified in the file variable; file is the complete path to the file and 
# the file name
# **************************************************************************************************************

def remove_file(file):
    print(file)
    try:
        os.remove(f"{file}")
    except OSError:
        pass

# **************************************************************************************************************
# PSQL Functions
# **************************************************************************************************************

## Get psql connection
def get_pg_con(host,dbname,port,pw,usr):
  try:
    con1 = psycopg.connect(dbname=dbname, user=usr, host=host, port=port, password=pw)
  except Exception as e:
    exit_message(e)
  return(con1)


## Run psql on both nodes
def run_psql(cmd1,con1):
    try:
        cur1 = con1.cursor()
        cur1.execute(cmd1)
        print(json.dumps(cur1.fetchall()))
        ret1 = 0
        cur1.close()
    except Exception as e:
        exit_message(e)
    
    try:
        con1.close()
    except Exception as e:
        pass
    return ret1

    
## Write psql
def write_psql(cmd,host,dbname,port,pw,usr):
    ret = 1
    con = get_pg_con(host,dbname,port,pw,usr)
    try:
        cur = con.cursor()
        cur.execute(cmd)
        print(cur.statusmessage)
        ret = 0
        con.commit()
        cur.close()
    except Exception as e:
        exit_message(e)

    try:
        con.close()
    except Exception as e:
        pass
    return ret


## Read psql
def read_psql(cmd,host,dbname,port,pw,usr):
    con = get_pg_con(host,dbname,port,pw,usr)
    try:
        cur = con.cursor()
        cur.execute(cmd)
        print(cmd)
        ret = json.dumps(cur.fetchall())
        cur.close()
    except Exception as e:
        exit_message(e)

    try:
        con.close()
    except Exception as e:
        pass
    return ret


def cleanup_sub(db):
    cmd = "SELECT sub_name FROM spock.subscription"
    ret_n1, ret_n2 = run_psql(cmd)
    if "sub_n1n2" in str(ret_n1):
        cmd1 = f"spock sub-drop sub_n1n2 {db}"
        cmd2 = None
        if "sub_n2n1" in str(ret_n2):
            cmd2 = f"spock sub-drop sub_n2n1 {db}"
        run_cmd("Drop Subs",cmd1,cmd2)
        

# *****************************************************************************
## Query the SQLite Database
## The file is here: nc/pgedge/cluster/demo/n1/pgedge/data/conf
## and its name is db_local.db
# *****************************************************************************

## Create a connection to our SQLite database:

def get_sqlite_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"{conn}")
    except Error as e:
        print(e)
    return conn

## Execute a query on the SQLite database:

def execute_sqlite_query(conn):
    cur = conn.cursor()
    cur.execute(f"{query}")
    rows = cur.fetchall()
    for row in rows:
        print(row)


# *****************************************************************************
## Verify a result set
# *****************************************************************************

def contains(haystack, needle):
    print(f'haystack = ({haystack})')
    print(f'needle = ({needle})')
    
    if haystack is None and needle is None or len(haystack) == 0 and len(needle) == 0:
        return 0

    if haystack.find(needle) != -1:
        print('Haystack and needle both have content, and our value is found - this case correctly returns true')
        return 0
    else:
        print('Haystack and needle both have content, but our value is not found - returning 1 as it should')
        exit_message("Fail", p_rc=1)


    
def needle_in_haystack(haystack, needle):
    if needle in str(haystack):
      print("pass")
      exit_message("Pass", p_rc=0)
    else:
      exit_message("Fail", p_rc=1)


# *****************************************************************************
## Function to grab diff file and data from stdout
# *****************************************************************************

def get_diff_data(stdout: str) -> tuple[str, dict]:
    # current pattern expects `diffs/YYYY-MM-DD_hh:mm:ss/diff.json`
    file_pattern = r'diffs/\d{4}-\d{2}-\d{2}_\d{2}:\d{2}:\d{2}/diff\.json'
    match = re.search(file_pattern, stdout)

    if match:
        diff_file_local = match.group(0)
        diff_file_path = os.path.join(os.getenv("EDGE_HOME_DIR"), diff_file_local)
    else:
        exit_message(f"Fail - {os.path.basename(__file__)} - Couldn't find diff file", 1)

    diff_file = open(diff_file_path, "r")
    diff_data = json.load(diff_file)
    return diff_file_local, diff_data


# *****************************************************************************
## Compares data in dicts, allows lists to be out of order
# *****************************************************************************

def compare_structures(struct1, struct2) -> bool:
    if isinstance(struct1, dict) and isinstance(struct2, dict):
        if set(struct1.keys()) != set(struct2.keys()):
            return False
        return all(compare_structures(struct1[key], struct2[key]) for key in struct1)

    elif isinstance(struct1, list) and isinstance(struct2, list):
        if len(struct1) != len(struct2):
            return False
        # Sort both lists before comparison to ignore order
        sorted_struct1 = sorted(struct1, key=str)
        sorted_struct2 = sorted(struct2, key=str)
        return all(compare_structures(item1, item2) for item1, item2 in zip(sorted_struct1, sorted_struct2))

    else:
        return struct1 == struct2
    
# *****************************************************************************
## Prints the result from a command run in a nicer format since its driving me crazy
# *****************************************************************************

def printres(res: subprocess.CompletedProcess[str]) -> None:
    print(f"Command `{res.args}` ran with return code {res.returncode}")
    print("stdout:")
    for line in res.stdout.strip().split("\\n"):
        print(f"\t{line.strip()}")
    print("stderr:")
    for line in res.stderr.strip().split("\\n"):
        print(f"\t{line.strip()}")
