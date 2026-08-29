/**
 * Channel-neutral Evidence capability.
 * Evidence is metadata + a device-local reference; binary content remains local
 * until an explicit, policy-approved submission path is selected.
 */

export const EVIDENCE_SCHEMA_VERSION = 1;

const ALLOWED_TYPES = new Set(["photo", "video", "document", "audio", "link", "note"]);

export function createEvidence(input) {
  if (!input || typeof input !== "object") throw new Error("Evidence input is required");
  if (!ALLOWED_TYPES.has(input.type)) throw new Error("Unsupported evidence type");
  if (!input.case_id) throw new Error("Case id is required");
  if (!input.id) throw new Error("Evidence id is required");

  return {
    schema_version: EVIDENCE_SCHEMA_VERSION,
    id: input.id,
    case_id: input.case_id,
    type: input.type,
    label: input.label ? String(input.label).slice(0, 200) : null,
    local_ref: input.local_ref ? String(input.local_ref) : null,
    source_url: input.type === "link" && input.source_url ? String(input.source_url) : null,
    captured_at: input.captured_at ?? new Date().toISOString(),
    content_hash: input.content_hash ?? null,
    notes: input.notes ? String(input.notes).slice(0, 2000) : null,
    status: "local",
  };
}

export function assertEvidenceIsLocal(evidence) {
  if (evidence?.status !== "local") {
    throw new Error("Evidence must remain local until an explicit submission policy is approved");
  }
  return evidence;
}
