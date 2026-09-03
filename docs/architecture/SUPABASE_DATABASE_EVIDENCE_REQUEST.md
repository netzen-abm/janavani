# Janavani — Supabase Database Evidence Request

**Status:** REQUIRED VERIFICATION INPUT  
**Purpose:** Establish the actual PostgreSQL/Supabase database state before production migration, RLS, or durable Civic Case activation.  
**Safety:** All queries below are read-only metadata queries. They do not create, modify, or delete database data.

## Why this is required

GitHub currently contains the canonical Civic Case schema, migration draft, transaction contract, and RLS authorization contract, but the repository does not contain a verified `supabase/migrations` history or proof of the deployed database schema.

The production implementation must therefore be reconciled against the real database rather than inferred from documentation.

## Execute in Supabase SQL Editor

Run each query separately and export/copy the complete result.

### 1. Tables and views

```sql
select
    table_schema,
    table_name,
    table_type
from information_schema.tables
where table_schema not in ('pg_catalog', 'information_schema')
order by table_schema, table_name;
```

### 2. Columns

```sql
select
    table_schema,
    table_name,
    ordinal_position,
    column_name,
    data_type,
    udt_name,
    is_nullable,
    column_default
from information_schema.columns
where table_schema = 'public'
order by table_name, ordinal_position;
```

### 3. Constraints

```sql
select
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type,
    kcu.column_name,
    ccu.table_name as referenced_table,
    ccu.column_name as referenced_column
from information_schema.table_constraints tc
left join information_schema.key_column_usage kcu
    on tc.constraint_name = kcu.constraint_name
    and tc.table_schema = kcu.table_schema
left join information_schema.constraint_column_usage ccu
    on tc.constraint_name = ccu.constraint_name
    and tc.table_schema = ccu.table_schema
where tc.table_schema = 'public'
order by tc.table_name, tc.constraint_name, kcu.ordinal_position;
```

### 4. Indexes

```sql
select
    schemaname,
    tablename,
    indexname,
    indexdef
from pg_indexes
where schemaname = 'public'
order by tablename, indexname;
```

### 5. RLS enabled state

```sql
select
    n.nspname as schema_name,
    c.relname as table_name,
    c.relrowsecurity as rls_enabled,
    c.relforcerowsecurity as rls_forced
from pg_class c
join pg_namespace n
    on n.oid = c.relnamespace
where n.nspname = 'public'
  and c.relkind = 'r'
order by c.relname;
```

### 6. RLS policies

```sql
select
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
from pg_policies
where schemaname = 'public'
order by tablename, policyname;
```

### 7. Functions and RPCs

```sql
select
    n.nspname as schema_name,
    p.proname as function_name,
    pg_get_function_identity_arguments(p.oid)
        as arguments,
    pg_get_function_result(p.oid) as return_type
from pg_proc p
join pg_namespace n
    on n.oid = p.pronamespace
where n.nspname = 'public'
order by p.proname, arguments;
```

### 8. Triggers

```sql
select
    event_object_schema,
    event_object_table,
    trigger_name,
    event_manipulation,
    action_statement
from information_schema.triggers
where event_object_schema = 'public'
order by event_object_table, trigger_name;
```

### 9. Supabase migration history, if available

If the project exposes the migration history table, run:

```sql
select *
from supabase_migrations.schema_migrations
order by version;
```

If this relation does not exist or is not accessible, report that fact. Do not create it merely to satisfy this query.

## Evidence handling

Do **not** provide:

- `SUPABASE_ANON_KEY`;
- service-role keys;
- database passwords;
- access tokens;
- private connection strings;
- secrets from environment variables.

The metadata query results are sufficient for schema reconciliation.

## What will happen after evidence is supplied

The results will be reconciled against:

1. `src/core/civic_case.py`;
2. `docs/DATA_CONTRACTS.md`;
3. `docs/architecture/CANONICAL_CASE_POSTGRES_SCHEMA.md`;
4. `docs/architecture/CANONICAL_CASE_RLS_AUTHORIZATION_MATRIX.md`;
5. `docs/architecture/CANONICAL_CASE_TRANSACTION_CONTRACT.md`;
6. `src/storage/repositories/supabase_civic_case.py`;
7. the review-only PostgreSQL migration draft.

The reconciliation will classify every relevant object as:

```text
MATCH
MISMATCH
MISSING
EXTRA / LEGACY
UNKNOWN
```

Only after that classification will we decide whether to:

```text
adopt existing schema
      OR
extend existing schema safely
      OR
create missing canonical objects
```

## Explicit gate

No production migration, RLS policy change, legacy-data migration, or switch from `InMemoryCivicCaseRepository` to the durable provider is authorized until this evidence has been reviewed and the resulting implementation plan has passed the existing verification gates.
