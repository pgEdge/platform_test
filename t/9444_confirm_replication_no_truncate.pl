# This test case confirms that insert statements are not 
# replicated on node 2.

use strict;
use warnings;

use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;


# Our parameters are:

my $username = "lcusr";
my $password = "password";
my $database = "lcdb";
my $version = "pg17";
my $spock = "3.2";
my $cluster = "demo";
my $repset = "demo-repset";
my $n1 = "~/work/nodectl/test/pgedge/cluster/demo/n1";
my $n2 = "~/work/nodectl/test/pgedge/cluster/demo/n2";

# We can retrieve the home directory from nodectl in json form... 
my $json = `$n1/pgedge/nc --json info`;
#print("my json = $json");
my $out = decode_json($json);
my $homedir = $out->[0]->{"home"};
print("The home directory of n1 is {$homedir}\n");

# We can retrieve the port number from nodectl in json form...
my $json2 = `$n1/pgedge/nc --json info $version`;
#print("my json = $json2");
my $out2 = decode_json($json2);
my $port = $out2->[0]->{"port"};
print("The port number of n1 is {$port}\n");

# We can retrieve the home directory from nodectl in json form... 
my $json3 = `$n2/pgedge/nc --json info`;
#print("my json = $json3");
my $out3 = decode_json($json3);
my $homedir2 = $out3->[0]->{"home"};
print("The home directory of n2 is {$homedir2}\n");

# We can retrieve the port number from nodectl in json form...
my $json4 = `$n2/pgedge/nc --json info $version`;
#print("my json = $json4");
my $out4 = decode_json($json4);
my $port2 = $out4->[0]->{"port"};
print("The port number of n2 is {$port2}\n");

# Connect to psql on node 1 and truncate 'foo':
#

my $cmd28 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "TRUNCATE TABLE foo");
print("cmd28 = $cmd28\n");
my($success28, $error_message28, $full_buf28, $stdout_buf28, $stderr_buf28)= IPC::Cmd::run(command => $cmd28, verbose => 0);
print("stdout_buf = @$stdout_buf28\n");
print("We've just added 777 to the foo table on $n1 using $port\n");

# Test to see if replication is working on node 2

my $cmd29 = qq($homedir2/$version/bin/psql -t -h 127.0.0.1 -p $port2 -d $database -c "SELECT * FROM foo");
print("cmd29 = $cmd29\n");
my($success29, $error_message29, $full_buf29, $stdout_buf29, $stderr_buf29)= IPC::Cmd::run(command => $cmd29, verbose => 0);
# print("stdout_buf = @$stdout_buf29\n");

print("If 777 is in our search string from $n2 listening on $port2 the cluster is replicating insert statements and this script 
	should exit.\n");

if(!(contains(@$stdout_buf29[0], "3")))
{
    exit(1);
}

# Add a record to node 1 so we can test later:

my $cmd9 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "INSERT INTO foo VALUES ('1')");
print("cmd9 = $cmd9\n");
my($success9, $error_message9, $full_buf9, $stdout_buf9, $stderr_buf9)= IPC::Cmd::run(command => $cmd9, verbose => 0);
print("stdout_buf = @$stdout_buf9\n");

print("We're just adding a value so we have something to check for in our truncated table.\n");


# Connect to psql on node 2 and truncate 'foo':
#

my $cmd38 = qq($homedir2/$version/bin/psql -t -h 127.0.0.1 -p $port2 -d $database -c "TRUNCATE TABLE foo");
print("cmd38 = $cmd38\n");
my($success38, $error_message38, $full_buf38, $stdout_buf38, $stderr_buf38)= IPC::Cmd::run(command => $cmd38, verbose => 0);
print("stdout_buf38 = @$stdout_buf38\n");
print("We've just added 888 to the foo table on $n2 using $port2\n");

# Test to see if replication is working on node 1

my $cmd39 = qq($homedir/$version/bin/psql -t -h 127.0.0.1 -p $port -d $database -c "SELECT * FROM foo");
print("cmd39 = $cmd39\n");
my($success39, $error_message39, $full_buf39, $stdout_buf39, $stderr_buf39)= IPC::Cmd::run(command => $cmd39, verbose => 0);
print("stdout_buf = @$stdout_buf39\n");

print("If 1 is not in our search string from $n1 listening on $port the cluster is replicating truncate statements and this script 
        should exit with fail.\n");

# Test for the search_term in a buffer.

if (contains(@$stdout_buf39[0], "1"))

{
    exit(0);
}
else
{
    exit(1);
}

