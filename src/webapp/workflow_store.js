import { WORKFLOW_STATES } from "./civic_workflow.js";

const NAMESPACE = "workflow";

/** Stores only workflow references/state; underlying Case/Evidence remain in their own namespaces. */
export class LocalWorkflowStore {
  constructor(vault) { this.vault = vault; }

  async save(state) {
    if (!state?.case_id) throw new Error("Workflow case_id is required");
    await this.vault.put(NAMESPACE, state.case_id, {
      version: 1,
      case_id: state.case_id,
      state: state.state,
      evidence: state.evidence ?? [],
      authority: state.authority ?? null,
      document: state.document ?? null,
      receipt: state.receipt ?? null,
      tracking: state.tracking ?? null,
      updated_at: new Date().toISOString(),
    });
    return state;
  }

  async load(caseId) {
    const state = await this.vault.get(NAMESPACE, caseId);
    return state ? { ...state, version: 1 } : null;
  }

  async remove(caseId) { return this.vault.remove(NAMESPACE, caseId); }

  static isTerminal(state) {
    return state?.state === WORKFLOW_STATES.TRACKING;
  }
}
