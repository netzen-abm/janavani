import { createCasePayload } from "./contracts.js";

const DB_NAME = "janavani-local";
const STORE_NAME = "cases";
const DB_VERSION = 1;

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
    request.onerror = () => reject(request.error || new Error("Unable to open local case store"));
  });
}

function transaction(storeMode, work) {
  return openDatabase().then((db) => new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, storeMode);
    const store = tx.objectStore(STORE_NAME);
    let result;
    try {
      result = work(store);
    } catch (error) {
      reject(error);
      return;
    }
    tx.oncomplete = () => {
      db.close();
      resolve(result);
    };
    tx.onerror = () => {
      db.close();
      reject(tx.error || new Error("Local case transaction failed"));
    };
    tx.onabort = () => {
      db.close();
      reject(tx.error || new Error("Local case transaction aborted"));
    };
  }));
}

function makeId() {
  if (globalThis.crypto?.randomUUID) return globalThis.crypto.randomUUID();
  throw new Error("Secure random UUID support is required");
}

export async function saveCase(input) {
  const payload = createCasePayload(input);
  const record = {
    id: makeId(),
    created_at: new Date().toISOString(),
    status: "draft",
    payload,
  };
  await transaction("readwrite", (store) => store.put(record));
  return record;
}

export async function listCases() {
  return transaction("readonly", (store) => {
    const request = store.getAll();
    return new Promise((resolve, reject) => {
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error || new Error("Unable to list local cases"));
    });
  });
}

export async function deleteCase(id) {
  await transaction("readwrite", (store) => store.delete(id));
}
