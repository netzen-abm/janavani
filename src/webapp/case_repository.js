import { IndexedDbLocalVault } from "./local_vault.js";

/**
 * CaseRepository adapter for the browser-local encrypted vault.
 *
 * The adapter persists only through LocalVault. It never falls back to a
 * remote store when browser-local persistence fails.
 */
export class LocalVaultCaseRepository {
  constructor(vault) {
    if (!(vault instanceof IndexedDbLocalVault)) {
      throw new Error("An IndexedDbLocalVault is required");
    }
    this.vault = vault;
  }

  async save(caseRecord) {
    if (!caseRecord?.id) throw new Error("Case id is required");
    await this.vault.put(caseRecord.id, caseRecord);
    return caseRecord;
  }

  async getById(caseId) {
    if (!caseId) throw new Error("Case id is required");
    return this.vault.get(caseId);
  }

  async deleteById(caseId) {
    if (!caseId) throw new Error("Case id is required");
    await this.vault.remove(caseId);
  }
}
