/**
 * Orchestrates capabilities without owning their storage or provider logic.
 * The UI can call these transitions and render the returned state.
 */
export const WORKFLOW_STATES = Object.freeze({
  CASE: "case",
  EVIDENCE: "evidence",
  AUTHORITY: "authority",
  DOCUMENT: "document",
  REVIEW: "review",
  APPROVED: "approved",
  SUBMITTED: "submitted",
  TRACKING: "tracking",
});

export function createWorkflowState(caseRecord) {
  if (!caseRecord?.id) throw new Error("Case is required");
  return { version: 1, case_id: caseRecord.id, state: WORKFLOW_STATES.CASE, authority: null, document: null, receipt: null, tracking: null };
}

export function attachEvidence(state, evidence) {
  if (!state?.case_id) throw new Error("Workflow state is required");
  return { ...state, state: WORKFLOW_STATES.EVIDENCE, evidence: [...(state.evidence ?? []), { id: evidence.id, type: evidence.type, content_hash: evidence.content_hash ?? null }] };
}

export function chooseAuthority(state, authority) {
  if (authority?.state !== "selected") throw new Error("Selected authority is required");
  return { ...state, state: WORKFLOW_STATES.AUTHORITY, authority: { id: authority.id, name: authority.name, jurisdiction: authority.jurisdiction, authority_type: authority.authority_type } };
}

export function attachDocument(state, document) {
  if (document?.case_id !== state.case_id) throw new Error("Document does not belong to this Case");
  return { ...state, state: WORKFLOW_STATES.REVIEW, document: { id: document.id, status: document.status, submission_status: document.submission_status } };
}

export function approveWorkflow(state) {
  if (state?.state !== WORKFLOW_STATES.REVIEW || state.document?.status !== "approved") throw new Error("Approved document is required");
  return { ...state, state: WORKFLOW_STATES.APPROVED };
}

export function attachReceipt(state, receipt) {
  if (state?.state !== WORKFLOW_STATES.APPROVED) throw new Error("Workflow must be approved before submission");
  if (!receipt?.receipt_id) throw new Error("Submission receipt is required");
  return { ...state, state: WORKFLOW_STATES.SUBMITTED, receipt: { receipt_id: receipt.receipt_id, submission_id: receipt.submission_id ?? null } };
}

export function attachTracking(state, tracking) {
  if (state?.state !== WORKFLOW_STATES.SUBMITTED) throw new Error("Submission receipt is required before tracking");
  return { ...state, state: WORKFLOW_STATES.TRACKING, tracking: { id: tracking.id, status: tracking.status, external_reference: tracking.external_reference ?? null } };
}
