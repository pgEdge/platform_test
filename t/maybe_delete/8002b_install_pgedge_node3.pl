# This test case will install pgedge in node3 (n3) and validate it exists.

use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use File::Copy;
use lib './t/lib';
use contains;
use edge;



my $n3dir = "$ENV{EDGE_CLUSTER_DIR}/n3";
my $homedir3 = "$n3dir/pgedge";
my $cli = "$ENV{EDGE_CLI}";
my $pgversion = "$ENV{EDGE_COMPONENT}";
my $exitcode = 0;
my $myport3 = $ENV{'EDGE_START_PORT'} + 2;
my $snowflakeversion = "snowflake-$pgversion";

# Fetch the spock version from the configuration
my ($spock_ver, $ver_type) = get_spock_ver_from_config();
# Remove dots and extract the first two characters to form spock product name
my $spver = $spock_ver;
$spver =~ s/\.//g;
$spver = substr($spver, 0, 2);
my $spockversion = "spock$spver-$pgversion"; #forming the spock product name e.g. spock32-pg16

# Construct the CLI setup base command, keeping spock default (no spock version specified)
my $setup_command = qq($homedir3/$cli setup -U $ENV{EDGE_USERNAME} -P $ENV{EDGE_PASSWORD} -d $ENV{EDGE_DB} -p $myport3 --pg_ver $ENV{EDGE_INST_VERSION});

# Append the --spock_ver argument if the version type is pinned
if ($ver_type eq 'pinned') {
    $setup_command .= qq( --spock_ver $spock_ver);
}

# Install pgedge
print("pgedge setup command :  $setup_command \n");
# Run the CLI setup command
my $out_buf = (run_command_and_exit_iferr($setup_command))[3];

# Check if 'already installed' is present in stdout_buf
if (grep { /already installed/i } @$out_buf) {
    print("pgedge already installed, Exiting. Full Buffer (Install): @$out_buf\n");
    $exitcode = 0;
}

print "Setup command output: @$out_buf\n";

#check for pgV
my $cmd = qq($homedir3/$cli um list);
print("cmd = $cmd\n");
my ($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);
#print("stdout : @$full_buf \n");
if (defined($success) && !is_umlist_component_installed($stdout_buf, "$pgversion")) 
{
    print("cmd = $cmd\n");
    $exitcode=1;
} 

#check for spock
my $cmd2 = qq($homedir3/$cli um list);
print("cmd = $cmd2\n");
my ($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);
#print("stdout : @$full_buf \n");
if (defined($success2) && !is_umlist_component_installed($stdout_buf2, "$spockversion")) 
{
    $exitcode=1;
} 

#check for snowflake
my $cmd3 = qq($homedir3/$cli um list);
print("cmd = $cmd3\n");
my ($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);
#print("stdout : @$full_buf \n");
if (defined($success3) && !is_umlist_component_installed($stdout_buf3, "$snowflakeversion")) 
{
    $exitcode=1;
} 


# Set the exitcode based on component installations
exit($exitcode);