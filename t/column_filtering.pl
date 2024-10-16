# This is part of a complex test case; after creating a two node cluster on the localhost, 

# the test case tells us how data can be filtered by column filteration

use strict;
use warnings;
use File::Which;
use IPC::Cmd qw(run);
use Try::Tiny;
use JSON;
use lib './t/lib';
use contains;
use edge;
use DBI;
use List::MoreUtils qw(pairwise);
no warnings 'uninitialized';

# Our parameters are:
#pgedge home directory for n1
my $homedir1="$ENV{EDGE_CLUSTER_DIR}/n1/pgedge";
print("whoami = $ENV{EDGE_REPUSER}\n");
print("The home directory is $homedir1\n"); 
print("The port number is $ENV{EDGE_START_PORT}\n");

#pgedge home directory for n2
my $homedir2="$ENV{EDGE_CLUSTER_DIR}/n2/pgedge";
#increment 1 to the default port for use with node n2
my $myport2 = $ENV{'EDGE_START_PORT'} + 1;
print("The home directory is $homedir2\n"); 
print("The port number is $myport2\n");
print ("-"x50,"\n"); 

##Source the environment variables on node 1:

my $cmd = qq(source $homedir1/$ENV{EDGE_COMPONENT}/pg16.env);
print("cmd = $cmd\n");
my($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);
##
print("full_buf = @$full_buf\n");
print("stdout_buf = @$stdout_buf\n");
print("stderr_buf = @$stderr_buf\n");

# I removed the check for the tables existence (since we can include the IF NOT EXISTS clause in the command):
# Creating public.$ENV{EDGE_TABLE} Table
  
my $cmd1 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "CREATE TABLE IF NOT EXISTS public.employee (
emp_id smallint Primary Key,
emp_govt_id varchar(15),
emp_first_name varchar(40),
emp_last_name varchar(40),
emp_address varchar(50),
emp_city_state varchar(15),
emp_country varchar(2),
emp_birth_date date,
emp_division varchar(7),
emp_date_added date);");
    
print("cmd1 = $cmd1\n");
my($success1, $error_message1, $full_buf1, $stdout_buf1, $stderr_buf1)= IPC::Cmd::run(command => $cmd1, verbose => 0);
##
## This is where we fail! 
print("full_buf1 = @$full_buf1\n");
print("stdout_buf1 = @$stdout_buf1\n");
print("stderr_buf1 = @$stderr_buf1\n");

if(!(contains(@$stdout_buf1[0], "CREATE TABLE")))
{
    exit(1);
}
print ("-"x50,"\n"); 
    
#Adding Table to the Repset 

#if($ENV{EDGE_SETNAME} eq "")

my $cmd2 = qq($ENV{EDGE_CLUSTER_DIR}/n1/pgedge/$ENV{EDGE_CLI} spock repset-add-table default employee $ENV{EDGE_DB} --columns emp_id,emp_first_name,emp_last_name,emp_address,emp_city_state,emp_country,emp_division,emp_date_added );
print("cmd2 = $cmd2\n");
my($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);
print("stdout_buf2 = @$stdout_buf2\n");

if(!(contains(@$stdout_buf2[0], "Adding table")))
{
    exit(1);
}     
    else 
{
    print ("Table employee is already added to default\n");   
}
print ("-"x50,"\n"); 
   
my $cmd3 = qq($homedir2/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p$myport2 -d $ENV{EDGE_DB} -c "CREATE TABLE IF NOT EXISTS public.employee (
emp_id smallint Primary Key,
emp_govt_id varchar(15),
emp_first_name varchar(40),
emp_last_name varchar(40),
emp_address varchar(50),
emp_city_state varchar(15),
emp_country varchar(2),
emp_birth_date date,
emp_division varchar(7),
emp_date_added date);");
    
print("cmd3 = $cmd3\n");
    
my($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);

print("full_buf3 = @$full_buf3\n");
print("stdout_buf3 = @$stdout_buf3\n");
print("stderr_buf3 = @$stderr_buf3\n");
    
if(!(contains(@$stdout_buf3[0], "CREATE TABLE")))
{
    exit(1);
}
print ("-"x50,"\n");    
    
#Adding table to repset on n2
my $cmd4 = qq($ENV{EDGE_CLUSTER_DIR}/n2/pgedge/$ENV{EDGE_CLI} spock repset-add-table default employee $ENV{EDGE_DB});    
print("cmd4 = $cmd4\n");
my($success4, $error_message4, $full_buf4, $stdout_buf4, $stderr_buf4)= IPC::Cmd::run(command => $cmd4, verbose => 0);
print("stdout_buf4 = @$stdout_buf4\n");
      
if(!(contains(@$stdout_buf4[0], "Adding table")))
{
    exit(1);
}   
else 
{
    print ("Table employee is already added to default\n");
}
print ("-"x50,"\n");

# Inserting into public.$ENV{EDGE_TABLE} table

my $cmd5 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "INSERT INTO public.employee VALUES ('8', '738963773', 'Alice', 'Adams', '18 Austin Blvd', 'Austin, TX', 'US', '1983-01-06', 'mgmt', '2021-04-15'),
('20', '08031375B89', 'Benson', 'Brown', 'Rosensweig 58', 'Berlin', 'DE', '1975-03-13', 'sales', '2023-02-18'),
('30', '839467228377', 'Charles', 'Clark', '4, Amrita Rd', 'Delhi', 'IN', '1963-07-18', 'sales', '2022-05-22'),
('40', '560389338', 'Douglas', 'Davis', '3758 Hampton Street', 'Seattle, WA', 'US', '1973-08-09', 'sales', '2020-08-12'),
('50', '0809246719', 'Elaine', 'Evans', 'Hauptstrasse 9375', 'Frankfurt', 'DE', '1967-09-24', 'mgmt', '2021-09-13'),
('60', '294667291937', 'Frederick', 'Ford', 'Flat 80, Triveni Apartments', 'Pune', 'IN', '1971-02-21', 'sales', '2021-03-11'),
('70', '833029112', 'Geoffrey', 'Graham', '84667 Blake Blvd', 'New York, NY', 'US', '1982-01-14', 'mgmt', '2022-08-19'),
('80', '06030764H21', 'Helen', 'Harris', 'Dresden 3-9883', 'Munich', 'DE', '1964-03-07', 'sales', '2022-12-12'),
('90', '8874 7793 8299', 'Isaac', 'Ingram', '4758 Miller Lane', 'Wan Chai', 'HK', '1968-04-19', 'sales', '2020-06-01');");

#print("cmd5 = $cmd5\n");
my($success5, $error_message5, $full_buf5, $stdout_buf5, $stderr_buf5)= IPC::Cmd::run(command => $cmd5, verbose => 0);
print("stdout_buf5 = @$stdout_buf5\n");

if(!(contains(@$stdout_buf5[0], "INSERT")))
{
    exit(1);
}   
else 
{   
    print ("The INSERT statement succeeded (cmd5)\n");
}
print("="x50,"\n");

# Then, use the info to connect to psql and test for inserted data.

my $cmd6 = qq($ENV{EDGE_CLUSTER_DIR}/n1/pgedge/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "SELECT * FROM employee");
#print("cmd6 = $cmd6\n");
print("inserted Records in n1\n");
my($success6, $error_message6, $full_buf6, $stdout_buf6, $stderr_buf6)= IPC::Cmd::run(command => $cmd6, verbose => 0);
print("stdout_buf6 = @$stdout_buf6\n");
print("-"x50,"\n");

#check inserted data on n2
my $cmd7 = qq($ENV{EDGE_CLUSTER_DIR}/n2/pgedge/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p$myport2  -d $ENV{EDGE_DB} -c "SELECT * FROM employee");
#print("cmd7 = $cmd7\n");
print("Replicated Records in n2\n");
my($success7, $error_message7, $full_buf7, $stdout_buf7, $stderr_buf7)= IPC::Cmd::run(command => $cmd7, verbose => 0);
print("stdout_buf7 = @$stdout_buf7\n");
print("-"x50,"\n");

#DROP TABLE in n1

my $cmd8 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "DROP TABLE employee cascade;");
print("cmd8 = $cmd8\n");    
my($success8, $error_message8, $full_buf8, $stdout_buf8, $stderr_buf8)= IPC::Cmd::run(command => $cmd8, verbose => 0);
print("stdout_buf8 = @$stdout_buf8\n");
    
if(!(contains(@$stdout_buf8[0], "DROP TABLE")))
{
    exit(1);
}
print("-"x50,"\n");

#DROP TABLE in n2

my $cmd9 = qq($homedir2/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p$myport2 -d $ENV{EDGE_DB} -c "DROP TABLE employee cascade;");
print("cmd9 = $cmd9\n");
my($success9, $error_message9, $full_buf9, $stdout_buf9, $stderr_buf9)= IPC::Cmd::run(command => $cmd9, verbose => 0);
print("stdout_buf9 = @$stdout_buf9\n");

if(!(contains(@$stdout_buf9[0], "DROP TABLE")))
{
    exit(1);
}

## Needle and Haystack 

if(contains(@$stdout_buf7[0], "8 |             | Alice          | Adams         | 18 Austin Blvd"))
{
    exit(0);
}
else
{
    exit(1);
}



