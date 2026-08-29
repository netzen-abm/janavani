/**
 * Provider-neutral document capability.
 * Deterministic rendering is the baseline; AI-assisted drafting can be a
 * future provider behind the same boundary and must receive sanitized context.
 */
export const DOCUMENT_SCHEMA_VERSION = 1;

export class DocumentProvider {
  async generate(_input) { throw new Error("DocumentProvider.generate is not implemented"); }
}

export function createDocumentDraft({ caseRecord, authority, evidence = [], template = "civic-complaint-v1" }) {
  if (!caseRecord?.id) throw new Error("Case is required");
  if (authority?.state !== "verified" && authority?.state !== "selected") throw new Error("A verified or selected authority is required");
  return {
    schema_version: DOCUMENT_SCHEMA_VERSION,
    id: crypto.randomUUID(),
    case_id: caseRecord.id,
    template,
    status: "draft",
    authority: {
      id: authority.id,
      name: authority.name,
      jurisdiction: authority.jurisdiction,
      authority_type: authority.authority_type,
      source: authority.source,
      source_url: authority.source_url,
    },
    subject: String(caseRecord.issue ?? caseRecord.title ?? "Civic request").slice(0, 300),
    body: String(caseRecord.description ?? caseRecord.issue ?? "").slice(0, 10000),
    evidence_refs: evidence.map((item) => ({ id: item.id, type: item.type, content_hash: item.content_hash ?? null })),
    created_at: new Date().toISOString(),
    requires_citizen_review: true,
    submission_status: "not_submitted",
  };
}

export function updateDocumentDraft(draft, patch) {
  if (!draft?.id || draft.status !== "draft") throw new Error("Only editable drafts can be updated");
  return { ...draft, ...patch, id: draft.id, case_id: draft.case_id, status: "draft", updated_at: new Date().toISOString() };
}

export function approveDocument(draft) {
  if (!draft?.id || draft.status !== "draft") throw new Error("Only a draft can be approved");
  return { ...draft, status: "approved", approved_at: new Date().toISOString(), submission_status: "ready" };
}
