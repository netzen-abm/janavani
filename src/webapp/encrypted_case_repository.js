import { createCasePayload } from "./contracts.js";
import { IndexedDbLocalVault, createVaultKey } from "./local_vault.js";

export const CASE_NAMESPACE = "case";

export async function createLocalCaseRepository() {
  const key = await createVaultKey();
  return new EncryptedCaseRepository(new IndexedDbLocalVault(key));
}

/** Canonical browser adapter for the shared CaseRepository capability. */
export class EncryptedCaseRepository {
  constructor(vault) {
    if (!(vault instanceof IndexedDbLocalVault)) {
      throw new Error("IndexedDbLocalVault is required");
    }
    this.vault = vault;
  }

  async create(input) {
    const payload = createCasePayload(input);
    const now = new Date().toISOString();
    const record = {
      id: crypto.randomUUID(),
      schema_version: payload.schema_version,
      status: "draft",
      created_at: now,
      updated_at: now,
      payload,
    };
    await this.vault.put(CASE_NAMESPACE, record.id, record);
    return record;
  }

  async get(id) { return this.vault.get(CASE_NAMESPACE, id); }
  async list() { return this.vault.list(CASE_NAMESPACE); }

  async update(record) {
    if (!record?.id) throw new Error("Case id is required");
    const existing = await this.get(record.id);
    if (!existing) return null;
    const updated = { ...existing, ...record, updated_at: new Date().toISOString() };
    await this.vault.put(CASE_NAMESPACE, updated.id, updated);
    return updated;
  }

  async updateStatus(id, status) {
    const existing = await this.get(id);
    if (!existing) return null;
    return this.update({ ...existing, status });
  }

  async delete(id) {
    await this.vault.remove(CASE_NAMESPACE, id);
    return true;
  }
}
