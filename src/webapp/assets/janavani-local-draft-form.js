(() => {
  const form = document.getElementById("local-case-draft-form");
  const field = document.getElementById("citizen-input");
  const status = document.getElementById("local-vault-status");
  if (!form || !field || !window.JanavaniLocalVault) return;
  let scope = null;
  let caseId = null;
  let pendingSave = Promise.resolve();
  field.disabled = true;
  const setStatus = (message) => { status.textContent = message; };
  const draftList = document.getElementById("local-draft-list");
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
  const save = async () => {
    if (!scope || !caseId) return;
    await window.JanavaniLocalVault.saveDraft(scope, {
      case_id: caseId, subject: "Civic complaint", narrative: field.value
    });
    setStatus("Draft saved in this browser. It is not a server backup.");
  };
  (async () => {
    try {
      scope = await window.JanavaniLocalVault.resolveScope();
      caseId = "local-" + (window.crypto && crypto.randomUUID
        ? crypto.randomUUID() : Date.now().toString(36) + Math.random().toString(36).slice(2));
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
    } catch (error) {
      field.disabled = true;
      setStatus("Local draft storage is unavailable. No content will be sent. " + error.message);
    }
  })();
  field.addEventListener("input", () => {
    pendingSave = pendingSave.then(save).catch(error => {
      setStatus("Local save failed. Do not navigate away. " + error.message);
    });
  });
  document.getElementById("open-local-draft").addEventListener("click", async () => {
    try {
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
    const selectedId = draftList.value;
    if (!selectedId || !window.confirm("Delete this local draft from this browser? This cannot be undone.")) return;
    try {
      await window.JanavaniLocalVault.deleteDraft(scope, selectedId);
      if (caseId === selectedId) {
        caseId = "local-" + crypto.randomUUID();
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
      const payload = JSON.parse(await file.text());
      const draft = payload && payload.draft;
      if (payload.schema !== "janavani.local-draft.v1" || !draft ||
          typeof draft.narrative !== "string" || typeof draft.case_id !== "string") {
        throw new Error("This file is not a supported JANAVANI local draft.");
      }
      const importedId = "local-" + crypto.randomUUID();
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
      await pendingSave;
      await save();
      const draft = await window.JanavaniLocalVault.getDraft(scope, caseId);
      const blob = new Blob([JSON.stringify({
        schema: "janavani.local-draft.v1",
        exported_at: new Date().toISOString(),
        draft
      }, null, 2)], {type: "application/json"});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "janavani-local-draft-" + caseId + ".json";
      link.click();
      URL.revokeObjectURL(url);
      setStatus("A copy of your local draft was exported. Keep it somewhere safe.");
    } catch (error) {
      setStatus("Export failed. Your local draft remains unchanged. " + error.message);
    }
  });
  document.getElementById("clear-local-drafts").addEventListener("click", async () => {
    if (!window.confirm("Permanently clear all JANAVANI local drafts for this signed-in account from this browser? This cannot be undone.")) return;
    try {
      await window.JanavaniLocalVault.clearScope(scope);
      field.value = "";
      caseId = "local-" + (window.crypto && crypto.randomUUID
        ? crypto.randomUUID() : Date.now().toString(36) + Math.random().toString(36).slice(2));
      setStatus("Local drafts for this account were cleared from this browser.");
    } catch (error) {
      setStatus("Could not clear local drafts. " + error.message);
    }
  });
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    try {
      if (!scope) throw new Error("Sign in and verify local storage before continuing.");
      await pendingSave;
      await save();
      const response = await fetch("/submit-issue", {
        method: "POST",
        credentials: "same-origin",
        headers: {"Content-Type": "application/x-www-form-urlencoded"},
        body: new URLSearchParams({
          case_type: "complaint",
          local_draft_id: caseId
        })
      });
      if (!response.ok) throw new Error("Could not create the Case shell.");
      const created = await response.json();
      await window.JanavaniLocalVault.saveDraft(scope, {
        case_id: caseId, server_case_id: created.case_id,
        subject: "Civic complaint", narrative: field.value
      });
      setStatus("Case " + created.case_id + " created. Your complaint remains in this browser; only Case metadata was sent.");
    } catch (error) {
      setStatus("Case not created. Your local draft remains in this browser. " + error.message);
    }
  });
})();
