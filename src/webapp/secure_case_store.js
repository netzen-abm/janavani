import { createCasePayload } from "./contracts.js";
import { IndexedDbLocalVault, createVaultKey } from "./local_vault.js";

/**
 * Canonical local Case persistence factory.
 * The vault key is held by the running client and is never persisted here.
 * Device-key recovery/migration belongs to a future platform key provider.
 */
export async function createLocalCaseRepository() {
  const key = await createVaultKey();
  const vault = new IndexedDbLocalVault(key);
  return new EncryptedCaseRepository(vault);
}

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
    await this.vault.put(record.id, record);
    return record;
  }

  async get(id) { return this.vault.get(id); }
  async list() { return this.vault.list(); }

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
