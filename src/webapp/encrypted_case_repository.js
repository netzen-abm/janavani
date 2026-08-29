import { createCasePayload } from "./contracts.js";
import { IndexedDbLocalVault } from "./local_vault.js";

export class EncryptedCaseRepository {
  constructor(vault) {
    if (!(vault instanceof IndexedDbLocalVault)) {
      throw new Error("IndexedDbLocalVault is required");
    }
    this.vault = vault;
  }

  async create(input) {
    const payload = createCasePayload(input);
    const record = {
      id: crypto.randomUUID(),
      schema_version: payload.schema_version,
      status: "draft",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      payload,
    };
    await this.vault.put(record.id, record);
    return record;
  }

  async get(id) {
    return this.vault.get(id);
  }

  async list() {
    return this.vault.list();
  }

  async update(record) {
    if (!record?.id) throw new Error("Case id is required");
    const existing = await this.get(record.id);
    if (!existing) return null;
    const updated = { ...existing, ...record, updated_at: new Date().toISOString() };
    await this.vault.put(updated.id, updated);
    return updated;
  }

  async updateStatus(id, status) {
    const existing = await this.get(id);
    if (!existing) return null;
    return this.update({ ...existing, status });
  }

  async delete(id) {
    await this.vault.remove(id);
    return true;
  }
}
