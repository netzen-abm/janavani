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
