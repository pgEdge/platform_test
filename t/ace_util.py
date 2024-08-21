import util_test, os, subprocess
from psycopg.sql import Identifier
from typing import Union

# Utility file for ACE tests

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")


# STRING CONSTS
DIFF_MATCH    = "TABLES MATCH OK"
DIFF_COUNT    = "FOUND {number} DIFFS"
DIFF_MISMATCH = "TABLES DO NOT MATCH"
REP_SUCCESS   = "Successfully applied diffs to public.{table_name}"

DIFF_ERR_NOPKEY    = "No primary key found"
DIFF_ERR_NOCLUSTER = "cluster not found"
DIFF_ERR_NOTABLE   = "Invalid table name '{table_name}'"
DIFF_ERR_NODB      = "Database '{db_name}' not found in cluster '{cluster}'"
DIFF_ERR_SMALLBR   = "Block row size should be >= 1000"
DIFF_ERR_CPURANGE  = "Invalid value range for ACE_MAX_CPU_RATIO or --max_cpu_ratio"
DIFF_ERR_CPUTYPE   = "Invalid values for ACE_MAX_CPU_RATIO"
DIFF_ERR_OUTPUTF   = "table-diff currently supports only csv and json output formats"
DIFF_ERR_DUPNODE   = "Ignoring duplicate node names"
DIFF_ERR_NODFILE   = "Diff file {file_name} not found"
DIFF_ERR_NOTJSON   = "Could not load diff file as JSON"
DIFF_ERR_DFILEFORM = "Contents of diff file improperly formatted"

# GENERIC FUNCTIONS
def run_override(cmd_node: str) -> subprocess.CompletedProcess[str]:
    return util_test.run_cmd("Override", cmd_node, f"{home_dir}")


# TABLE DIFF FUNCTIONS
def run_table_diff(table_name: str, args: dict[str: any] = {}) -> subprocess.CompletedProcess[str]:
    cmd_node  = f"ace table-diff {cluster} public.{table_name}"
    cmd_node += "".join([f" { arg }={ value }" for arg, value in args.items()])
    return util_test.run_cmd("table-diff", cmd_node, f"{home_dir}")


def diff_assert_match(table_name: str, args: dict[str: any] = {}, quiet = False) -> bool:
    res = run_table_diff(table_name, args=args)
    if not quiet: util_test.printres(res)
    return res.returncode == 0 and DIFF_MATCH in res.stdout


def diff_assert_diff_count(table_name: str, expected_count: int, args: dict[str: any] = {}, quiet = False) -> bool:
    res = run_table_diff(table_name, args=args)
    if not quiet: util_test.printres(res)
    return res.returncode == 0 and DIFF_COUNT.format( number=expected_count ) in res.stdout


def diff_assert_mismatch(table_name: str, args: dict[str: any] = {}, quiet = False, get_diff = False) -> Union[bool, tuple[bool, str]]:
    res = run_table_diff(table_name, args=args)
    if not quiet: util_test.printres(res)
    ret = res.returncode == 0 and DIFF_MISMATCH in res.stdout
    if get_diff:
        diff_file, _ = util_test.get_diff_data(res.stdout)
        return ret, diff_file
    return ret


def diff_assert_fail(table_name: str, exit_statment: str, args: dict[str: any] = {}, quiet = False, call_override: str = None) -> bool:
    if call_override: res = run_override(call_override)
    else: res = run_table_diff(table_name, args=args)
    if not quiet: util_test.printres(res)
    return res.returncode != 0 and exit_statment in res.stdout


# REPSET FUNCTIONS


# SPOCK DIFF FUNCTIONS


# SCHEMA DIFF FUNCTIONS


# RERUN FUNCTIONS
def run_table_rerun(table_name: str, diff_file: str, args: dict[str: any] = {}) -> subprocess.CompletedProcess[str]:
    cmd_node  = f"ace table-rerun {cluster} {diff_file} public.{table_name}"
    cmd_node += "".join([f" { arg }={ value }" for arg, value in args.items()])
    return util_test.run_cmd("table-diff", cmd_node, f"{home_dir}")


def rerun_assert_match(table_name: str, diff_file: str, args: dict[str: any] = {}, quiet = False) -> bool:
    res = run_table_rerun(table_name, diff_file, args=args)
    if not quiet: util_test.printres(res)
    return res.returncode == 0 and DIFF_MATCH in res.stdout


def rerun_assert_diff_count(table_name: str, diff_file: str, expected_count: int, args: dict[str: any] = {}, quiet = False) -> bool:
    res = run_table_rerun(table_name, diff_file, args=args)
    if not quiet: util_test.printres(res)
    return res.returncode == 0 and DIFF_COUNT.format( number=expected_count ) in res.stdout


def rerun_assert_mismatch(table_name: str, diff_file: str, args: dict[str: any] = {}, quiet = False, get_diff = False) -> Union[bool, tuple[bool, str]]:
    res = run_table_rerun(table_name, diff_file, args=args)
    if not quiet: util_test.printres(res)
    ret = res.returncode == 0 and DIFF_MISMATCH in res.stdout
    if get_diff:
        diff_file, _ = util_test.get_diff_data(res.stdout)
        return ret, diff_file
    return ret


def rerun_assert_fail(table_name: str, diff_file: str, exit_statment: str, args: dict[str: any] = {}, quiet = False, call_override: str = None) -> bool:
    if call_override: res = run_override(call_override)
    else: res = run_table_rerun(table_name, diff_file, args=args)
    if not quiet: util_test.printres(res)
    return res.returncode != 0 and exit_statment in res.stdout


# REPAIR FUNCTIONS
def run_table_repair(table_name: str, diff_file: str, source_of_truth: str, args: dict[str: any] = {}) -> subprocess.CompletedProcess[str]:
    cmd_node  = f"ace table-repair {cluster} {diff_file} {source_of_truth} public.{table_name}"
    cmd_node += "".join([f" { arg }={ value }" for arg, value in args.items()])
    return util_test.run_cmd("table-diff", cmd_node, f"{home_dir}")


def repair_assert_works(table_name: str, diff_file: str, source_of_truth: str, args: dict[str: any] = {}, quiet = False) -> bool:
    res = run_table_repair(table_name, diff_file, source_of_truth, args=args)
    if not quiet: util_test.printres(res)
    return res.returncode == 0 and REP_SUCCESS.format( table_name=table_name ) in res.stdout
