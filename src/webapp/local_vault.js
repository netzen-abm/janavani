/**
 * Browser-local encrypted vault for the canonical WebApp boundary.
 *
 * Design constraints:
 * - Web Crypto owns encryption/decryption.
 * - IndexedDB stores ciphertext only.
 * - The encryption key is never written to IndexedDB.
 * - No network fallback is performed here.
 * - Callers must obtain consent/policy before remote processing.
 */

const DB_NAME = "janavani_local_vault";
const DB_VERSION = 1;
const STORE_NAME = "encrypted_cases";
const KEY_SIZE = 256;

function requireWebCrypto() {
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

function encodeJson(value) {
  return new TextEncoder().encode(JSON.stringify(value));
}

function decodeJson(bytes) {
  return JSON.parse(new TextDecoder().decode(bytes));
}

function openDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: "id" });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error ?? new Error("IndexedDB open failed"));
  });
}

export async function createVaultKey() {
  const cryptoApi = requireWebCrypto();
  return cryptoApi.subtle.generateKey(
    { name: "AES-GCM", length: KEY_SIZE },
    false,
    ["encrypt", "decrypt"],
  );
}

export async function encryptValue(value, key) {
  const cryptoApi = requireWebCrypto();
  const iv = cryptoApi.getRandomValues(new Uint8Array(12));
  const ciphertext = await cryptoApi.subtle.encrypt(
    { name: "AES-GCM", iv },
    key,
    encodeJson(value),
  );
  return {
    version: 1,
    algorithm: "AES-GCM",
    iv: bytesToBase64(iv),
    ciphertext: bytesToBase64(new Uint8Array(ciphertext)),
  };
}

export async function decryptValue(envelope, key) {
  const cryptoApi = requireWebCrypto();
  if (envelope?.version !== 1 || envelope?.algorithm !== "AES-GCM") {
    throw new Error("Unsupported encrypted envelope");
  }
  const plaintext = await cryptoApi.subtle.decrypt(
    { name: "AES-GCM", iv: base64ToBytes(envelope.iv) },
    key,
    base64ToBytes(envelope.ciphertext),
  );
  return decodeJson(new Uint8Array(plaintext));
}

export class IndexedDbLocalVault {
  constructor(key) {
    if (!key) throw new Error("A non-null vault key is required");
    this.key = key;
  }

  async put(id, value) {
    if (!id) throw new Error("Vault record id is required");
    const envelope = await encryptValue(value, this.key);
    const db = await openDatabase();
    await new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, "readwrite");
      tx.objectStore(STORE_NAME).put({ id, envelope });
      tx.oncomplete = resolve;
      tx.onerror = () => reject(tx.error ?? new Error("IndexedDB write failed"));
    });
    db.close();
  }

  async get(id) {
    const db = await openDatabase();
    const record = await new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, "readonly");
      const request = tx.objectStore(STORE_NAME).get(id);
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error ?? new Error("IndexedDB read failed"));
    });
    db.close();
    return record ? decryptValue(record.envelope, this.key) : null;
  }

  async list() {
    const db = await openDatabase();
    const records = await new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, "readonly");
      const request = tx.objectStore(STORE_NAME).getAll();
      request.onsuccess = () => resolve(request.result ?? []);
      request.onerror = () => reject(request.error ?? new Error("IndexedDB list failed"));
    });
    db.close();
    return Promise.all(records.map((record) => decryptValue(record.envelope, this.key)));
  }

  async remove(id) {
    const db = await openDatabase();
    await new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, "readwrite");
      tx.objectStore(STORE_NAME).delete(id);
      tx.oncomplete = resolve;
      tx.onerror = () => reject(tx.error ?? new Error("IndexedDB delete failed"));
    });
    db.close();
  }
}
