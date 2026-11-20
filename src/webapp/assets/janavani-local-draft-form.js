(() => {
  const form = document.getElementById("local-case-draft-form");
  const field = document.getElementById("citizen-input");
  const status = document.getElementById("local-vault-status");
  if (!form || !field || !window.JanavaniLocalVault) return;
  let scope = null;
  let caseId = null;
  let pendingSave = Promise.resolve();
  let scopeCheck = null;
  const MAX_IMPORT_BYTES = 256 * 1024;
  field.disabled = true;
  const setStatus = (message) => { status.textContent = message; };
  const draftList = document.getElementById("local-draft-list");
  const newLocalId = () => "local-" + (crypto.randomUUID ? crypto.randomUUID() : Date.now().toString(36) + Math.random().toString(36).slice(2));
  const refreshDraftList = async (selectedId = caseId) => {
    const drafts = await window.JanavaniLocalVault.listDrafts(scope);
    draftList.replaceChildren();
    drafts.sort((a, b) => b.updated_at.localeCompare(a.updated_at)).forEach(draft => {
      const option = document.createElement("option");
      option.value = draft.case_id;
      option.textContent = (draft.server_case_id ? draft.server_case_id + " — " : "") +
        new Date(draft.updated_at).toLocaleString();
      option.selected = draft.case_id === selectedId;
      draftList.appendChild(option);
    });
    if (!draftList.options.length) {
      const option = document.createElement("option");
      option.value = "";
      option.textContent = "No saved drafts";
      draftList.appendChild(option);
    }
  };
  const restoreForScope = async (nextScope) => {
    scope = nextScope;
    caseId = newLocalId();
    field.value = "";
    const drafts = await window.JanavaniLocalVault.listDrafts(scope);
    const latest = drafts.sort((a, b) => b.updated_at.localeCompare(a.updated_at))[0];
    if (latest) {
      caseId = latest.case_id;
      field.value = latest.narrative || "";
      setStatus("Your latest local draft was restored in this browser.");
    } else {
      setStatus("Drafts stay in this browser until you choose to create a Case.");
    }
    await refreshDraftList(caseId);
    field.disabled = false;
  };
  const checkAccountScope = () => {
    if (scopeCheck) return scopeCheck;
    scopeCheck = (async () => {
      try {
        const currentScope = await window.JanavaniLocalVault.resolveScope();
        if (currentScope === scope) return true;
        await pendingSave;
        await restoreForScope(currentScope);
        setStatus("The signed-in account changed. Drafts remain isolated by account.");
        return false;
      } catch (_error) {
        await pendingSave;
        scope = null;
        caseId = null;
        field.value = "";
        field.disabled = true;
        draftList.replaceChildren();
        setStatus("Sign in again to access local drafts. Previous account drafts remain in this browser.");
        return false;
      }
    })();
    return scopeCheck.finally(() => { scopeCheck = null; });
  };
  const save = async () => {
    const writeScope = scope;
    const writeCaseId = caseId;
    const narrative = field.value;
    if (!writeScope || !writeCaseId) return;
    await window.JanavaniLocalVault.saveDraft(writeScope, {
      case_id: writeCaseId, subject: "Civic complaint", narrative
    });
    setStatus("Draft saved in this browser. It is not a server backup.");
  };
  (async () => {
    try {
      await restoreForScope(await window.JanavaniLocalVault.resolveScope());
    } catch (error) {
      field.disabled = true;
      setStatus("Local draft storage is unavailable. No content will be sent. " + error.message);
    }
  })();
  field.addEventListener("input", () => {
    const writeScope = scope;
    const writeCaseId = caseId;
    const narrative = field.value;
    pendingSave = pendingSave.then(async () => {
      if (!writeScope || !writeCaseId) return;
      await window.JanavaniLocalVault.saveDraft(writeScope, {
        case_id: writeCaseId, subject: "Civic complaint", narrative
      });
      setStatus("Draft saved in this browser. It is not a server backup.");
    }).catch(error => {
      setStatus("Local save failed. Do not navigate away. " + error.message);
    });
  });
  window.addEventListener("focus", () => { checkAccountScope(); });
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden) checkAccountScope();
  });
  document.getElementById("open-local-draft").addEventListener("click", async () => {
    try {
      if (!(await checkAccountScope())) return;
      await pendingSave;
      const selected = await window.JanavaniLocalVault.getDraft(scope, draftList.value);
      if (!selected) throw new Error("Selected draft was not found.");
      caseId = selected.case_id;
      field.value = selected.narrative || "";
      setStatus("Opened local draft. Changes save automatically in this browser.");
    } catch (error) {
      setStatus("Could not open draft. " + error.message);
    }
  });
  document.getElementById("delete-local-draft").addEventListener("click", async () => {
    if (!(await checkAccountScope())) return;
    const selectedId = draftList.value;
    if (!selectedId || !window.confirm("Delete this local draft from this browser? This cannot be undone.")) return;
    try {
      await pendingSave;
      await window.JanavaniLocalVault.deleteDraft(scope, selectedId);
      if (caseId === selectedId) {
        caseId = newLocalId();
        field.value = "";
      }
      await refreshDraftList();
      setStatus("Selected local draft deleted.");
    } catch (error) {
      setStatus("Could not delete draft. " + error.message);
    }
  });
  document.getElementById("import-local-draft").addEventListener("change", async (event) => {
    const file = event.target.files && event.target.files[0];
    if (!file) return;
    try {
      if (!(await checkAccountScope())) return;
      if (file.size > MAX_IMPORT_BYTES) throw new Error("Import file exceeds the 256 KB limit.");
      await pendingSave;
      const payload = JSON.parse(await file.text());
      const draft = payload && payload.draft;
      if (payload.schema !== "janavani.local-draft.v1" || !draft ||
          typeof draft.narrative !== "string" || draft.narrative.length > 20000 ||
          typeof draft.case_id !== "string") {
        throw new Error("This file is not a supported JANAVANI local draft.");
      }
      const importedId = newLocalId();
      await window.JanavaniLocalVault.saveDraft(scope, {
        case_id: importedId,
        server_case_id: "",
        subject: String(draft.subject || "Imported civic draft"),
        narrative: draft.narrative
      });
      caseId = importedId;
      field.value = draft.narrative;
      await refreshDraftList(importedId);
      setStatus("Draft imported into this browser. Review it before creating a Case.");
    } catch (error) {
      setStatus("Import failed. " + error.message);
    } finally {
      event.target.value = "";
    }
  });
  document.getElementById("export-local-draft").addEventListener("click", async () => {
    try {
      if (!(await checkAccountScope())) return;
      await pendingSave;
      await save();
      const draft = await window.JanavaniLocalVault.getDraft(scope, caseId);
      const blob = new Blob([JSON.stringify({
        schema: "janavani.local-draft.v1",
        exported_at: new Date().toISOString(),
        draft: {
          case_id: draft.case_id,
          subject: draft.subject,
          narrative: draft.narrative
        }
      }, null, 2)], {type: "application/json"});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "janavani-local-draft-" + caseId + ".json";
      link.click();
      setTimeout(() => URL.revokeObjectURL(url), 0);
      setStatus("A copy of your local draft was exported. Keep it somewhere safe.");
    } catch (error) {
      setStatus("Export failed. Your local draft remains unchanged. " + error.message);
    }
  });
  document.getElementById("clear-local-drafts").addEventListener("click", async () => {
    if (!(await checkAccountScope())) return;
    if (!window.confirm("Permanently clear all JANAVANI local drafts for this signed-in account from this browser? This cannot be undone.")) return;
    try {
      await pendingSave;
      await window.JanavaniLocalVault.clearScope(scope);
      field.value = "";
      caseId = "local-" + (window.crypto && crypto.randomUUID
        ? crypto.randomUUID() : Date.now().toString(36) + Math.random().toString(36).slice(2));
      await refreshDraftList();
      setStatus("Local drafts for this account were cleared from this browser.");
    } catch (error) {
      setStatus("Could not clear local drafts. " + error.message);
    }
  });
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      if (!(await checkAccountScope())) throw new Error("Sign in again before creating a Case.");
      await pendingSave;
      await save();
      const requestScope = scope;
      const requestCaseId = caseId;
      const requestNarrative = field.value;
      const response = await fetch("/submit-issue", {
        method: "POST",
        credentials: "same-origin",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body: new URLSearchParams({
          case_type: "complaint",
          local_draft_id: requestCaseId,
          local_vault_scope: requestScope
        })
      });
      if (!response.ok) throw new Error("Could not create the Case shell.");
      const created = await response.json();
      // Associate the metadata shell only with the exact local account/draft
      // that initiated this request, even if the browser account changed in flight.
      await window.JanavaniLocalVault.saveDraft(requestScope, {
        case_id: requestCaseId, server_case_id: created.case_id,
        subject: "Civic complaint", narrative: requestNarrative
      });
      const currentScope = await window.JanavaniLocalVault.resolveScope().catch(() => null);
      if (currentScope !== requestScope) {
        await checkAccountScope();
        setStatus("A Case shell was created for the account active when you requested it. Sign into that account to see its local association; no draft was copied into this account.");
        return;
      }
      if (scope !== requestScope || caseId !== requestCaseId) {
        await restoreForScope(currentScope);
        setStatus("Case shell created for the earlier draft. Reopen that draft to see its Case association.");
        return;
      }
      setStatus("Case " + created.case_id + " created. Your complaint remains in this browser; only Case metadata was sent.");
    } catch (error) {
      setStatus("Case not created or linked. Your local draft remains in this browser. " + error.message);
    }
  });
})();
