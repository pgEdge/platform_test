import util_test, os, subprocess

# Utility file for ACE tests

## Get Test Settings
util_test.set_env()

home_dir = os.getenv("NC_DIR")
cluster = os.getenv("EDGE_CLUSTER")

# Statments
DIFF_MATCH    = "TABLES MATCH OK"
DIFF_COUNT    = "FOUND {number} DIFFERENCES"
DIFF_MISMATCH = "TABLES DO NOT MATCH"

# Functions
def run_table_diff(table_name: str, args: dict[str: any] = {}, call_override: str | None = None) -> subprocess.CompletedProcess[str]:
    if call_override:
        cmd_node = call_override
    else:
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


def diff_assert_mismatch(table_name: str, args: dict[str: any] = {}, quiet = False) -> bool:
    res = run_table_diff(table_name, args=args)
    if not quiet: util_test.printres(res)
    return res.returncode == 0 and DIFF_MISMATCH in res.stdout


def diff_assert_fail(table_name: str, exit_statment: str, args: dict[str: any] = {}, quiet = False, call_override: str | None = None) -> bool:
    res = run_table_diff(table_name, args=args, call_override=call_override)
    if not quiet: util_test.printres(res)
    return res.returncode != 0 and exit_statment in res.stdout