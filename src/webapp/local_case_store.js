import { createCasePayload } from "./contracts.js";
import { IndexedDbLocalVault, createVaultKey } from "./local_vault.js";
import { WebSessionKeyProvider } from "./device_key_provider.js";

export async function createLocalCaseRepository() {
  const keyProvider = new WebSessionKeyProvider(createVaultKey);
  const key = await keyProvider.create();
  return new EncryptedCaseRepository(new IndexedDbLocalVault(key), keyProvider);
}

export class EncryptedCaseRepository {
  constructor(vault, keyProvider = null) {
    this.vault = vault;
    this.keyProvider = keyProvider;
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
    await this.vault.put("case", record.id, record);
    return record;
  }

  async get(id) { return this.vault.get("case", id); }
  async list() { return this.vault.list("case"); }

  async update(record) {
    if (!record?.id) throw new Error("Case id is required");
    const existing = await this.get(record.id);
    if (!existing) return null;
    const updated = { ...existing, ...record, updated_at: new Date().toISOString() };
    await this.vault.put("case", updated.id, updated);
    return updated;
  }

  async updateStatus(id, status) {
    const existing = await this.get(id);
    if (!existing) return null;
    return this.update({ ...existing, status });
  }

  async delete(id) {
    await this.vault.remove("case", id);
    return true;
  }

  async destroySessionKey() {
    if (this.keyProvider) await this.keyProvider.destroy();
  }
}
