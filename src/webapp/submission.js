/**
 * Provider-neutral submission capability.
 * Submission is impossible until the citizen explicitly approves the draft.
 * Providers receive only the caller-approved minimal payload.
 */
export const SUBMISSION_SCHEMA_VERSION = 1;

export class SubmissionProvider {
  async submit(_payload) { throw new Error("SubmissionProvider.submit is not implemented"); }
}

export function buildSubmissionPayload(draft, { includeEvidence = true } = {}) {
  if (!draft?.id || draft.status !== "approved" || draft.submission_status !== "ready") {
    throw new Error("Only an explicitly approved, ready document can be submitted");
  }
  return {
    schema_version: SUBMISSION_SCHEMA_VERSION,
    submission_id: crypto.randomUUID(),
    document_id: draft.id,
    case_id: draft.case_id,
    authority: {
      id: draft.authority.id,
      name: draft.authority.name,
      jurisdiction: draft.authority.jurisdiction,
      authority_type: draft.authority.authority_type,
    },
    subject: draft.subject,
    body: draft.body,
    evidence_refs: includeEvidence ? draft.evidence_refs : [],
    approved_at: draft.approved_at,
  };
}

export async function submitDocument(provider, draft, options = {}) {
  if (!provider || typeof provider.submit !== "function") throw new Error("Invalid SubmissionProvider");
  const payload = buildSubmissionPayload(draft, options);
  const receipt = await provider.submit(payload);
  if (!receipt?.receipt_id) throw new Error("Submission provider must return a receipt_id");
  return { ...receipt, submission_id: payload.submission_id, document_id: draft.id, case_id: draft.case_id };
}
