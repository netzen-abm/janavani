-- Citizen-owned, content-free reusable document structures.
-- Apply only to the intended preview/staging database after review. Never auto-run at app startup.
-- The deployment owner must grant least-privilege table access to the dedicated runtime DB role.
-- The runtime role must not be a superuser, table owner with RLS bypass, or have BYPASSRLS.
BEGIN;

CREATE TABLE IF NOT EXISTS public.citizen_document_formats (
    format_id text PRIMARY KEY,
    owner_principal_id text NOT NULL,
    template_id text NOT NULL,
    template_version integer NOT NULL CHECK (template_version > 0),
    section_field_names text[] NOT NULL CHECK (cardinality(section_field_names) > 0),
    structure_hash char(64) NOT NULL CHECK (structure_hash ~ '^[0-9a-f]{64}$'),
    created_at timestamptz NOT NULL,
    updated_at timestamptz NOT NULL,
    CONSTRAINT citizen_document_formats_owner_structure_unique
        UNIQUE (owner_principal_id, structure_hash)
);

CREATE INDEX IF NOT EXISTS citizen_document_formats_owner_created_idx
    ON public.citizen_document_formats (owner_principal_id, created_at, format_id);

ALTER TABLE public.citizen_document_formats ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.citizen_document_formats FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS citizen_document_formats_owner_select ON public.citizen_document_formats;
CREATE POLICY citizen_document_formats_owner_select
ON public.citizen_document_formats FOR SELECT
USING (owner_principal_id = NULLIF(current_setting('janavani.principal_id', true), ''));

DROP POLICY IF EXISTS citizen_document_formats_owner_insert ON public.citizen_document_formats;
CREATE POLICY citizen_document_formats_owner_insert
ON public.citizen_document_formats FOR INSERT
WITH CHECK (owner_principal_id = NULLIF(current_setting('janavani.principal_id', true), ''));

DROP POLICY IF EXISTS citizen_document_formats_owner_update ON public.citizen_document_formats;
CREATE POLICY citizen_document_formats_owner_update
ON public.citizen_document_formats FOR UPDATE
USING (owner_principal_id = NULLIF(current_setting('janavani.principal_id', true), ''))
WITH CHECK (owner_principal_id = NULLIF(current_setting('janavani.principal_id', true), ''));

DROP POLICY IF EXISTS citizen_document_formats_owner_delete ON public.citizen_document_formats;
CREATE POLICY citizen_document_formats_owner_delete
ON public.citizen_document_formats FOR DELETE
USING (owner_principal_id = NULLIF(current_setting('janavani.principal_id', true), ''));

COMMENT ON TABLE public.citizen_document_formats IS
    'Owner-scoped reusable structural identifiers only; never stores source prose, personal values, evidence, or completed documents.';

COMMIT;
