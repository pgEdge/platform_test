import sys, os, util_test, subprocess
import random, string, json
from datetime import datetime, timedelta

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

def create_string() -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=128))

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
    util_test.exit_message("Error: wrong input type to generate_item")


# Function to generate table into psql servers
def generate_table(table_name: str, form: dict, size: int) -> None:
    # Load env_data into dict to prevent possible variable name conflicts
    env_data = {
        "num_nodes": int(os.getenv("EDGE_NODES", 2)),
        "port": int(os.getenv("EDGE_START_PORT", 6432)),
        "usr": os.getenv("EDGE_USERNAME", "lcusr"),
        "pw": os.getenv("EDGE_PASSWORD", "password"),
        "host": os.getenv("EDGE_HOST", "localhost"),
        "dbname": os.getenv("EDGE_DB", "lcdb"),
    }

    if size > 1000:
        checkpoint = size/10
        stars = 1

    # Connect to PostgreSQL
    try:
        cons = [util_test.get_pg_con(env_data["host"], env_data["dbname"], env_data["port"]+n, env_data["pw"], env_data["usr"])
                for n in range(env_data["num_nodes"])]
        curs = [con.cursor() for con in cons]
    except Exception as e:
        util_test.exit_message(f"Couldn't establish connection: {e}")

    # Create table
    psql_qry = f"""
        DROP TABLE IF EXISTS {table_name};
        CREATE TABLE {table_name} (
            id SERIAL PRIMARY KEY,
            {
                ', '.join([
                    f"{row_name} {row_tpye}" for row_name, row_tpye in form
                ])
            }
        );
    """

    try:
        for cur in curs:
            cur.execute(psql_qry)
    except Exception as e:
        util_test.exit_message(f"Couldn't create table: {e}")

    # Create data and write to table
    psql_qry = f"""
        INSERT INTO {table_name} (name, info, small_int, big_int, float_value, numbers, obj, date)
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
    # Load env_data into dict to prevent possible variable name conflicts
    env_data = {
        "num_nodes": int(os.getenv("EDGE_NODES", 2)),
        "port": int(os.getenv("EDGE_START_PORT", 6432)),
        "usr": os.getenv("EDGE_USERNAME", "lcusr"),
        "pw": os.getenv("EDGE_PASSWORD", "password"),
        "host": os.getenv("EDGE_HOST", "localhost"),
        "dbname": os.getenv("EDGE_DB", "lcdb"),
    }

    # Connect to PostgreSQL
    try:
        cons = [util_test.get_pg_con(env_data["host"], env_data["dbname"], env_data["port"]+n, env_data["pw"], env_data["usr"])
                for n in range(env_data["num_nodes"])]
        curs = [con.cursor() for con in cons]
    except Exception as e:
        util_test.exit_message(f"Couldn't establish connection: {e}")

    # Remove table
    try:
        for cur in curs:
            cur.execute(f"DROP TABLE IF EXISTS {table_name};")
    except Exception as e:
        util_test.exit_message(f"Couldn't remove table: {e}")


if __name__ == "__main__":
    # Example of Use
    generate_table("t1", [
        ("name", "VARCHAR(255)"),
        ("info", "TEXT"),
        ("small_int", "INTEGER"),
        ("big_int", "BIGINT"),
        ("float_value", "REAL"),
        ("numbers", "FLOAT[]"),
        ("obj", "JSONB"),
        ("date", "TIMESTAMP"),
    ], 10)

    remove_table("t1")
