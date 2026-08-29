/**
 * Provider-neutral local tracking for civic submissions.
 * Stores operational status and receipt metadata, never submission content.
 */
export const TRACKING_SCHEMA_VERSION = 1;
export const TRACKING_STATES = Object.freeze({ PENDING: "pending", SUBMITTED: "submitted", ACKNOWLEDGED: "acknowledged", IN_PROGRESS: "in_progress", RESOLVED: "resolved", REJECTED: "rejected", UNKNOWN: "unknown" });

export class TrackingProvider {
  async getStatus(_receipt) { throw new Error("TrackingProvider.getStatus is not implemented"); }
}

export function createTrackingRecord({ receipt_id, submission_id, case_id, status = TRACKING_STATES.SUBMITTED, provider = null, external_reference = null }) {
  if (!receipt_id || !submission_id || !case_id) throw new Error("Receipt, submission, and case identifiers are required");
  return {
    schema_version: TRACKING_SCHEMA_VERSION,
    id: crypto.randomUUID(),
    receipt_id,
    submission_id,
    case_id,
    status,
    provider,
    external_reference,
    updated_at: new Date().toISOString(),
  };
}

export function applyTrackingUpdate(record, update) {
  if (!record?.id) throw new Error("Tracking record is required");
  if (!Object.values(TRACKING_STATES).includes(update?.status)) throw new Error("Unsupported tracking status");
  return { ...record, status: update.status, external_reference: update.external_reference ?? record.external_reference, updated_at: update.updated_at ?? new Date().toISOString() };
}

export class LocalTrackingStore {
  constructor(vault) { this.vault = vault; }
  async save(record) { await this.vault.put("tracking", record.id, record); return record; }
  async getByCase(caseId) { return (await this.vault.list("tracking")).filter((item) => item.case_id === caseId); }
}
