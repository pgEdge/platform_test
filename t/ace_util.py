import util_test, os, subprocess

# Utility file for ACE tests

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")


# STRING CONSTS
DIFF_MATCH    = "TABLES MATCH OK"
DIFF_COUNT    = "FOUND {number} DIFFERENCES"
DIFF_MISMATCH = "TABLES DO NOT MATCH"

DIFF_ERR_NOPKEY    = "No primary key found"
DIFF_ERR_NOCLUSTER = "cluster not found"
DIFF_ERR_NOTABLE   = "Invalid table name '{table_name}'"


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


def diff_assert_mismatch(table_name: str, args: dict[str: any] = {}, quiet = False, get_diff = False) -> bool | tuple[bool, str]:
    res = run_table_diff(table_name, args=args)
    if not quiet: util_test.printres(res)
    ret = res.returncode == 0 and DIFF_MISMATCH in res.stdout
    if get_diff:
        diff_file, _ = util_test.get_diff_data(res.stdout)
        return ret, diff_file
    return ret


def diff_assert_fail(table_name: str, exit_statment: str, args: dict[str: any] = {}, quiet = False, call_override: str | None = None) -> bool:
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


def rerun_assert_mismatch(table_name: str, diff_file: str, args: dict[str: any] = {}, quiet = False, get_diff = False) -> bool | tuple[bool, str]:
    res = run_table_rerun(table_name, diff_file, args=args)
    if not quiet: util_test.printres(res)
    ret = res.returncode == 0 and DIFF_MISMATCH in res.stdout
    if get_diff:
        diff_file, _ = util_test.get_diff_data(res.stdout)
        return ret, diff_file
    return ret


def diff_assert_fail(table_name: str, diff_file: str, exit_statment: str, args: dict[str: any] = {}, quiet = False, call_override: str | None = None) -> bool:
    if call_override: res = run_override(call_override)
    else: res = run_table_rerun(table_name, diff_file, args=args)
    if not quiet: util_test.printres(res)
    return res.returncode != 0 and exit_statment in res.stdout


# REPAIR FUNCTIONS
