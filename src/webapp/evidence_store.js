import { IndexedDbLocalVault } from "./local_vault.js";
import { assertEvidenceIsLocal, createEvidence } from "./evidence.js";

const EVIDENCE_NAMESPACE = "evidence";

/** Shared local provider for the Evidence capability. Raw evidence bytes stay on-device. */
export class LocalEvidenceStore {
  constructor(vault, provenanceStore = null) {
    if (!(vault instanceof IndexedDbLocalVault)) throw new Error("IndexedDbLocalVault is required");
    this.vault = vault;
    this.provenanceStore = provenanceStore;
  }

  async add(input) {
    const evidence = assertEvidenceIsLocal(createEvidence(input));
    await this.vault.put(EVIDENCE_NAMESPACE, evidence.id, evidence);
    await this.#record(evidence.id, "created", { content_hash: evidence.content_hash });
    if (evidence.captured_at) await this.#record(evidence.id, "captured", {}, evidence.captured_at);
    return evidence;
  }

  async get(id) { return this.vault.get(EVIDENCE_NAMESPACE, id); }

  async listForCase(caseId) {
    return (await this.vault.list(EVIDENCE_NAMESPACE)).filter((item) => item.case_id === caseId);
  }

  async remove(id) {
    const evidence = await this.get(id);
    await this.vault.remove(EVIDENCE_NAMESPACE, id);
    if (evidence) await this.#record(id, "deleted");
  }

  async #record(artifactId, event, details = {}, occurred_at) {
    if (!this.provenanceStore) return;
    await this.provenanceStore.append({ artifact_id: artifactId, event, details, occurred_at });
  }
}
