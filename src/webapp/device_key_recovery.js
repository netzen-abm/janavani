/**
 * User-controlled recovery for the LocalVault data-encryption key.
 * The passphrase and raw data key never leave the active client.
 */

const PBKDF2_ITERATIONS = 600_000;
const SALT_BYTES = 16;
const IV_BYTES = 12;
const VERSION = 2;

function api() {
  if (!globalThis.crypto?.subtle || !globalThis.crypto?.getRandomValues) throw new Error("Web Crypto API is required");
  return globalThis.crypto;
}
function b64(bytes) { let s = ""; bytes.forEach((b) => { s += String.fromCharCode(b); }); return btoa(s); }
function unb64(value) { const s = atob(value); return Uint8Array.from(s, (c) => c.charCodeAt(0)); }

async function deriveRecoveryKey(passphrase, salt) {
  if (typeof passphrase !== "string" || passphrase.length < 12) throw new Error("Recovery passphrase must be at least 12 characters");
  const material = await api().subtle.importKey("raw", new TextEncoder().encode(passphrase), "PBKDF2", false, ["deriveKey"]);
  return api().subtle.deriveKey(
    { name: "PBKDF2", salt, iterations: PBKDF2_ITERATIONS, hash: "SHA-256" },
    material,
    { name: "AES-GCM", length: 256 },
    false,
    ["encrypt", "decrypt"],
  );
}

/** Wrap the actual non-extractable vault key using the recovery passphrase. */
export async function createRecoveryRecord(dataKey, passphrase) {
  const salt = api().getRandomValues(new Uint8Array(SALT_BYTES));
  const iv = api().getRandomValues(new Uint8Array(IV_BYTES));
  const recoveryKey = await deriveRecoveryKey(passphrase, salt);
  const wrapped = await api().subtle.wrapKey("raw", dataKey, recoveryKey, { name: "AES-GCM", iv });
  return {
    version: VERSION,
    kdf: "PBKDF2-SHA256",
    iterations: PBKDF2_ITERATIONS,
    cipher: "AES-GCM-256",
    salt: b64(salt),
    iv: b64(iv),
    wrapped_key: b64(new Uint8Array(wrapped)),
  };
}

/** Recover the same vault key, imported as non-extractable. */
export async function recoverDataKey(passphrase, record) {
  if (record?.version !== VERSION || record?.kdf !== "PBKDF2-SHA256" || record?.cipher !== "AES-GCM-256") throw new Error("Unsupported recovery record");
  const recoveryKey = await deriveRecoveryKey(passphrase, unb64(record.salt));
  return api().subtle.unwrapKey(
    "raw",
    unb64(record.wrapped_key),
    recoveryKey,
    { name: "AES-GCM", iv: unb64(record.iv) },
    { name: "AES-GCM", length: 256 },
    false,
    ["encrypt", "decrypt"],
  );
}
