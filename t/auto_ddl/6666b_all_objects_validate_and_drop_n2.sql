SELECT pg_sleep(2);--to ensure all objects are replicated

---- Validate all objects on n2 and then drop them on n2 that should also drop objects on n1
-- Validate database, should not exist
\l obj_database

-- Validate extension
\dx "uuid-ossp"

SET search_path TO s1, public;
-- Validate tablespace, should be 0
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

-- Validate subscription, should not exist
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

-- Validate operator class, should list 2
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

-- Drop statements
DROP EVENT TRIGGER obj_event_trigger;
--Database wasn't auto replicated to n2, nothing to drop
DROP DATABASE obj_database;
--Tablespace wasn't auto replicated to n2, nothing to drop
DROP TABLESPACE obj_tablespace;
DROP ROLE obj_role;
DROP EXTENSION "uuid-ossp";
DROP FOREIGN DATA WRAPPER obj_fdw CASCADE;
DROP PUBLICATION obj_publication;
DROP AGGREGATE obj_aggregate (int);
DROP COLLATION obj_collation;
DROP CONVERSION obj_conversion;
DROP DOMAIN obj_domain2;
DROP INDEX obj_index;
DROP EXTENSION plperl;
DROP MATERIALIZED VIEW obj_mview;
DROP OPERATOR ##(path,path);
DROP OPERATOR CLASS obj_opclass USING btree;
DROP OPERATOR FAMILY obj_opfamily USING btree;
DROP POLICY obj_policy ON obj_table;
DROP PROCEDURE obj_procedure;
DROP RULE obj_rule ON obj_table;
DROP TEXT SEARCH CONFIGURATION obj_tsconfig;
DROP TEXT SEARCH DICTIONARY obj_tsdict;
DROP TEXT SEARCH PARSER obj_tsparser;
DROP TEXT SEARCH TEMPLATE obj_tstemplate;
DROP TRANSFORM FOR int LANGUAGE SQL;
DROP TRIGGER obj_trigger ON obj_table;
DROP TYPE obj_composite_type;
DROP TYPE obj_enum;
DROP TYPE obj_range;
DROP VIEW obj_view;
DROP FUNCTION obj_function CASCADE;
DROP FUNCTION obj_function_event_trigger CASCADE;
DROP FUNCTION obj_function_cast(obj_type) CASCADE;
DROP TABLE obj_table CASCADE;
DROP GROUP obj_group;
DROP SCHEMA s1 CASCADE;