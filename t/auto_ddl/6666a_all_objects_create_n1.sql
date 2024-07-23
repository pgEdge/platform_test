-- Create spocktab prepared statement
PREPARE spocktab AS SELECT nspname, relname, set_name FROM spock.tables WHERE relname LIKE $1 ORDER BY relid;

-- Create schema
CREATE SCHEMA s1;
SET search_path TO s1;

-- Create database
CREATE DATABASE obj_database;

-- Create extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create foreign data wrapper
CREATE FOREIGN DATA WRAPPER obj_fdw;

-- Create server
CREATE SERVER obj_server FOREIGN DATA WRAPPER obj_fdw;

-- Create user mapping
CREATE USER MAPPING FOR CURRENT_USER SERVER obj_server;

-- Create tablespace
SET allow_in_place_tablespaces = true; -- allows to create a tablespace without a path
CREATE TABLESPACE obj_tablespace LOCATION '';

-- Create role
CREATE ROLE obj_role;

-- Create publication
CREATE PUBLICATION obj_publication FOR TABLES IN SCHEMA s1;

-- Create subscription
CREATE SUBSCRIPTION obj_subscription CONNECTION '' PUBLICATION obj_publication WITH (connect = false, slot_name = NONE);


CREATE TYPE obj_type AS (x INT, y INT);
CREATE DOMAIN obj_domain AS INT;
-- Create cast
CREATE FUNCTION obj_function_cast(obj_type) RETURNS INT LANGUAGE plpgsql AS $$
BEGIN
    RETURN $1.x + $1.y;
END $$;
-- Create the cast from obj_type1 to int
CREATE CAST (obj_type AS int) WITH FUNCTION obj_function_cast(obj_type) AS IMPLICIT;

-- Create aggregate
CREATE FUNCTION int4_sum(state int4, value int4) RETURNS int4 LANGUAGE internal IMMUTABLE STRICT AS 'int4pl';

-- Create aggregate
CREATE AGGREGATE obj_aggregate (
    sfunc = int4_sum,
    stype = int4,
    basetype = int4,
    initcond = '0'
);


-- Create collation
CREATE COLLATION obj_collation (lc_collate = 'C', lc_ctype = 'C');

-- Create conversion
CREATE CONVERSION obj_conversion FOR 'LATIN1' TO 'UTF8' FROM iso8859_1_to_utf8;


-- Create domain
CREATE DOMAIN obj_domain2 AS INT CHECK (VALUE >= 0);

-- Create foreign table
CREATE FOREIGN TABLE obj_foreign_table (
    id INT,
    name TEXT
) SERVER obj_server;

-- Create function
CREATE FUNCTION obj_function() RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    RETURN NEW;
END $$;

-- Create index
CREATE TABLE obj_table (id INT PRIMARY KEY, name TEXT);
CREATE INDEX obj_index ON obj_table (name);

-- Create language
CREATE LANGUAGE plperl;

-- Create materialized view
CREATE MATERIALIZED VIEW obj_mview AS SELECT * FROM obj_table WITH NO DATA;

-- Create operator
CREATE OPERATOR ## (
   leftarg = path,
   rightarg = path,
   function = path_inter,
   commutator = ##
);

-- Create operator family
CREATE OPERATOR FAMILY obj_opfamily USING btree;

-- Create operator class
CREATE OPERATOR CLASS obj_opclass FOR TYPE int4 USING btree FAMILY obj_opfamily AS
    OPERATOR 1 < ,
    OPERATOR 2 <= ,
    OPERATOR 3 = ,
    OPERATOR 4 >= ,
    OPERATOR 5 > ,
    FUNCTION 1 btint4cmp(int4, int4);

-- Create policy
CREATE POLICY obj_policy ON obj_table FOR SELECT TO PUBLIC USING (true);

-- Create procedure
CREATE PROCEDURE obj_procedure() LANGUAGE plpgsql AS $$
BEGIN
    RAISE NOTICE 'Procedure executed';
END $$;

-- Create rule
CREATE RULE obj_rule AS ON INSERT TO obj_table DO ALSO NOTHING;

-- Create text search dictionary
CREATE TEXT SEARCH DICTIONARY obj_tsdict (
    TEMPLATE = simple
);

-- Create text search parser
CREATE TEXT SEARCH PARSER obj_tsparser (
    START = prsd_start,
    GETTOKEN = prsd_nexttoken,
    END = prsd_end,
    LEXTYPES = prsd_lextype
);

-- Create text search configuration
CREATE TEXT SEARCH CONFIGURATION obj_tsconfig (PARSER = obj_tsparser);

-- Create text search template
CREATE TEXT SEARCH TEMPLATE obj_tstemplate (
    INIT = dsimple_init,
    LEXIZE = dsimple_lexize
);

-- Create transform
CREATE TRANSFORM FOR int LANGUAGE SQL (
    FROM SQL WITH FUNCTION prsd_lextype(internal),
    TO SQL WITH FUNCTION int4recv(internal));

-- Create trigger
CREATE TRIGGER obj_trigger AFTER INSERT ON obj_table FOR EACH ROW EXECUTE FUNCTION obj_function();

-- Create type
CREATE TYPE obj_composite_type AS (x INT, y INT);
CREATE TYPE obj_enum AS ENUM ('red', 'green', 'blue');
CREATE TYPE obj_range AS RANGE (subtype = int4range);

-- Create view
CREATE VIEW obj_view AS SELECT * FROM obj_table;

-- Create group
CREATE GROUP obj_group;

-- Create event trigger
CREATE FUNCTION obj_function_event_trigger() RETURNS event_trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE NOTICE 'Event trigger activated: %', tg_tag;
END $$;
CREATE EVENT TRIGGER obj_event_trigger ON ddl_command_start EXECUTE FUNCTION obj_function_event_trigger();


-- Meta command validations
-- Validate database
\l obj_database

-- Validate extension
\dx "uuid-ossp"

-- Validate tablespace
SELECT count(*) FROM pg_tablespace WHERE spcname = 'obj_tablespace';

-- Validate role
\dg obj_role

-- Validate schema
\dn s1

-- Validate foreign data wrapper
\dew obj_fdw

-- Validate server
\des obj_server

-- Validate user mapping
\deu

-- Validate publication
\dRp obj_publication

-- Validate subscription
\dRs obj_subscription

-- Validate cast
\dC obj_type

-- Validate aggregate
\da obj_aggregate

-- Validate collation
\dO obj_collation

-- Validate conversion
\dc obj_conversion

-- Validate domain
\dD obj_domain2

-- Validate event trigger
\dy obj_event_trigger

-- Validate foreign table
\det obj_foreign_table

-- Validate function
\df obj_function

-- Validate index
\di obj_index

-- Validate language
\dL plperl

-- Validate materialized view
\d+ obj_mview

-- Validate operator
\do s1.##

-- Validate operator class
\dAc btree integer

-- Validate operator family
SELECT count(*) FROM pg_opfamily WHERE opfname = 'obj_opfamily';

-- Validate procedure
\df obj_procedure

-- Validate text search configuration
\dF obj_tsconfig

-- Validate text search dictionary
\dFd obj_tsdict

-- Validate text search parser
\dFp obj_tsparser

-- Validate text search template
\dFt obj_tstemplate

-- Validate transform
SELECT  l.lanname, ty.typname
FROM pg_transform t
JOIN pg_language l ON t.trflang = l.oid
JOIN pg_type ty ON t.trftype = ty.oid
WHERE ty.typname = 'int4' AND l.lanname = 'sql';

-- Validate type
\dT+ obj_composite_type
\dT+ obj_enum
\dT+ obj_range

-- Validate view
\d+ obj_view

--validate table, triggers, rules
\d+ obj_table

-- Validate group
\dg obj_group
