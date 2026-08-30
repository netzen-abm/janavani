import { IndexedDbLocalVault } from "./local_vault.js";
import { assertEvidenceIsLocal, createEvidence } from "./evidence.js";

const EVIDENCE_NAMESPACE = "evidence";

/**
 * Shared local provider for the Evidence capability.
 * Binary evidence is never written to a remote repository by this store.
 */
export class LocalEvidenceStore {
  constructor(vault, provenanceStore = null) {
    if (!(vault instanceof IndexedDbLocalVault)) {
      throw new Error("IndexedDbLocalVault is required");
    }
    this.vault = vault;
    this.provenanceStore = provenanceStore;
  }

  async add(input) {
    const evidence = assertEvidenceIsLocal(createEvidence(input));
    await this.vault.put(EVIDENCE_NAMESPACE, evidence.id, evidence);
    if (this.provenanceStore) {
      await this.provenanceStore.append({
        artifact_id: evidence.id,
        event: "created",
        details: {
          content_hash: evidence.content_hash,
        },
      });
      if (evidence.captured_at) {
        await this.provenanceStore.append({
          artifact_id: evidence.id,
          event: "captured",
          occurred_at: evidence.captured_at,
        });
      }
    }
    return evidence;
  }

  async get(id) {
    return this.vault.get(EVIDENCE_NAMESPACE, id);
  }

  async listForCase(caseId) {
    const all = await this.vault.list(EVIDENCE_NAMESPACE);
    return all.filter((item) => item.case_id === caseId);
  }

  async remove(id) {
    const evidence = await this.get(id);
    await this.vault.remove(EVIDENCE_NAMESPACE, id);
    if (this.provenanceStore && evidence) {
      await this.provenanceStore.append({
        artifact_id: id,
        event: "deleted",
      });
    }
  }
}
