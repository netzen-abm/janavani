/**
 * Browser-local encrypted vault for the canonical WebApp boundary.
 *
 * Design constraints:
 * - Web Crypto owns encryption/decryption.
 * - IndexedDB stores ciphertext only.
 * - The encryption key is never written to IndexedDB.
 * - No network fallback is performed here.
 * - Callers must obtain consent/policy before remote processing.
 * - Records are namespaced so capabilities share infrastructure safely.
 */

const DB_NAME = "janavani_local_vault";
const DB_VERSION = 2;
const STORE_NAME = "encrypted_records";
const KEY_SIZE = 256;
const IV_BYTES = 12;

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

function encode(value) { return new TextEncoder().encode(JSON.stringify(value)); }
function decode(bytes) { return JSON.parse(new TextDecoder().decode(bytes)); }

function recordKey(namespace, id) {
  if (!namespace || !id) throw new Error("Vault namespace and id are required");
  return `${namespace}:${id}`;
}

function associatedData(namespace, id, version) {
  return encode({ namespace, id, version });
}

function openDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: "key" });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error ?? new Error("IndexedDB open failed"));
  });
}

export async function createVaultKey() {
  return requireWebCrypto().subtle.generateKey(
    { name: "AES-GCM", length: KEY_SIZE },
    false,
    ["encrypt", "decrypt"],
  );
}

export async function encryptValue(value, key, namespace = "default", id = "value") {
  const cryptoApi = requireWebCrypto();
  const version = 2;
  const iv = cryptoApi.getRandomValues(new Uint8Array(IV_BYTES));
  const ciphertext = await cryptoApi.subtle.encrypt(
    { name: "AES-GCM", iv, additionalData: associatedData(namespace, id, version) },
    key,
    encode(value),
  );
  return {
    version,
    algorithm: "AES-GCM",
    namespace,
    id,
    iv: bytesToBase64(iv),
    ciphertext: bytesToBase64(new Uint8Array(ciphertext)),
  };
}

export async function decryptValue(envelope, key) {
  const cryptoApi = requireWebCrypto();
  if (envelope?.version !== 2 || envelope?.algorithm !== "AES-GCM") {
    throw new Error("Unsupported encrypted envelope");
  }
  const plaintext = await cryptoApi.subtle.decrypt(
    {
      name: "AES-GCM",
      iv: base64ToBytes(envelope.iv),
      additionalData: associatedData(envelope.namespace, envelope.id, envelope.version),
    },
    key,
    base64ToBytes(envelope.ciphertext),
  );
  return decode(new Uint8Array(plaintext));
}

export class IndexedDbLocalVault {
  constructor(key) {
    if (!key) throw new Error("A non-null vault key is required");
    this.key = key;
  }

  async put(namespace, id, value) {
    const envelope = await encryptValue(value, this.key, namespace, id);
    const db = await openDatabase();
    await new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, "readwrite");
      tx.objectStore(STORE_NAME).put({ key: recordKey(namespace, id), envelope });
      tx.oncomplete = resolve;
      tx.onerror = () => reject(tx.error ?? new Error("IndexedDB write failed"));
    });
    db.close();
  }

  async get(namespace, id) {
    const db = await openDatabase();
    const record = await new Promise((resolve, reject) => {
      const request = db.transaction(STORE_NAME, "readonly").objectStore(STORE_NAME).get(recordKey(namespace, id));
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error ?? new Error("IndexedDB read failed"));
    });
    db.close();
    return record ? decryptValue(record.envelope, this.key) : null;
  }

  async list(namespace) {
    const db = await openDatabase();
    const records = await new Promise((resolve, reject) => {
      const request = db.transaction(STORE_NAME, "readonly").objectStore(STORE_NAME).getAll();
      request.onsuccess = () => resolve(request.result ?? []);
      request.onerror = () => reject(request.error ?? new Error("IndexedDB list failed"));
    });
    db.close();
    return Promise.all(records
      .filter((record) => record.envelope?.namespace === namespace)
      .map((record) => decryptValue(record.envelope, this.key)));
  }

  async remove(namespace, id) {
    const db = await openDatabase();
    await new Promise((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, "readwrite");
      tx.objectStore(STORE_NAME).delete(recordKey(namespace, id));
      tx.oncomplete = resolve;
      tx.onerror = () => reject(tx.error ?? new Error("IndexedDB delete failed"));
    });
    db.close();
  }
}
