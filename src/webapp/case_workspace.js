import { createWorkflowState, attachEvidence, chooseAuthority, attachDocument, approveWorkflow, attachReceipt, attachTracking } from "./civic_workflow.js";

/** Thin UI/controller boundary over shared capabilities. */
export class CaseWorkspace {
  constructor({ caseRepository, evidenceStore, authorityDirectory, documentProvider, submissionProvider, trackingStore, workflowStore }) {
    Object.assign(this, { caseRepository, evidenceStore, authorityDirectory, documentProvider, submissionProvider, trackingStore, workflowStore });
    this.state = null;
  }

  async start(caseRecord) {
    this.state = createWorkflowState(caseRecord);
    await this.caseRepository.save(caseRecord);
    await this.persist();
    return this.state;
  }

  async resume(caseId) {
    if (!this.workflowStore) throw new Error("Workflow persistence is unavailable");
    this.state = await this.workflowStore.load(caseId);
    if (!this.state) throw new Error("No saved workflow exists for this Case");
    return this.state;
  }

  async persist() {
    if (!this.workflowStore) throw new Error("Workflow persistence is unavailable");
    await this.workflowStore.save(this.state);
    return this.state;
  }

  async addEvidence(evidence) { this.state = attachEvidence(this.state, evidence); return this.persist(); }
  async findAuthorities(query) { if (!this.authorityDirectory) throw new Error("Authority discovery is unavailable"); return this.authorityDirectory.discover(query); }
  async selectAuthority(authority) { this.state = chooseAuthority(this.state, authority); return this.persist(); }
  async setDocument(document) { this.state = attachDocument(this.state, document); return this.persist(); }
  async approve(document) {
    const approved = document?.status === "approved" ? document : { ...this.state.document, ...document, status: "approved" };
    this.state = approveWorkflow({ ...this.state, document: approved });
    return this.persist();
  }
  async submit(draft, options = {}) {
    if (!this.submissionProvider) throw new Error("Submission is unavailable");
    const { buildSubmissionPayload } = await import("./submission.js");
    const payload = buildSubmissionPayload(draft, options);
    const receipt = await this.submissionProvider.submit(payload);
    this.state = attachReceipt(this.state, receipt);
    await this.persist();
    return { state: this.state, receipt };
  }
  async track(trackingRecord) {
    await this.trackingStore.save(trackingRecord);
    this.state = attachTracking(this.state, trackingRecord);
    await this.persist();
    return this.state;
  }
}
