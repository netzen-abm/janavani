import { createVaultKey, IndexedDbLocalVault } from "./local_vault.js";
import { createEncryptedAttachment, getEncryptedAttachment, removeEncryptedAttachment } from "./evidence_attachments.js";

export async function verifyEncryptedAttachment() {
  const key = await createVaultKey();
  const vault = new IndexedDbLocalVault(key);
  const secret = "PRIVATE-ATTACHMENT-CONTENT-MUST-NOT-BE-STORED-IN-PLAINTEXT";
  const file = new File([secret], "verification.txt", { type: "text/plain", lastModified: 0 });
  const evidence = await createEncryptedAttachment({ caseId: "verification-case", file, vault });
  const restored = await getEncryptedAttachment(evidence.id, vault);
  if (!restored?.bytes) throw new Error("Encrypted attachment could not be restored");
  const text = new TextDecoder().decode(restored.bytes);
  if (text !== secret) throw new Error("Attachment content did not round-trip");

  const request = indexedDB.open("janavani_local_vault", 2);
  const raw = await new Promise((resolve, reject) => {
    request.onerror = () => reject(request.error ?? new Error("IndexedDB open failed"));
    request.onsuccess = () => {
      const db = request.result;
      const q = db.transaction("encrypted_records", "readonly").objectStore("encrypted_records").getAll();
      q.onerror = () => reject(q.error ?? new Error("IndexedDB read failed"));
      q.onsuccess = () => { db.close(); resolve(q.result ?? []); };
    };
  });
  if (JSON.stringify(raw).includes(secret)) throw new Error("Plaintext attachment content found in IndexedDB");
  await removeEncryptedAttachment(evidence.id, vault);
  if (await getEncryptedAttachment(evidence.id, vault) !== null) throw new Error("Deleted attachment remains retrievable");
  return { ok: true, checks: ["round-trip", "ciphertext-only", "delete"] };
}
