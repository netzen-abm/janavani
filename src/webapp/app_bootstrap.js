import { BrowserDeviceKeyProvider } from "./device_key_provider.js";
import { IndexedDbLocalVault } from "./local_vault.js";
import { LocalVaultCaseRepository } from "./case_repository.js";
import { LocalEvidenceStore } from "./evidence_store.js";

/**
 * Shared WebApp bootstrap. All local capabilities receive the same vault key
 * for the active device session. No capability creates its own key.
 */
export async function createWebAppContext({ passphrase, mode = "unlock" } = {}) {
  const keyProvider = new BrowserDeviceKeyProvider();
  const key = mode === "create"
    ? await keyProvider.create(passphrase)
    : await keyProvider.unlock(passphrase);
  const vault = new IndexedDbLocalVault(key);
  return Object.freeze({
    keyProvider,
    vault,
    caseRepository: new LocalVaultCaseRepository(vault),
    evidenceStore: new LocalEvidenceStore(vault),
  });
}
