(() => {
  "use strict";
  const form = document.getElementById("draft-form");
  const output = document.getElementById("draft");
  const status = document.getElementById("status");
  const download = document.getElementById("download");
  const print = document.getElementById("print");
  let currentDraft = "";

  const values = () => Object.fromEntries(new FormData(form).entries());
  const labels = {
    complaint: "COMPLAINT REGARDING A PUBLIC SERVICE",
    grievance: "GRIEVANCE REPRESENTATION",
    rti: "APPLICATION UNDER THE RIGHT TO INFORMATION ACT",
    petition: "PETITION / COLLECTIVE REQUEST",
    representation: "REPRESENTATION TO A PUBLIC AUTHORITY"
  };
  const clean = (value) => String(value || "").trim();
  const optional = (label, value) => clean(value) ? label + ": " + clean(value) + "\n" : "";

  function buildDraft(data) {
    const date = new Intl.DateTimeFormat("en-IN", { dateStyle: "long" }).format(new Date());
    const title = labels[data.kind] || labels.complaint;
    const recipient = clean(data.office) || "[Name of competent public authority]";
    const sender = clean(data.name) || "[Your name, if required]";
    const facts = clean(data.facts).replace(/\r/g, "");
    const requested = clean(data.request).replace(/\r/g, "");
    const evidence = clean(data.evidence);
    const contact = clean(data.contact);
    const isRti = data.kind === "rti";
    const opening = isRti
      ? "Please treat this as a request for information under the Right to Information Act, 2005, subject to verification of the appropriate public authority, applicable procedure, fee and any lawful exemptions."
      : "I respectfully submit the following issue for your consideration and request appropriate action within the authority's jurisdiction.";
    return [
      title, "", date, "", "To,", recipient, "[Office address, if known]", "",
      "Subject: " + clean(data.subject), "", "Respected Sir / Madam,", "",
      opening, "", "FACTS AND BACKGROUND", facts, "",
      "ACTION / INFORMATION REQUESTED", requested, "",
      evidence ? "SUPPORTING REFERENCES (as listed by the applicant)\n" + evidence + "\n" : "",
      "I request an acknowledgement or reference number, where the applicable process provides one, and a response in accordance with the relevant rules.",
      "", "Yours faithfully,", "", sender, optional("Contact", contact),
      "", "Applicant's review checklist:", "- Verify the authority and its jurisdiction.",
      "- Check dates, facts, attachments, fees and current legal requirements.",
      "- Remove any unnecessary personal or sensitive information.",
      "- Keep a copy and proof of delivery after you submit it yourself.",
      "", "DRAFT ONLY — not submitted, delivered, or legally validated by Janavani."
    ].filter((line) => line !== null).join("\n");
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    currentDraft = buildDraft(values());
    output.textContent = currentDraft;
    status.textContent = "Draft generated in this browser. Review all details before use.";
    download.disabled = false;
    print.disabled = false;
  });

  form.addEventListener("reset", () => {
    currentDraft = "";
    output.textContent = "JANAVANI — CITIZEN DRAFT\n\nComplete the form and choose “Generate draft”.";
    status.textContent = "Form cleared. Nothing was sent or saved.";
    download.disabled = true;
    print.disabled = true;
  });

  download.addEventListener("click", () => {
    if (!currentDraft) return;
    const blob = new Blob([currentDraft], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "janavani-citizen-draft.txt";
    link.click();
    URL.revokeObjectURL(url);
  });

  print.addEventListener("click", () => {
    if (currentDraft) window.print();
  });
})();
