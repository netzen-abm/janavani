/**
 * Provider-neutral device key boundary with a browser implementation.
 *
 * The raw data-encryption key is never persisted. It is wrapped by an
 * AES-GCM key derived from a user-controlled recovery passphrase. The
 * passphrase exists only in memory during the active operation/session.
 *
 * IMPORTANT: this provider is a lifecycle boundary. The vault key and
 * recovery wrapping must be generated from the same data key before this
 * provider is considered production-ready.
 */

import { createVaultKey } from "./local_vault.js";
import { createRecoveryRecord, recoverDataKey } from "./device_key_recovery.js";

const DB_NAME = "janavani_device_keys";
const STORE_NAME = "key_material";
const RECORD_ID = "primary";

function openDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, 1);
    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(STORE_NAME)) db.createObjectStore(STORE_NAME, { keyPath: "id" });
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error ?? new Error("Device key store unavailable"));
  });
}

async function readRecord() {
  const db = await openDatabase();
  return new Promise((resolve, reject) => {
    const request = db.transaction(STORE_NAME, "readonly").objectStore(STORE_NAME).get(RECORD_ID);
    request.onsuccess = () => { db.close(); resolve(request.result ?? null); };
    request.onerror = () => { db.close(); reject(request.error ?? new Error("Device key record unavailable")); };
  });
}

async function writeRecord(record) {
  const db = await openDatabase();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readwrite");
    tx.objectStore(STORE_NAME).put({ id: RECORD_ID, ...record });
    tx.oncomplete = () => { db.close(); resolve(); };
    tx.onerror = () => { db.close(); reject(tx.error ?? new Error("Device key record write failed")); };
  });
}

async function removeRecord() {
  const db = await openDatabase();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE_NAME, "readwrite");
    tx.objectStore(STORE_NAME).delete(RECORD_ID);
    tx.oncomplete = () => { db.close(); resolve(); };
    tx.onerror = () => { db.close(); reject(tx.error ?? new Error("Device key record deletion failed")); };
  });
}

export class DeviceKeyProvider {
  async create() { throw new Error("Not implemented"); }
  async unlock() { throw new Error("Not implemented"); }
  async rotate() { throw new Error("Not implemented"); }
  async destroy() { throw new Error("Not implemented"); }
}

export class BrowserDeviceKeyProvider extends DeviceKeyProvider {
  constructor() { super(); this.key = null; }

  async create(passphrase) {
    if (typeof passphrase !== "string" || passphrase.length < 12) throw new Error("Recovery passphrase must be at least 12 characters");
    this.key = await createVaultKey();
    const recoveryRecord = await createRecoveryRecord(passphrase);
    await writeRecord({ version: 1, recovery: recoveryRecord });
    return this.key;
  }

  async unlock(passphrase) {
    const record = await readRecord();
    if (!record?.recovery) throw new Error("No recoverable device key is configured");
    this.key = await recoverDataKey(passphrase, record.recovery);
    return this.key;
  }

  async rotate(passphrase) {
    await this.destroy();
    return this.create(passphrase);
  }

  async destroy() {
    this.key = null;
    await removeRecord();
  }
}
