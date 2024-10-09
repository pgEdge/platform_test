import sys, os, util_test, subprocess, random, time

import psycopg, psycopg.rows
import multiprocessing

import ace_util

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")

port=int(os.getenv("EDGE_START_PORT",6432))
usr=os.getenv("EDGE_USERNAME","lcusr")
pw=os.getenv("EDGE_PASSWORD","password")
host=os.getenv("EDGE_HOST","localhost")
dbname=os.getenv("EDGE_DB","lcdb")
num_nodes=int(os.getenv("EDGE_NODES",2))


# Generic representation of a PGCon that works with needed settings
# and increases performance relative to existsing functions
class PGCon:

    # Set up connection and cursor
    def __init__(self, db: str, usr: str, psw: str, host: str, port: int, verbose = False):
        try:
            self.con = psycopg.connect( dbname = db, user = usr, password = psw, host = host, port = port, autocommit = False )
            self.cur = self.con.cursor( row_factory = psycopg.rows.dict_row )
            self.verbose = verbose
            self.port = port
        except Exception as e:
            util_test.exit_message( f"Couldn't connect to PG: {e}" )


    # Closes connection and cursor
    def __del__(self):
        try:
            self.cur.close()
            self.con.close()
        except Exception as e:
            print( f"Could not close correctly: {e}" )


    # Runs specified command, returning all results
    def run (self, cmd: str) -> list[psycopg.rows.DictRow]:
        try:
            if self.verbose:
                print( f"Port {self.port}: Running `{cmd}`" )
            
            self.cur.execute( cmd )
            try:
                output = self.cur.fetchall()
            except Exception as e:
                output = None
            self.con.commit()
            return output
        except Exception as e:
            util_test.exit_message( f"Couldn't run command `{cmd}`: {e}" )


# Class to hold main test functions, keeps track of shared information
class Tester:

    # Initilizes with a random or set seed and creates shared objects
    def __init__(self, Runners: list[PGCon], seed = random.randint(-32768, 32767), verbose = False):
        self.Runners = Runners
        self.verbose = verbose
        self.manager        = multiprocessing.Manager()
        self.shared_list    = self.manager.list()
        self.snowflake_list = self.manager.list()
        random.seed(seed)
        print( f"Initializing Test with seed: {seed}" )


    # Creates and runs a randomized ddl statment
    def run_random_ddl( self, Runner: PGCon ) -> None:
        shared = self.shared_list
        ddl = random.randint(0, 99)
        col_name = f"col_{random.randint(0, 999999):06}"

        # If there is only one column remaing add another regardless
        if len(shared) < 2: ddl = 1
        else:               random_col = random.randrange(len(shared))

        # 25% Add column case
        if   ddl < 25:
            cmd = f"ALTER TABLE test ADD COLUMN {col_name} varchar(10)"
            shared.append(col_name)

        # 25% Rename column case
        elif ddl < 50:
            cmd = f"ALTER TABLE test RENAME COLUMN {shared[random_col]} TO {col_name}"
            shared.pop(random_col)
            shared.append(col_name)

        # 25% Drop column case
        elif ddl < 75:
            cmd = f"ALTER TABLE test DROP COLUMN {shared[random_col]}"
            shared.pop(random_col)

        # 25% Change column type case
        else:
            if   ddl < 80: col_type = "varchar(30)"
            elif ddl < 90: col_type = "varchar(40)"
            else:          col_type = "varchar(50)"
            cmd = f"ALTER TABLE test ALTER COLUMN {shared[random_col]} TYPE {col_type}"

        Runner.run( cmd )
        return


    # Creates and runs a randomized command
    def run_random_cmd( self ):
        shared = self.shared_list
        snowflake_list = self.snowflake_list
        opt = random.randint(0, 99)
        Runner = random.choice( self.Runners )

        # If there are too few items do an insert regardless
        if len(snowflake_list) < 3 and opt < 90: opt = 1
        elif opt < 90:                           offset = random.randrange(len(snowflake_list))

        # 30% Insert Case
        if opt < 30:
            cmd = f"INSERT INTO test ({', '.join(shared)}) VALUES ({str(shared)[1:-1]}) returning id"
            id = Runner.run( cmd )[0]['id']
            snowflake_list.append(id)

            if self.verbose:
                print( len(snowflake_list) )

        # 30% Update Case
        elif opt < 60:
            cmd = f"UPDATE test SET {shared[-1]} = 'update' WHERE id = {snowflake_list[offset]}"
            Runner.run( cmd )

            if self.verbose:
                print( shared )
                print( snowflake_list )

        # 30% Delete Case
        elif opt < 90:
            cmd =f"DELETE FROM test WHERE id = {snowflake_list[offset]}"
            Runner.run( cmd )
            snowflake_list.pop( offset )

        # 10% DDL Case
        else: self.run_random_ddl( Runner )


# Runs random commands until test is over
def run_test( tester: Tester, end_time: float ):
    while time.time() < end_time:
        tester.run_random_cmd()
        #time.sleep(1)


# ----- Start Tests -----

# Temp Config
dur_time = 30
threads  = 10

# Init Classes
runners = [ PGCon( dbname, usr, pw, host, int( port ) + i, verbose = True ) for i in range( 1 ) ]
tester = Tester( runners )

# Sets up table
runners[0].run( "DROP TABLE IF EXISTS test CASCADE" )
runners[0].run( "SET snowflake.node = 1" )
runners[0].run( "CREATE TABLE test (id bigint DEFAULT snowflake.nextval() PRIMARY KEY, col_a varchar(20), col_b varchar(20), col_c varchar(20))" )
tester.shared_list.extend(['col_a','col_b','col_c'])

# Creates Processes
end_time = time.time() + dur_time
jobs = list()

for i in range( threads ):
    process = multiprocessing.Process( run_test( tester, end_time ) )
    jobs.append( process )

# Runs Processes
for job in jobs:
    job.start()

# Waits for Procesess to Finish
for job in jobs:
    job.join()

# Exit Report
print("\n\n")
print(f"Total number of rows is {len(tester.snowflake_list)}")
print(f"Ending table has these columns: {tester.shared_list}")
print("\n\n")

# Assert that changes replicated

b1 = ace_util.assert_spock_match()
b2 = ace_util.assert_schema_match()
b3 = ace_util.diff_assert_match("test")

if not (b1 and b2 and b3):
    util_test.exit_message( f"Failed at least one of the final checks: spock {b1}, schema {b2}, table {b3}." )

util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
