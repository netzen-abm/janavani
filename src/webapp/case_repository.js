import { IndexedDbLocalVault } from "./local_vault.js";

const CASE_NAMESPACE = "case";

/** Canonical browser adapter for the shared CaseRepository capability. */
export class LocalVaultCaseRepository {
  constructor(vault) {
    if (!(vault instanceof IndexedDbLocalVault)) {
      throw new Error("An IndexedDbLocalVault is required");
    }
    this.vault = vault;
  }

  async create(caseRecord) {
    return this.save(caseRecord);
  }

  async save(caseRecord) {
    if (!caseRecord?.id) throw new Error("Case id is required");
    await this.vault.put(CASE_NAMESPACE, caseRecord.id, caseRecord);
    return caseRecord;
  }

  async get(caseId) {
    if (!caseId) throw new Error("Case id is required");
    return this.vault.get(CASE_NAMESPACE, caseId);
  }

  async getById(caseId) {
    return this.get(caseId);
  }

  async list() {
    return this.vault.list(CASE_NAMESPACE);
  }

  async update(caseRecord) {
    return this.save(caseRecord);
  }

  async updateStatus(caseId, status) {
    const record = await this.get(caseId);
    if (!record) return null;
    const updated = { ...record, status, updated_at: new Date().toISOString() };
    return this.save(updated);
  }

  async delete(caseId) {
    if (!caseId) throw new Error("Case id is required");
    await this.vault.remove(CASE_NAMESPACE, caseId);
    return true;
  }

  async deleteById(caseId) {
    return this.delete(caseId);
  }
}
