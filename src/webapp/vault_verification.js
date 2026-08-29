import { createVaultKey, decryptValue, encryptValue, IndexedDbLocalVault } from "./local_vault.js";
import { LocalVaultCaseRepository } from "./case_repository.js";

export async function verifyLocalVault() {
  const key = await createVaultKey();
  const vault = new IndexedDbLocalVault(key);
  const repository = new LocalVaultCaseRepository(vault);
  const id = `verification-${crypto.randomUUID()}`;
  const secret = "PRIVATE-CASE-CONTENT-MUST-NOT-BE-STORED-IN-PLAINTEXT";

  const record = { id, status: "draft", payload: { title: "Vault verification", secret } };
  await repository.create(record);
  const restored = await repository.get(id);
  if (restored?.payload?.secret !== secret) throw new Error("Case decryption failed");

  const raw = await readRawVaultRecords();
  const serialized = JSON.stringify(raw);
  if (serialized.includes(secret)) throw new Error("Plaintext Case content found in IndexedDB");
  if (!serialized.includes("ciphertext")) throw new Error("Encrypted envelope missing from IndexedDB");

  const envelope = await encryptValue({ check: true }, key, "verification", "tamper");
  envelope.ciphertext = envelope.ciphertext.slice(0, -2) + "AA";
  let rejected = false;
  try { await decryptValue(envelope, key); } catch { rejected = true; }
  if (!rejected) throw new Error("Tampered ciphertext was accepted");

  await repository.delete(id);
  if (await repository.get(id) !== null) throw new Error("Deleted Case is still retrievable");
  return { ok: true, checks: ["decrypt", "ciphertext-only", "tamper-rejection", "delete"] };
}

async function readRawVaultRecords() {
  const request = indexedDB.open("janavani_local_vault", 2);
  return new Promise((resolve, reject) => {
    request.onerror = () => reject(request.error ?? new Error("IndexedDB open failed"));
    request.onsuccess = () => {
      const db = request.result;
      const query = db.transaction("encrypted_records", "readonly")
        .objectStore("encrypted_records").getAll();
      query.onerror = () => reject(query.error ?? new Error("IndexedDB read failed"));
      query.onsuccess = () => { db.close(); resolve(query.result ?? []); };
    };
  });
}
