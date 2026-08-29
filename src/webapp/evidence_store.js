import { IndexedDbLocalVault } from "./local_vault.js";
import { assertEvidenceIsLocal, createEvidence } from "./evidence.js";

const EVIDENCE_PREFIX = "evidence:";

/** Shared local provider for the Evidence capability. */
export class LocalEvidenceStore {
  constructor(vault) {
    if (!(vault instanceof IndexedDbLocalVault)) {
      throw new Error("IndexedDbLocalVault is required");
    }
    this.vault = vault;
  }

  async add(input) {
    const evidence = assertEvidenceIsLocal(createEvidence(input));
    await this.vault.put(`${EVIDENCE_PREFIX}${evidence.id}`, evidence);
    return evidence;
  }

  async get(id) {
    return this.vault.get(`${EVIDENCE_PREFIX}${id}`);
  }

  async listForCase(caseId) {
    const all = await this.vault.list();
    return all.filter((item) => item.case_id === caseId);
  }

  async remove(id) {
    await this.vault.remove(`${EVIDENCE_PREFIX}${id}`);
  }
}
