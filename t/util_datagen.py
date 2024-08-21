import sys, os, util_test, subprocess

import psycopg.sql
import random, string, json, time, psycopg
from datetime import datetime, timedelta
from uuid import uuid4

from ace_util import diff_assert_mismatch, rerun_assert_match, repair_assert_works

## Get Test Settings
util_test.set_env()

## Generates complicated tables for future functionality testing

# Data
_F_NAMES_ = ["Colin", "Andrew", "Peter", "Karsten", "Sabrina", "Hannah", "Ethan", "Adrian", "Ashay", "Valerie", "Ahna"]
_L_NAMES_ = ["Langella", "Pelow", "deBruin", "Braun", "Boyum", "Kipe", "Wolfe", "Tongthaworn", "Nagrani", "Zhang", "Shah"]


# Functions to Create Data for Various Datatypes
def create_full_name() -> str:
    return ' '.join([random.choice(_F_NAMES_), random.choice(_L_NAMES_)])

def create_first_name() -> str:
    return random.choice(_F_NAMES_)

def create_string(k=128) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=k))

def create_int() -> int:
    return random.randint(-100, 100)

def create_big_int() -> int:
    return random.randint(-100000, 100000)

def create_float() -> float:
    return random.uniform(-500.0, 500.0)

def create_num_list() -> list[int]:
    sz = random.randint(2, 32)
    return [create_float() for _ in range(sz)]

def create_object() -> dict:
    return {
        "str": ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
        "dat": [create_big_int() if random.randint(0, 1) == 1 else create_float() for _ in range(8)],
        "obj": {
            "name": create_first_name(),
            "friends": random.choices(_F_NAMES_, k=3),
            "value": random.randint(0, 128),
        },
    }

def create_random_time() -> datetime:
    start_date = datetime(2000, 1, 1)
    end_date = datetime(2039, 12, 31)

    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days

    random_number_of_days = random.randrange(days_between_dates)
    return start_date + timedelta(days=random_number_of_days)

# Calls proper generate function for requested type
def generate_item(item_type: str):
    if item_type == "VARCHAR(255)":
        return create_full_name()
    if item_type == "TEXT":
        return create_string()
    if item_type == "INTEGER":
        return create_int()
    if item_type == "BIGINT":
        return create_big_int()
    if item_type == "REAL":
        return create_float()
    if item_type == "FLOAT[]":
        return create_num_list()
    if item_type == "JSONB":
        return json.dumps(create_object())
    if item_type == "TIMESTAMP":
        return create_random_time()
    if item_type == "CHAR(36)":
        # note that uuid4 isn't affected by random.seed()
        # if that ever becomes a problem look into uuid3() or uuid5()
        return str(uuid4())
    util_test.exit_message("Error: wrong input type to generate_item")

# Gets env data
def get_env():
    return {
        "num_nodes": int(os.getenv("EDGE_NODES", 2)),
        "port": int(os.getenv("EDGE_START_PORT", 6432)),
        "usr": os.getenv("EDGE_USERNAME", "lcusr"),
        "pw": os.getenv("EDGE_PASSWORD", "password"),
        "host": os.getenv("EDGE_HOST", "localhost"),
        "dbname": os.getenv("EDGE_DB", "lcdb"),
    }

# Generates base seed
def get_seed():
    return random.randint(-32768, 32767)

# Gets pkey statment
def pkey_msgs():
    return {
        "serial": "id SERIAL PRIMARY KEY,",
        "uuid": "id CHAR(36) PRIMARY KEY DEFAULT (gen_random_uuid()),",
        "comp": "rand_id INTEGER NOT NULL, id SERIAL NOT NULL,",
        "none": ""
    }

# Valid pkey options
def valid_pkeys():
    return pkey_msgs().keys()

# Get all nodes
def get_all_nodes() -> list[int]:
    num_nodes = get_env()["num_nodes"]
    return [num for num in range(1,num_nodes+1)]

# Gets all connections and cursors
def get_psql_cons(nodes: list[int] = get_all_nodes()) -> tuple[list, list]:
    env_data = get_env()

    try:
        cons = [util_test.get_pg_con(env_data["host"], env_data["dbname"], env_data["port"]+n-1, env_data["pw"], env_data["usr"])
                for n in nodes]
        curs = [con.cursor() for con in cons]
    except Exception as e:
        util_test.exit_message(f"Couldn't establish connection: {e}")

    return cons, curs

# Writes diff data to testing dir
def write_diff(fname: str, data: dict) -> None:
    diff_dir = "diffs"
    if not os.path.exists(diff_dir):
        os.makedirs(diff_dir)
        print(f"Created directory {diff_dir} for diffs")

    fname += "_" + create_string(k=8) + ".json"
    diff_fname = os.path.join(diff_dir, fname)

    with open(diff_fname, "w") as file:
        json.dump(data, file, indent=2)
        print(f"Wrote diffs to {diff_fname}")

# Function to generate table into psql servers
def generate_table(
        table_name: str, form: list[tuple[str, str]],
        size: int, pkey: str = "serial",
        seed: int = None, nodes: list[int] = get_all_nodes()
    ) -> None:

    if size > 1000:
        checkpoint = size/10
        stars = 1

    if seed is None:
        seed = get_seed()

    if pkey not in valid_pkeys():
        util_test.exit_message(f"invalid option for pkey: {pkey}")

    comp_pkey = pkey == "comp"
    pkey_msg = pkey_msgs()[pkey]

    msg = f"""
Running generate table with args:
    table name: {table_name}
    form: {json.dumps(form)}
    size: {size}
    pkey: {pkey}
    seed: {seed}
    nodes: {nodes}
"""
    print(msg)
    random.seed(seed)

    # Connect to PostgreSQL
    cons, curs = get_psql_cons(nodes)

    # Create table
    psql_qry = f"""
        DROP TABLE IF EXISTS {table_name};
        CREATE TABLE {table_name} (
            {
                pkey_msg
            } {
                ', '.join([
                    f"{row_name} {row_tpye}" for row_name, row_tpye in form
                ])
            } {
                ", PRIMARY KEY(rand_id, id)" if comp_pkey else ""
            }
        );
    """

    if comp_pkey:
        form = [("rand_id", "INTEGER")] + form
    elif pkey == "uuid":
        form = [("id", "CHAR(36)")] + form

    try:
        for cur in curs:
            cur.execute(psql_qry)
    except Exception as e:
        util_test.exit_message(f"Couldn't create table: {e}")

    # Create data and write to table
    psql_qry = f"""
        INSERT INTO {table_name} ({
            ", ".join([
                row_name for row_name, _ in form
            ])
        })
        VALUES ({
            ", ".join([
                "%s" for _ in form
            ])
        });
    """

    try:
        for n in range(size):
            # Generates Items
            items = tuple([generate_item(row_type) for _, row_type in form])

            # Write to table
            for cur in curs:
                cur.execute(psql_qry, items)

            # Give some live printing for larger tables
            if size > 1000 and n == checkpoint * stars:
                print(('*' * stars) + ('.' * (10-stars)) + f" ({n}/{size})")
                stars+=1

    except Exception as e:
        util_test.exit_message(f"Error in writing to table or generating data: {e}")

    # Commit and close connections
    for con in cons:
        try:
            con.commit()
            con.close()
        except Exception as e:
            util_test.exit_message(f"Couldn't close connection: {e}")

    for cur in curs:
        try:
            cur.close()
        except Exception as e:
            util_test.exit_message(f"Couldn't close cursor: {e}")


def remove_table(table_name: str) -> None:
    # Connect to PostgreSQL
    cons, curs = get_psql_cons()

    # Remove table
    try:
        for cur in curs:
            cur.execute(f"DROP TABLE IF EXISTS {table_name};")
    except Exception as e:
        util_test.exit_message(f"Couldn't remove table: {e}")

    # Commit and close connections
    for con in cons:
        try:
            con.commit()
            con.close()
        except Exception as e:
            util_test.exit_message(f"Couldn't close connection: {e}")

    for cur in curs:
        try:
            cur.close()
        except Exception as e:
            util_test.exit_message(f"Couldn't close cursor: {e}")


def mod_and_repair(
        column: tuple[str, str], table_name: str,
        cluster = os.getenv("EDGE_CLUSTER"), pg_dir = os.getenv("EDGE_HOME_DIR"),
        action = "update", where = "mod(id, 3) = 0",
        set: str = None, verbose = False, grabDiffs = False
    ) -> tuple[int, str]:

    if not set:
        set = generate_item(column[1])
    env_data = get_env()

    if action not in {"update", "delete"}:
        util_test.exit_message(f"Invalid option for action: {action}")

    if action == "update":
        if column[1] == "FLOAT[]":
            set = f"ARRAY{set}::FLOAT[]"
        else:
            set = f"'{set}'"
        psql_qry = f"""
            UPDATE {table_name}
            SET {column[0]} = {set}
            WHERE {where}
        """
    if action == "delete":
        psql_qry = f"""
            DELETE FROM {table_name}
            WHERE {where}
        """

    msg = f"""
Running mod_and_repair with options:
    column: {column}
    table name: {table_name}
    psql qry: {psql_qry}
"""

    print(msg)

    if util_test.write_psql(psql_qry, env_data["host"], env_data["dbname"], env_data["port"]+1, env_data["pw"], env_data["usr"]) == 1:
        util_test.exit_message("Couldn't edit contents of table")

    # Use table diff to find differences and save diff file info
    start = time.time()
    found_diff, diff_file = diff_assert_mismatch(table_name, quiet=not verbose, get_diff=True)
    if grabDiffs:
        with open( os.path.join( pg_dir, diff_file ) ) as file: write_diff("MaR_run1", json.load(file))

    if not found_diff:
        return 1, "Couldn't find difference in tables"
    diff_time = time.time() - start

    # Use table repair with n1 as the source of truth
    start = time.time()
    if not repair_assert_works(table_name, diff_file, "n1", quiet=not verbose):
        return 1, "Couldn't repair differences in tables"
    repair_time = time.time()-start

    # Run with now matching info
    start = time.time()
    if not rerun_assert_match(table_name, diff_file, quiet=not verbose):
        return 1, "Differences in tables not fixed"
    rerun_time = time.time() - start

    print(f"Process took {diff_time:0.4f}s for diff, {repair_time:0.4f}s for repair, and {rerun_time:0.4f}s for rerun")

    return 0, ""


def insert_into(
        table_name: str, form: list[tuple[str, str]],
        amount: int, pkey: str = "serial",
        seed: int = None, nodes: list[int] = get_all_nodes()
    ) -> None:

    if seed is None:
        seed = get_seed()

    msg = f"""
Running insert into with args:
    table name: {table_name}
    form: {json.dumps(form)}
    size: {amount}
    pkey: {pkey}
    seed: {seed}
    nodes: {nodes}
"""
    print(msg)
    random.seed(seed)

    if pkey not in valid_pkeys():
        util_test.exit_message(f"invalid option for pkey: {pkey}")
    comp_pkey = pkey == "comp"

    # Connect to PostgreSQL
    cons, curs = get_psql_cons(nodes)

    if comp_pkey:
        form = [("rand_id", "INTEGER")] + form
    elif pkey == "uuid":
        form = [("id", "CHAR(36)")] + form

    # Write to table
    psql_qry = f"""
        INSERT INTO {table_name} ({
            ", ".join([
                row_name for row_name, _ in form
            ])
        })
        VALUES ({
            ", ".join([
                "%s" for _ in form
            ])
        });
    """

    try:
        for n in range(amount):
            # Generates Items
            items = tuple([generate_item(row_type) for _, row_type in form])

            # Write to table
            for cur in curs:
                cur.execute(psql_qry, items)

    except Exception as e:
        util_test.exit_message(f"Error in writing to table or generating data: {e}")

    # Commit and close connections
    for con in cons:
        try:
            con.commit()
            con.close()
        except Exception as e:
            util_test.exit_message(f"Couldn't close connection: {e}")

    for cur in curs:
        try:
            cur.close()
        except Exception as e:
            util_test.exit_message(f"Couldn't close cursor: {e}")


if __name__ == "__main__":
    env_data = {
        "num_nodes": int(os.getenv("EDGE_NODES", 2)),
        "port": int(os.getenv("EDGE_START_PORT", 6432)),
        "usr": os.getenv("EDGE_USERNAME", "lcusr"),
        "pw": os.getenv("EDGE_PASSWORD", "password"),
        "host": os.getenv("EDGE_HOST", "localhost"),
        "dbname": os.getenv("EDGE_DB", "lcdb"),
    }

    big_form = [
        ("name", "VARCHAR(255)"),
        ("info", "TEXT"),
        ("small_int", "INTEGER"),
        ("big_int", "BIGINT"),
        ("float_value", "REAL"),
        ("numbers", "FLOAT[]"),
        ("obj", "JSONB"),
        # ("date", "TIMESTAMP"),    (commented out to make printing nicer since datetime cannot be put into json)
    ]

    small_form = [
        ("name", "VARCHAR(255)"),
        ("info", "TEXT"),
        ("small_int", "INTEGER"),
        ("big_int", "BIGINT"),
    ]

    # Example of Use
    generate_table("t1", big_form, 10)

    with util_test.get_pg_con(env_data["host"],env_data["dbname"],env_data["port"],env_data["pw"],env_data["usr"]) as con:
        cur = con.cursor()
        cur.execute("SELECT * from t1")
        print("---------- T1 ----------")
        print(json.dumps(cur.fetchall(), indent=2))
        print()
        con.commit()
        cur.close()

    remove_table("t1")

    # Showcase of Seed
    generate_table("t1", small_form, 10, seed=42)   # should match
    generate_table("t2", small_form, 10, seed=42)   # should match
    generate_table("t3", small_form, 10)            # should not match

    with util_test.get_pg_con(env_data["host"],env_data["dbname"],env_data["port"],env_data["pw"],env_data["usr"]) as con:
        cur = con.cursor()
        cur.execute("SELECT * from t1")
        print("---------- T1 ----------")
        print(json.dumps(cur.fetchall(), indent=2))
        print()
        cur.execute("SELECT * from t2")
        print("---------- T2 ----------")
        print(json.dumps(cur.fetchall(), indent=2))
        print()
        cur.execute("SELECT * from t3")
        print("---------- T3 ----------")
        print(json.dumps(cur.fetchall(), indent=2))
        print()
        con.commit()
        cur.close()

    remove_table("t1")
    remove_table("t2")
    remove_table("t3")

