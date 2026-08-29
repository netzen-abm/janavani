import { createWorkflowState, attachEvidence, chooseAuthority, attachDocument, approveWorkflow, attachReceipt, attachTracking } from "./civic_workflow.js";

/** Thin UI controller over shared capabilities. It owns no persistence. */
export class CaseWorkspace {
  constructor({ caseRepository, evidenceStore, authorityDirectory, documentProvider, submissionProvider, trackingStore }) {
    Object.assign(this, { caseRepository, evidenceStore, authorityDirectory, documentProvider, submissionProvider, trackingStore });
    this.state = null;
  }

  async start(caseRecord) {
    this.state = createWorkflowState(caseRecord);
    await this.caseRepository.save(caseRecord);
    return this.state;
  }

  addEvidence(evidence) { this.state = attachEvidence(this.state, evidence); return this.state; }

  async findAuthorities(query) {
    if (!this.authorityDirectory) throw new Error("Authority discovery is unavailable");
    return this.authorityDirectory.discover(query);
  }

  selectAuthority(authority) { this.state = chooseAuthority(this.state, authority); return this.state; }

  setDocument(document) { this.state = attachDocument(this.state, document); return this.state; }

  approve(document) {
    const approved = document?.status === "approved" ? document : { ...this.state.document, ...document, status: "approved" };
    this.state = { ...this.state, document: approved };
    this.state = approveWorkflow(this.state);
    return this.state;
  }

  async submit(draft, options = {}) {
    if (!this.submissionProvider) throw new Error("Submission is unavailable");
    const { buildSubmissionPayload } = await import("./submission.js");
    const payload = buildSubmissionPayload(draft, options);
    const receipt = await this.submissionProvider.submit(payload);
    this.state = attachReceipt(this.state, receipt);
    return { state: this.state, receipt };
  }

  async track(trackingRecord) {
    await this.trackingStore.save(trackingRecord);
    this.state = attachTracking(this.state, trackingRecord);
    return this.state;
  }
}
