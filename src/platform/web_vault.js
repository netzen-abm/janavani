// Janavani browser-local encrypted vault.
//
// Security boundary:
// - plaintext exists only in the calling page memory;
// - records are encrypted with AES-256-GCM before IndexedDB persistence;
// - the non-extractable CryptoKey is itself stored in IndexedDB via structured clone;
// - no localStorage/sessionStorage is used for case data or key material;
// - remote transport is intentionally outside this module.
//
// This is a provider implementation of the LocalVault contract, not a complete
// identity/recovery system. Losing the origin's IndexedDB data/key loses access
// unless a future explicit recovery/export capability is used.

const DB_NAME = "janavani-local-vault";
const DB_VERSION = 1;
const KEY_STORE = "keys";
const RECORD_STORE = "records";
const KEY_ID = "case-vault-v1";
const ALGORITHM = "AES-GCM";
const KEY_LENGTH = 256;
const IV_BYTES = 12;
const VERSION = 1;

function assertSecureContext() {
  if (!globalThis.isSecureContext || !globalThis.crypto?.subtle) {
    throw new Error("Janavani local vault requires a secure context with Web Crypto (HTTPS).");
  }
}

function openDb() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(KEY_STORE)) {
        db.createObjectStore(KEY_STORE, { keyPath: "id" });
      }
      if (!db.objectStoreNames.contains(RECORD_STORE)) {
        const store = db.createObjectStore(RECORD_STORE, { keyPath: "id" });
        store.createIndex("updatedAt", "updatedAt", { unique: false });
      }
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error ?? new Error("Unable to open local vault."));
  });
}

function transaction(db, storeName, mode, operation) {
  return new Promise((resolve, reject) => {
    const tx = db.transaction(storeName, mode);
    const store = tx.objectStore(storeName);
    let request;
    try {
      request = operation(store);
    } catch (error) {
      reject(error);
      return;
    }
    if (request) {
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error ?? new Error("IndexedDB request failed."));
    }
    tx.oncomplete = () => resolve(request?.result);
    tx.onerror = () => reject(tx.error ?? new Error("IndexedDB transaction failed."));
    tx.onabort = () => reject(tx.error ?? new Error("IndexedDB transaction aborted."));
  });
}

async function getOrCreateKey(db) {
  const existing = await transaction(db, KEY_STORE, "readonly", (store) => store.get(KEY_ID));
  if (existing?.key) return existing.key;

  const key = await crypto.subtle.generateKey(
    { name: ALGORITHM, length: KEY_LENGTH },
    false,
    ["encrypt", "decrypt"],
  );

  await transaction(db, KEY_STORE, "readwrite", (store) =>
    store.put({ id: KEY_ID, version: VERSION, algorithm: ALGORITHM, key }),
  );
  return key;
}

function utf8(value) {
  return new TextEncoder().encode(value);
}

function decode(bytes) {
  return new TextDecoder().decode(bytes);
}

function bytesToBase64(bytes) {
  let binary = "";
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) {
    binary += String.fromCharCode(...bytes.subarray(i, i + chunk));
  }
  return btoa(binary);
}

function base64ToBytes(value) {
  const binary = atob(value);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) bytes[i] = binary.charCodeAt(i);
  return bytes;
}

function aadFor(id) {
  return utf8(`janavani-local-vault:${VERSION}:${id}`);
}

async function encryptRecord(key, id, value) {
  const iv = crypto.getRandomValues(new Uint8Array(IV_BYTES));
  const plaintext = utf8(JSON.stringify(value));
  const ciphertext = await crypto.subtle.encrypt(
    { name: ALGORITHM, iv, additionalData: aadFor(id), tagLength: 128 },
    key,
    plaintext,
  );
  return {
    id,
    version: VERSION,
    algorithm: ALGORITHM,
    iv: bytesToBase64(iv),
    ciphertext: bytesToBase64(new Uint8Array(ciphertext)),
    updatedAt: new Date().toISOString(),
  };
}

async function decryptRecord(key, record) {
  if (!record || record.version !== VERSION || record.algorithm !== ALGORITHM) {
    throw new Error("Unsupported or invalid vault record.");
  }
  const plaintext = await crypto.subtle.decrypt(
    {
      name: ALGORITHM,
      iv: base64ToBytes(record.iv),
      additionalData: aadFor(record.id),
      tagLength: 128,
    },
    key,
    base64ToBytes(record.ciphertext),
  );
  return JSON.parse(decode(new Uint8Array(plaintext)));
}

export async function putCase(caseId, caseValue) {
  assertSecureContext();
  if (!caseId || typeof caseId !== "string") throw new Error("caseId is required.");
  if (caseValue === undefined) throw new Error("caseValue is required.");

  const db = await openDb();
  try {
    const key = await getOrCreateKey(db);
    const record = await encryptRecord(key, `case:${caseId}`, caseValue);
    await transaction(db, RECORD_STORE, "readwrite", (store) => store.put(record));
  } finally {
    db.close();
  }
}

export async function getCase(caseId) {
  assertSecureContext();
  if (!caseId || typeof caseId !== "string") throw new Error("caseId is required.");

  const db = await openDb();
  try {
    const record = await transaction(db, RECORD_STORE, "readonly", (store) => store.get(`case:${caseId}`));
    if (!record) return null;
    const key = await getOrCreateKey(db);
    return await decryptRecord(key, record);
  } finally {
    db.close();
  }
}

export async function deleteCase(caseId) {
  assertSecureContext();
  if (!caseId || typeof caseId !== "string") throw new Error("caseId is required.");
  const db = await openDb();
  try {
    await transaction(db, RECORD_STORE, "readwrite", (store) => store.delete(`case:${caseId}`));
  } finally {
    db.close();
  }
}

export async function listCaseIds() {
  assertSecureContext();
  const db = await openDb();
  try {
    const rows = await transaction(db, RECORD_STORE, "readonly", (store) => store.getAllKeys());
    return rows.filter((id) => typeof id === "string" && id.startsWith("case:")).map((id) => id.slice(5));
  } finally {
    db.close();
  }
}

export async function clearVault() {
  assertSecureContext();
  const db = await openDb();
  try {
    await transaction(db, RECORD_STORE, "readwrite", (store) => store.clear());
  } finally {
    db.close();
  }
}
