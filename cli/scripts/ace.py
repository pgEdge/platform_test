#####################################################
#  Copyright 2022-2023 PGEDGE  All rights reserved. #
#####################################################

"""ACE is the place of the Anti Chaos Engine"""

import os, sys, random, time, json, socket, subprocess, re
import util, fire, meta, pgbench, cluster

l_dir = "/tmp"

try:
  import psycopg
except ImportError as e:
  util.exit_message("Missing 'psycopg' module from pip", 1)


def get_pg_v(pg):
  pg_v = str(pg)

  if pg_v.isdigit():
    pg_v = "pg" + str(pg_v)

  if pg_v == "None":
    k = 0
    pg_s = meta.get_installed_pg()

    for p in pg_s:
      k = k + 1

    if k == 1:
      pg_v = str(p[0])
    else:
      util.exit_message("must be one PG installed", 1)

  if not os.path.isdir(pg_v):
    util.exit_message(str(pg_v) + " not installed", 1)

  return(pg_v)


def get_pg_connection(pg_v, db, ip, usr):
  dbp = util.get_column("port", pg_v)

  if util.debug_lvl() > 0:
    util.message(f"get_pg_connection(): dbname={db}, user={usr}, port={dbp}", "debug")

  try:
    con = psycopg.connect(dbname=db, user=usr, host=ip, port=dbp, autocommit=False)
  except Exception as e:
    util.exit_exception(e)

  return(con)

def run_psyco_sql(pg_v, db, cmd, ip, usr=None):
  if usr == None:
    usr = util.get_user()

  if util.is_verbose():
    util.message(cmd, "info")

  if util.debug_lvl() > 0:
    util.message(cmd, "debug")

  con = get_pg_connection(pg_v, db, ip, usr)
  if util.debug_lvl() > 0:
    util.message("run_psyco_sql(): " + str(con), "debug")

  try:
    cur = con.cursor(row_factory=psycopg.rows.dict_row)
    cur.execute(cmd)
    con.commit()

    return cur.fetchall()
    try:
      cur.close()
      con.close()
    except Exception as e:
      pass

  except Exception as e:
      util.exit_exception(e)

def prCyan(skk): print("\033[96m {}\033[00m" .format(skk))
def prRed(skk): print("\033[91m {}\033[00m" .format(skk))


def get_csv_file_name(p_prfx, p_schm, p_tbl, p_base_dir="/tmp"):
  return(p_base_dir + os.sep + p_prfx + "-" + p_schm + "-" + p_tbl + ".csv")


def get_dump_file_name(p_prfx, p_schm, p_base_dir="/tmp"):
  return(p_base_dir + os.sep + p_prfx + "-" + p_schm + ".sql")


def write_tbl_csv(p_con, p_prfx, p_schm, p_tbl, p_cols, p_key, p_base_dir=None):
  try:
    out_file = get_csv_file_name(p_prfx, p_schm, p_tbl, p_base_dir)

    cur = p_con.cursor()

    sql = "SELECT " + p_cols + " " + \
          "  FROM " + p_schm + "." + p_tbl + " " + \
          "ORDER BY " + p_key

    copy_sql = "COPY (" + sql + ") TO STDOUT WITH DELIMITER ',' CSV HEADER;"

    util.message("\n## COPY table " + p_tbl + " to " + out_file + " #############")

    with open(out_file, "wb") as f:
      with cur.copy(copy_sql) as copy:
        for data in copy:
          f.write(data)

    with open(out_file, 'r') as fp:
      lines = len(fp.readlines())

    util.message(" detail rows = " + str(format(lines - 1, "n")))
  except Exception as e:
    util.exit_message("Error in write_tbl_csv():\n" + str(e), 1)

  return(out_file)


def write_pg_dump(p_ip, p_db, p_prfx, p_schm, p_base_dir="/tmp"):
  out_file = get_dump_file_name(p_prfx, p_schm, p_base_dir)
  try:
    cmd = "pg_dump -s -n " + p_schm + " -h " + p_ip + " -d " +  p_db + " > " + out_file
    os.system(cmd)
  except Exception as e:
      util.exit_exception(e)
  return(out_file)


def get_cols(p_con, p_schema, p_table):
  sql = """
SELECT ordinal_position, column_name
  FROM information_schema.columns
 WHERE table_schema = %s and table_name = %s
ORDER BY 1, 2
"""

  try:
    cur = p_con.cursor()
    cur.execute(sql,[p_schema, p_table,])
    rows = cur.fetchall()
    cur.close()
  except Exception as e:
    util.exit_message("Error in get_cols():\n" + str(e), 1)

  if not rows:
    return(None)

  col_lst = []
  for row in rows:
    col_lst.append(str(row[1]))

  return(','.join(col_lst))


def get_key(p_con, p_schema, p_table):
  sql = """
SELECT C.COLUMN_NAME
  FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS T  , INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE C
 WHERE c.constraint_name = t.constraint_name
   AND c.table_schema = t.constraint_schema
   AND c.table_schema = %s AND c.table_name = %s
   AND T.CONSTRAINT_TYPE='PRIMARY KEY'
"""

  try:
    cur = p_con.cursor()
    cur.execute(sql,[p_schema, p_table,])
    rows = cur.fetchall()
    cur.close()
  except Exception as e:
   util.exit_message("Error in get_key():\n" + str(e), 1)

  if not rows:
    return(None)

  key_lst = []
  for row in rows:
    key_lst.append(str(row[0]))

  return(','.join(key_lst))


def diff_schemas(cluster_name, node1, node2, schema_name):
  """Compare schema on different cluster nodes"""
  if not os.path.isfile("/usr/local/bin/csvdiff"):
    util.message("Installing the required 'csvdiff' component.")
    os.system("./nodectl install csvdiff")

  util.message(f"## Validating Cluster {cluster_name} exists")
  util.check_cluster_exists(cluster_name)

  if node1 == node2:
    util.exit_message("node1 must be different than node2")
    
  l_schema = schema_name

  db, pg, count, usr, cert, nodes = cluster.load_json(cluster_name)
  util.message(f"## db={db}, user={usr}\n")
  for nd in nodes:
    if nd["nodename"] == node1:
      sql1 = write_pg_dump(nd["ip"], db, "con1", l_schema)
    if nd["nodename"] == node2:
      sql2 = write_pg_dump(nd["ip"], db, "con2", l_schema)

  cmd = "diff " + sql1 + "  " + sql2 + " > /tmp/diff.txt"
  util.message("\n## Running # " + cmd + "\n")
  rc = os.system(cmd)
  if rc == 0:
    util.message("SCHEMAS ARE SAME!!")
    return(rc)
  else:
    util.message("SCHEMAS ARE NOT THE SAME!!")
    return(1)


def diff_spock(cluster_name, node1, node2):
  """Compare spock setup on different cluster nodes"""
  util.check_cluster_exists(cluster_name)

  if node1 == node2:
    util.exit_message("node1 must be different than node2")

  db, pg, count, usr, cert, cluster_nodes = cluster.load_json(cluster_name)
  compare_spock=[]
  pg_v = get_pg_v(pg)
  print("\n")

  for cluster_node in cluster_nodes:
    if cluster_node["nodename"] not in [node1, node2]:
      continue
    diff_spock={}
    diff_sub={}
    hints=[]
    print(" Spock - Config " + cluster_node["nodename"])
    print("~~~~~~~~~~~~~~~~~~~~~~~~~")
    prCyan("Node:")
    sql = """
    SELECT n.node_id, n.node_name, n.location, n.country,
           s.sub_id, s.sub_name, s.sub_enabled, s.sub_replication_sets
           FROM spock.node n LEFT OUTER JOIN spock.subscription s
           ON s.sub_target=n.node_id WHERE s.sub_name IS NOT NULL;
    """
    node_info = run_psyco_sql(pg_v, db, sql, cluster_node["ip"])
    print("  " + node_info[0]["node_name"])
    diff_spock["node"]=node_info[0]["node_name"]

    prCyan("  Subscriptions:")

    for node in node_info:
      if node["sub_name"] == None:
        hints.append("Hint: No subscriptions have been created on this node")
      else:
        print("    " + node["sub_name"])
        diff_sub["sub_name"]=node["sub_name"]
        diff_sub["sub_enabled"]=node["sub_enabled"]
        prCyan("    RepSets:")
        diff_sub["replication_sets"]=node["sub_replication_sets"]
        print("      " + json.dumps(node["sub_replication_sets"]))
        if node["sub_replication_sets"] == []:
          hints.append("Hint: No replication sets added to subscription")
        elif node["sub_replication_sets"] == ["default", "default_insert_only", "ddl_sql"]:
          hints.append("Hint: Only default replication sets added to subscription: " + node["sub_name"])
        diff_spock["subscriptions"]= diff_sub

    sql = """
    SELECT set_name, string_agg(relname,'   ') as relname FROM spock.tables GROUP BY set_name ORDER BY set_name;
    """
    table_info = run_psyco_sql(pg_v, db, sql, cluster_node["ip"])
    diff_spock["rep_set_info"]=[]
    prCyan("Tables in RepSets:")
    if table_info==[]:
        hints.append("Hint: No tables in database")
    for table in table_info:
      if table["set_name"] == None:
        print(" - Not in a replication set")
        hints.append("Hint: Tables not in replication set might not have primary keys, or you need to run repset-add-table")
      else:
        print(" - " + table["set_name"])
      
      diff_spock["rep_set_info"].append({table["set_name"]:table["relname"]})
      print("   - " + table["relname"])
        
    compare_spock.append(diff_spock)
    for hint in hints:
      prRed(hint)
    print("\n")

  if len(compare_spock) == 2: 
    print(" Spock - Diff") 
    print("~~~~~~~~~~~~~~~~~~~~~~~~~")
    if compare_spock[0]["rep_set_info"] == compare_spock[1]["rep_set_info"]:
      prCyan("   Replication Rules are the same!!")
    else:
      prRed("    Difference in Replication Rules")
  
  ##print(json.dumps(compare_spock,indent=2))
  return(compare_spock)


def diff_tables(cluster_name, node1, node2, table_name):
  """Compare table on different cluster nodes"""

  if not os.path.isfile("/usr/local/bin/csvdiff"):
    util.message("Installing the required 'csvdiff' component.")
    os.system("./nodectl install csvdiff")

  util.message(f"## Validating Cluster {cluster_name} exists")
  util.check_cluster_exists(cluster_name)

  if node1 == node2:
    util.exit_message("node1 must be different than node2")

  ##util.message(f"## Validating nodes {node1} & {node2} exist\n")
  ##util.check_node_exists(cluster_name, node1)
  ##util.check_node_exists(cluster_name, node2)

  nm_lst = table_name.split(".")
  if len(nm_lst) != 2:
    util.exit_message("TableName must be of form 'schema.table_name'")
  l_schema = nm_lst[0]
  l_table = nm_lst[1]
  util.message(f"## schema={l_schema}, table={l_table}")

  db, pg, count, usr, cert, nodes = cluster.load_json(cluster_name)
  util.message(f"## db={db}, user={usr}\n")
  con1 = None
  con2 = None
  try:
    for nd in nodes:
      if nd["nodename"] == node1:
        util.message("## Getting Conection to Node1 - " + nd["ip"] + ":" + str(nd["port"]))
        con1 = psycopg.connect(dbname=db, user=usr, host=nd["ip"], port=nd["port"])

      if nd["nodename"] == node2:
        util.message("## Getting Conection to Node2 - " + nd["ip"] + ":" + str(nd["port"]) + "\n")
        con2 = psycopg.connect(dbname=db, user=usr, host=nd["ip"], port=nd["port"])

  except Exception as e:
    util.exit_message("Error in diff_tbls():\n" + str(e), 1)

  c1_cols = get_cols(con1, l_schema, l_table)
  c1_key = get_key(con1, l_schema, l_table)
  if c1_cols and c1_key:
    util.message(f"## con1 cols={c1_cols}  key={c1_key}")
  else:
    util.exit_message("Table w/ Primary Key not in con1")

  c2_cols = get_cols(con2, l_schema, l_table)
  c2_key = get_key(con2, l_schema, l_table)
  if c2_cols and c2_key:
    util.message(f"## con2 cols={c2_cols}  key={c2_key}")
  else:
    util.exit_message("Table w/ Primary Key not in con2")

  if (c1_cols != c2_cols) or (c1_key != c2_key):
    util.exit_message("Tables don't match in con1 & con2")

  csv1 = write_tbl_csv(con1, "con1", l_schema, l_table, c1_cols, c1_key, l_dir)

  csv2 = write_tbl_csv(con2, "con2", l_schema, l_table, c2_cols, c2_key, l_dir)

  cmd = "csvdiff -o json " + csv1 + "  " + csv2
  util.message("\n## Running # " + cmd + "\n")
  diff_s = subprocess.check_output(cmd, shell=True)
  diff_j = json.loads(diff_s)

  if diff_j['Additions'] or diff_j['Deletions'] or diff_j['Modifications']:
    print(json.dumps(diff_j, indent=2))
    rc = 1
  else:
    util.message("TABLES ARE SAME!!")
    rc = 0

  return(rc)


if __name__ == '__main__':
  fire.Fire({
    'diff-tables':    diff_tables,
    'diff-schemas':   diff_schemas,
    'diff-spock':     diff_spock
  })