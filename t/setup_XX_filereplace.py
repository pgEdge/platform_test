import sys, os, util_test, subprocess
import shutil

## Print Script
print(f"Starting - {os.path.basename(__file__)}")

## Get Test Settings
util_test.set_env()

tempdir = "tempfiles"
homedir = os.getenv("EDGE_HOME_DIR")
scripts = os.path.join(homedir, "hub", "scripts")

## Optional Setup Script- Gives Ability to Test CLI Files not in Upstream

filenames = []

# Checks if pgedge is setup
if not os.path.exists(scripts):
    util_test.exit_message("File Replace can only be called after pgedge is installed")

# Checks if there is a tempfile folder
if not os.path.exists(tempdir):
    util_test.exit_message("No temp file directory found, if you intend to use one should be platform_test/tempfiles", 0)

for fname in filenames:
    temppath = os.path.join(tempdir, fname)
    edgepath = os.path.join(scripts, fname)

    if not os.path.exists(temppath):
        util_test.exit_message("Can't find file to use")
    if not os.path.exists(edgepath):
        util_test.exit_message("No such file to replace")

    shutil.copyfile(temppath, edgepath)
    print(f"Copied from {temppath} to {edgepath}")


util_test.exit_message(f"Pass - {os.path.basename(__file__)}", 0)
