/**
 * User-controlled recovery for the local vault's data-encryption key.
 *
 * The recovery secret never leaves the device. A PBKDF2-derived AES-GCM key
 * encrypts a random 256-bit data key; only the salt and wrapped key are stored.
 * The recovered data key is imported as a non-extractable CryptoKey.
 *
 * This is a recovery primitive, not a password manager. Production UX must
 * enforce strong passphrases, rate limiting where applicable, recovery export
 * warnings, and independent security review.
 */

const PBKDF2_ITERATIONS = 600_000;
const SALT_BYTES = 16;
const IV_BYTES = 12;
const KEY_BYTES = 32;
const VERSION = 1;

function cryptoApi() {
  if (!globalThis.crypto?.subtle || !globalThis.crypto?.getRandomValues) {
    throw new Error("Web Crypto API is required");
  }
  return globalThis.crypto;
}

function bytesToBase64(bytes) {
  let binary = "";
  bytes.forEach((byte) => { binary += String.fromCharCode(byte); });
  return btoa(binary);
}

function base64ToBytes(value) {
  const binary = atob(value);
  return Uint8Array.from(binary, (char) => char.charCodeAt(0));
}

async function deriveRecoveryKey(passphrase, salt) {
  if (typeof passphrase !== "string" || passphrase.length < 12) {
    throw new Error("Recovery passphrase must be at least 12 characters");
  }
  const api = cryptoApi();
  const material = await api.subtle.importKey(
    "raw", new TextEncoder().encode(passphrase), "PBKDF2", false, ["deriveKey"],
  );
  return api.subtle.deriveKey(
    { name: "PBKDF2", salt, iterations: PBKDF2_ITERATIONS, hash: "SHA-256" },
    material,
    { name: "AES-GCM", length: 256 },
    false,
    ["encrypt", "decrypt"],
  );
}

export async function createRecoveryRecord(passphrase) {
  const api = cryptoApi();
  const salt = api.getRandomValues(new Uint8Array(SALT_BYTES));
  const iv = api.getRandomValues(new Uint8Array(IV_BYTES));
  const recoveryKey = await deriveRecoveryKey(passphrase, salt);
  const rawDataKey = api.getRandomValues(new Uint8Array(KEY_BYTES));
  const wrapped = await api.subtle.encrypt({ name: "AES-GCM", iv }, recoveryKey, rawDataKey);
  return {
    version: VERSION,
    kdf: "PBKDF2-SHA256",
    iterations: PBKDF2_ITERATIONS,
    cipher: "AES-GCM-256",
    salt: bytesToBase64(salt),
    iv: bytesToBase64(iv),
    wrapped_key: bytesToBase64(new Uint8Array(wrapped)),
  };
}

export async function recoverDataKey(passphrase, record) {
  if (record?.version !== VERSION || record?.kdf !== "PBKDF2-SHA256" || record?.cipher !== "AES-GCM-256") {
    throw new Error("Unsupported recovery record");
  }
  const api = cryptoApi();
  const recoveryKey = await deriveRecoveryKey(passphrase, base64ToBytes(record.salt));
  const raw = await api.subtle.decrypt(
    { name: "AES-GCM", iv: base64ToBytes(record.iv) },
    recoveryKey,
    base64ToBytes(record.wrapped_key),
  );
  return api.subtle.importKey("raw", raw, { name: "AES-GCM", length: 256 }, false, ["encrypt", "decrypt"]);
}
