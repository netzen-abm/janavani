import { createVaultKey, IndexedDbLocalVault } from "./local_vault.js";
import { LocalVaultCaseRepository } from "./case_repository.js";
import { LocalEvidenceStore } from "./evidence_store.js";

/**
 * Creates one client-session vault and injects it into all local capabilities.
 * A future durable DeviceKeyProvider can replace createVaultKey without
 * changing Case/Evidence consumers.
 */
export async function createWebAppContext() {
  const key = await createVaultKey();
  const vault = new IndexedDbLocalVault(key);
  return Object.freeze({
    vault,
    caseRepository: new LocalVaultCaseRepository(vault),
    evidenceStore: new LocalEvidenceStore(vault),
  });
}
