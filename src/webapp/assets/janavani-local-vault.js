/* JANAVANI device-local draft vault.
 * Records remain in this browser's IndexedDB. The server-issued HMAC scope is
 * a namespace only; it is not an authentication credential or encryption key.
 * Do not use this module to imply encrypted-at-rest protection.
 */
(() => {
  "use strict";

  const DB_NAME = "janavani-device-vault";
  const DB_VERSION = 1;
  const STORE = "case-drafts";
  const MAX_SUBJECT = 500;
  const MAX_NARRATIVE = 20000;
  const SCOPE_RE = /^[a-f0-9]{64}$/;

  function validScope(scope) {
    if (typeof scope !== "string" || !SCOPE_RE.test(scope)) {
      throw new TypeError("A verified account vault scope is required.");
    }
    return scope;
  }

  function openDatabase() {
    if (!("indexedDB" in window)) {
      return Promise.reject(new Error("This browser does not support local draft storage."));
    }
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);
      request.onupgradeneeded = () => {
        const db = request.result;
        if (!db.objectStoreNames.contains(STORE)) {
          const store = db.createObjectStore(STORE, { keyPath: "id" });
          store.createIndex("by_scope", "scope", { unique: false });
          store.createIndex("by_scope_updated", ["scope", "updated_at"], { unique: false });
        }
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error || new Error("Could not open local draft storage."));
      request.onblocked = () => reject(new Error("Local draft storage is blocked by another browser tab."));
    });
  }

  async function resolveScope() {
    const response = await fetch("/civic/cases/local-vault/scope", {
      method: "GET",
      credentials: "same-origin",
      cache: "no-store",
      headers: { "Accept": "application/json" }
    });
    if (!response.ok) {
      throw new Error(response.status === 401
        ? "Sign in before opening private local drafts."
        : "Could not verify the local draft account scope.");
    }
    const data = await response.json();
    return validScope(data.scope);
  }

  function requestResult(request) {
    return new Promise((resolve, reject) => {
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error || new Error("Local draft operation failed."));
    });
  }

  async function withStore(scope, mode, operation) {
    validScope(scope);
    const db = await openDatabase();
    try {
      const tx = db.transaction(STORE, mode);
      const store = tx.objectStore(STORE);
      const result = await operation(store);
      await new Promise((resolve, reject) => {
        tx.oncomplete = resolve;
        tx.onerror = () => reject(tx.error || new Error("Local draft transaction failed."));
        tx.onabort = () => reject(tx.error || new Error("Local draft transaction was aborted."));
      });
      return result;
    } finally {
      db.close();
    }
  }

  async function saveDraft(scope, draft) {
    validScope(scope);
    if (!draft || typeof draft !== "object") throw new TypeError("Draft data is required.");
    const caseId = String(draft.case_id || "").trim();
    const subject = String(draft.subject || "");
    const narrative = String(draft.narrative || "");
    if (!caseId) throw new TypeError("A Case ID is required.");
    if (subject.length > MAX_SUBJECT || narrative.length > MAX_NARRATIVE) {
      throw new RangeError("Draft exceeds the local storage size limit.");
    }
    const record = {
      id: scope + ":" + caseId,
      scope,
      case_id: caseId,
      subject,
      narrative,
      updated_at: new Date().toISOString(),
      schema_version: 1
    };
    await withStore(scope, "readwrite", store => requestResult(store.put(record)));
    return { case_id: caseId, updated_at: record.updated_at };
  }

  async function getDraft(scope, caseId) {
    validScope(scope);
    const id = scope + ":" + String(caseId || "").trim();
    return withStore(scope, "readonly", store => requestResult(store.get(id)));
  }

  async function listDrafts(scope) {
    validScope(scope);
    return withStore(scope, "readonly", store =>
      requestResult(store.index("by_scope").getAll(scope))
    );
  }

  async function deleteDraft(scope, caseId) {
    validScope(scope);
    const id = scope + ":" + String(caseId || "").trim();
    return withStore(scope, "readwrite", store => requestResult(store.delete(id)));
  }

  async function clearScope(scope) {
    validScope(scope);
    return withStore(scope, "readwrite", async store => {
      const records = await requestResult(store.index("by_scope").getAllKeys(scope));
      for (const key of records) store.delete(key);
      return records.length;
    });
  }

  window.JanavaniLocalVault = Object.freeze({
    resolveScope,
    saveDraft,
    getDraft,
    listDrafts,
    deleteDraft,
    clearScope
  });
})();
