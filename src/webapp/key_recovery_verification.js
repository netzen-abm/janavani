import { BrowserDeviceKeyProvider } from "./device_key_provider.js";
import { IndexedDbLocalVault } from "./local_vault.js";

export async function verifyKeyRecovery() {
  const first = new BrowserDeviceKeyProvider();
  const passphrase = "janavani-verification-passphrase-1";
  const rotated = "janavani-verification-passphrase-2";
  const key = await first.create(passphrase);
  const vault = new IndexedDbLocalVault(key);
  const id = `recovery-${crypto.randomUUID()}`;
  const secret = "RECOVERY-CHECK-PRIVATE-CONTENT";
  await vault.put("case", id, { id, payload: { secret } });

  await first.destroy();

  const wrong = new BrowserDeviceKeyProvider();
  let wrongRejected = false;
  try { await wrong.unlock("wrong-passphrase-xxxxxxxx"); } catch { wrongRejected = true; }
  if (!wrongRejected) throw new Error("Wrong recovery passphrase was accepted");

  const second = new BrowserDeviceKeyProvider();
  const recovered = await second.unlock(passphrase);
  const restored = await new IndexedDbLocalVault(recovered).get("case", id);
  if (restored?.payload?.secret !== secret) throw new Error("Recovered key cannot decrypt original Case");

  await second.rotate(passphrase, rotated);
  await second.destroy();
  const third = new BrowserDeviceKeyProvider();
  let oldRejected = false;
  try { await third.unlock(passphrase); } catch { oldRejected = true; }
  if (!oldRejected) throw new Error("Old recovery passphrase remained valid after rotation");
  const finalKey = await third.unlock(rotated);
  const finalRecord = await new IndexedDbLocalVault(finalKey).get("case", id);
  if (finalRecord?.payload?.secret !== secret) throw new Error("Rotated recovery key cannot decrypt original Case");

  await third.destroy();
  return { ok: true, checks: ["wrong-passphrase-rejection", "reload-recovery", "same-key-decryption", "rotation"] };
}
