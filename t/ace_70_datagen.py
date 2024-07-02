import sys, os, util_test, subprocess
import random, string, json
from datetime import datetime, timedelta

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

num_nodes = int(os.getenv("EDGE_NODES", 2))
port = int(os.getenv("EDGE_START_PORT", 6432))
usr = os.getenv("EDGE_USERNAME", "lcusr")
pw = os.getenv("EDGE_PASSWORD", "password")
host = os.getenv("EDGE_HOST", "localhost")
dbname = os.getenv("EDGE_DB", "lcdb")

## Generates complicated tables for future functionality testing

# Data
f_names = ["Colin", "Andrew", "Peter", "Karsten", "Sabrina", "Hannah", "Ethan", "Adrian", "Ashay", "Valerie", "Ahna"]
l_names = ["Langella", "Pelow", "deBruin", "Braun", "Boyum", "Kipe", "Wolfe", "Tongthaworn", "Nagrani", "Zhang", "Shah"]
SIZE = 10 # for large stress test try 10,000

if SIZE > 1000:
    checkpoint = SIZE/10
    stars = 1

# Connect to PostgreSQL
try:
    cons = [util_test.get_pg_con(host, dbname, port+n, pw, usr) for n in range(num_nodes)]
    curs = [con.cursor() for con in cons]
except Exception as e:
    util_test.exit_message(f"Couldn't establish connection: {e}")

# Create table
for cur in curs:
    try:
        cur.execute("""
            DROP TABLE IF EXISTS random_data;
            CREATE TABLE random_data (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255),
                info TEXT,
                small_int INTEGER,
                big_int BIGINT,
                float_value REAL,
                numbers FLOAT[],
                obj JSONB,
                date TIMESTAMP
            );""")
    except Exception as e:
        util_test.exit_message(f"Couldn't create table: {e}")

# Insert data

try:
    for n in range(SIZE):

        # Create a random name for a varchar
        name = ' '.join([random.choice(f_names), random.choice(l_names)])

        # Create random info string for text
        info = ''.join(random.choices(string.ascii_letters + string.digits, k=128))

        # Create small int
        small_int = random.randint(-100, 100)

        # Create big int
        big_int = random.randint(-100000, 100000)

        # Create float
        float_value = random.uniform(-500.0, 500.0)

        # Create list of numbers
        sz = random.randint(2, 32)
        nums = [random.randint(-100000, 100000) for _ in range(sz)]

        # Create object
        obj = {
            "str": ''.join(random.choices(string.ascii_letters + string.digits, k=32)),
            "dat": [random.randint(-100000, 100000) if random.randint(0, 1) == 1 else random.uniform(-500.0, 500.0) for _ in range(16)],
            "obj": {
                "name": random.choice(f_names),
                "friends": random.choices(f_names, k=3),
                "value": random.randint(0, 128),
            },
        }

        # Create Timestamp
        start_date = datetime(2000, 1, 1)
        end_date = datetime(2039, 12, 31)
        
        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + timedelta(days=random_number_of_days)

        # Write to table
        for cur in curs:
            cur.execute("""
                INSERT INTO random_data (name, info, small_int, big_int, float_value, numbers, obj, date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""",
                (name, info, small_int, big_int, float_value, nums, json.dumps(obj), random_date))

        # Give some live printing for larger tables
        if SIZE > 1000 and n == checkpoint * stars:
            print(('*' * stars) + ('.' * (10-stars)) + f" ({n}/{SIZE})")
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

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
