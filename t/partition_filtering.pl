# After creating a two node cluster on the localhost, 
# the test case tells how a partitioned table is used to Filter the replicated content
#
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

my $cmd = qq(source $homedir1/$ENV{EDGE_COMPONENT}/pg16.env);
print("cmd = $cmd\n");
my($success, $error_message, $full_buf, $stdout_buf, $stderr_buf)= IPC::Cmd::run(command => $cmd, verbose => 0);
##
print("full_buf = @$full_buf\n");
print("stdout_buf = @$stdout_buf\n");
print("stderr_buf = @$stderr_buf\n");

# I removed the check for the tables existence (since we can include the IF NOT EXISTS clause in the command):
# Creating public.$ENV{EDGE_TABLE} Table

my $cmd1 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "CREATE TABLE IF NOT EXISTS public.customer (
cust_id integer,
cust_name varchar(40),
cust_contact varchar(40),
cust_address varchar(60),
city varchar(15),
country_code char(2),
sales_contact smallint,
sales_date_added date) PARTITION BY LIST (country_code);");
    
print("cmd1 = $cmd1\n");    
my($success1, $error_message1, $full_buf1, $stdout_buf1, $stderr_buf1)= IPC::Cmd::run(command => $cmd1, verbose => 0);
print("full_buf1 = @$full_buf1\n");
print("stdout_buf1 = @$stdout_buf1\n");
print("stderr_buf1 = @$stderr_buf1\n");
    
if(!(contains(@$stdout_buf1[0], "CREATE TABLE")))
{
    exit(1);
}
print ("-"x50,"\n"); 
   
# Adding constraints to  Table in n1
   
my $cmd2 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "ALTER TABLE public.customer ADD CONSTRAINT primary_constraint PRIMARY KEY (cust_id, country_code)");   
print("cmd2 = $cmd2\n");
my($success2, $error_message2, $full_buf2, $stdout_buf2, $stderr_buf2)= IPC::Cmd::run(command => $cmd2, verbose => 0);
print("stdout_buf2 = @$stdout_buf2\n");
    
if(!(contains(@$stdout_buf2[0], "ALTER TABLE")))
{
    exit(1);
}   
print ("-"x50,"\n"); 
   
#creating partition tables in n1
   
my $cmd3 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "CREATE TABLE IF NOT EXISTS eu_members PARTITION OF public.customer FOR VALUES IN ('BE', 'BG', 'CZ', 'DK', 'DE', 'EE', 'IE', 'EL', 'ES', 'FR', 'HR', 'IT', 'CY', 'LV', 'LT', 'LU', 'HU', 'MT', 'NL', 'AT', 'PL', 'PT', 'RO', 'SI', 'SK', 'FI', 'SE');");
#print("cmd3 = $cmd3\n");
my($success3, $error_message3, $full_buf3, $stdout_buf3, $stderr_buf3)= IPC::Cmd::run(command => $cmd3, verbose => 0);
print("stdout_buf3 = @$stdout_buf3\n");
    
if(!(contains(@$stdout_buf3[0], "CREATE TABLE")))
{
    exit(1);
}
   
my $cmd4 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c " 
CREATE TABLE non_eu_members PARTITION OF public.customer DEFAULT;;");
#print("cmd4 = $cmd4\n");
my($success4, $error_message4, $full_buf4, $stdout_buf4, $stderr_buf4)= IPC::Cmd::run(command => $cmd4, verbose => 0);
print("stdout_buf4 = @$stdout_buf4\n");
    
if(!(contains(@$stdout_buf4[0], "CREATE TABLE")))
{
    exit(1);
}
print ("-"x50,"\n"); 
   
# Creating public.$ENV{EDGE_TABLE} Table

my $cmd5 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $myport2 -d $ENV{EDGE_DB} -c "CREATE TABLE IF NOT EXISTS public.customer (
cust_id integer,
cust_name varchar(40),
cust_contact varchar(40),
cust_address varchar(60),
city varchar(15),
country_code char(2),
sales_contact smallint,
sales_date_added date) PARTITION BY LIST (country_code);");    
print("cmd5 = $cmd5\n");    
my($success5, $error_message5, $full_buf5, $stdout_buf5, $stderr_buf5)= IPC::Cmd::run(command => $cmd5, verbose => 0);
print("stdout_buf5 = @$stdout_buf5\n");

if(!(contains(@$stdout_buf5[0], "CREATE TABLE")))
{
    exit(1);
}
print ("-"x50,"\n"); 
    
# Adding constraints to  Table in n2

my $cmd6 = qq($homedir2/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $myport2 -d $ENV{EDGE_DB} -c "ALTER TABLE public.customer ADD CONSTRAINT primary_constraint PRIMARY KEY (cust_id, country_code)");
print("cmd6 = $cmd6\n");
my($success6, $error_message6, $full_buf6, $stdout_buf6, $stderr_buf6)= IPC::Cmd::run(command => $cmd6, verbose => 0);
print("stdout_buf6 = @$stdout_buf6\n");
    
if(!(contains(@$stdout_buf6[0], "ALTER TABLE")))
{
    exit(1);
}
print ("-"x50,"\n");  
  
#creating partition tables in n2
my $cmd7 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $myport2 -d $ENV{EDGE_DB} -c "CREATE TABLE IF NOT EXISTS eu_members PARTITION OF public.customer FOR VALUES IN ('BE', 'BG', 'CZ', 'DK', 'DE', 'EE', 'IE', 'EL', 'ES', 'FR', 'HR', 'IT', 'CY', 'LV', 'LT', 'LU', 'HU', 'MT', 'NL', 'AT', 'PL', 'PT', 'RO', 'SI', 'SK', 'FI', 'SE');");
print("cmd7 = $cmd7\n");
my($success7, $error_message7, $full_buf7, $stdout_buf7, $stderr_buf7)= IPC::Cmd::run(command => $cmd7, verbose => 0);
print("stdout_buf7 = @$stdout_buf7\n");
    
if(!(contains(@$stdout_buf7[0], "CREATE TABLE")))
{
    exit(1);
}
   
my $cmd8 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $myport2 -d $ENV{EDGE_DB} -c "CREATE TABLE non_eu_members PARTITION OF public.customer DEFAULT;");
print("cmd8 = $cmd8\n");
my($success8, $error_message8, $full_buf8, $stdout_buf8, $stderr_buf8)= IPC::Cmd::run(command => $cmd8, verbose => 0);
print("stdout_buf8 = @$stdout_buf8\n");
    
if(!(contains(@$stdout_buf8[0], "CREATE TABLE")))
{
    exit(1);
}
print ("-"x50,"\n"); 
  
    
#Adding Table to the Repset in n1

#if($ENV{EDEGE_SETNAME} eq ""){
my $cmd9 = qq($ENV{EDGE_CLUSTER_DIR}/n1/pgedge/$ENV{EDGE_CLI} spock repset-add-table default customer $ENV{EDGE_DB});
print("cmd9 = $cmd9\n");
my($success9, $error_message9, $full_buf9, $stdout_buf9, $stderr_buf9)= IPC::Cmd::run(command => $cmd9, verbose => 0);
print("stdout_buf9 = @$stdout_buf9\n");
     
if(!(contains(@$stdout_buf9[0], "Adding table")))
{
    exit(1);
}

else
{
   print ("Table customer is already added to default\n");   
}
print ("-"x50,"\n"); 
   
#Adding Table to the Repset in n2

#if($ENV{EDEGE_SETNAME} eq ""){
my $cmd10 = qq($ENV{EDGE_CLUSTER_DIR}/n2/pgedge/$ENV{EDGE_CLI} spock repset-add-table default customer $ENV{EDGE_DB});
print("cmd10 = $cmd10\n");
my($success10, $error_message10, $full_buf10, $stdout_buf10, $stderr_buf10)= IPC::Cmd::run(command => $cmd10, verbose => 0);
print("stdout_buf10 = @$stdout_buf10\n");
     
if(!(contains(@$stdout_buf10[0], "Adding table")))
{
    exit(1);  
} 

else
{
    print ("Table customer is already added to default\n");
}
print ("-"x50,"\n"); 

# Remove repset associated with partition table on n1 

my $cmd11 = qq($ENV{EDGE_CLUSTER_DIR}/n1/pgedge/$ENV{EDGE_CLI} spock repset-remove-partition customer $ENV{EDGE_DB} --partition=eu_members);
print("cmd11 = $cmd11\n");
my($success11, $error_message11, $full_buf11, $stdout_buf11, $stderr_buf11)= IPC::Cmd::run(command => $cmd11, verbose => 0);
print("stdout_buf11 = @$stdout_buf11\n");
 
if(!(contains(@$stdout_buf11[0], "repset_remove_partition")))
{
    exit(1);
}
print ("-"x50,"\n");     

# Insert records into n1

my $cmd12 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "INSERT INTO public.customer VALUES ('1027', 'Astro Adventures', 'A. Azimuth', '7667 Ace Avenue', 'Aarhus', 'DK', 20, '2024-03-26'), ('1028', 'Bharat Solutions', 'B. Bharati', '7667 Bajaj', 'Bangalore', 'IN', 30, '2024-04-21')");
#print("cmd12 = $cmd12\n");
my($success12, $error_message12, $full_buf12, $stdout_buf12, $stderr_buf12)= IPC::Cmd::run(command => $cmd12, verbose => 0);
print("stdout_buf12 = @$stdout_buf12\n");
      
if(!(contains(@$stdout_buf12[0], "INSERT")))
{
    exit(1);
}
print("-"x50,"\n");

#check records in n1

my $cmd13 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT}  -d $ENV{EDGE_DB} -c "SELECT * FROM CUSTOMER");
my($success13, $error_message13, $full_buf13, $stdout_buf13, $stderr_buf13)= IPC::Cmd::run(command => $cmd13, verbose => 0);
print("stdout_buf13 = @$stdout_buf13\n");
print("-"x50,"\n");

#check Filtered records in n2

my $cmd14 = qq($homedir2/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $myport2  -d $ENV{EDGE_DB} -c "SELECT * FROM CUSTOMER");
my($success14, $error_message14, $full_buf14, $stdout_buf14, $stderr_buf14)= IPC::Cmd::run(command => $cmd14, verbose => 0);
print("stdout_buf14 = @$stdout_buf14\n");
      
#DROP TABLE in n1

my $cmd15 = qq($homedir1/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p $ENV{EDGE_START_PORT} -d $ENV{EDGE_DB} -c "DROP TABLE customer cascade;");
print("cmd15 = $cmd15\n");
my($success15, $error_message15, $full_buf15, $stdout_buf15, $stderr_buf15)= IPC::Cmd::run(command => $cmd15, verbose => 0);
print("stdout_buf15 = @$stdout_buf15\n");
   
if(!(contains(@$stdout_buf15[0], "DROP TABLE")))
{
    exit(1);
}
print("-"x50,"\n");

#DROP TABLE in n2

my $cmd16 = qq($homedir2/$ENV{EDGE_COMPONENT}/bin/psql -t -h $ENV{EDGE_HOST} -p$myport2 -d $ENV{EDGE_DB} -c "DROP TABLE customer cascade;");
print("cmd16 = $cmd16\n");
my($success16, $error_message16, $full_buf16, $stdout_buf16, $stderr_buf16)= IPC::Cmd::run(command => $cmd16, verbose => 0);
print("stdout_buf16 = @$stdout_buf16\n");
     
if(!(contains(@$stdout_buf16[0], "DROP TABLE")))
{
    exit(1);
}

## Needle and Haystack

if(contains(@$stdout_buf14[0], "1028 | Bharat Solutions | B. Bharati   | 7667 Bajaj   | Bangalore |"))
{
    exit(0);
}
else
{
    exit(1);
}

  



