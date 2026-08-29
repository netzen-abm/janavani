import { describe, expect, it } from "vitest";
import { EncryptedCaseRepository } from "./encrypted_case_repository.js";
import { IndexedDbLocalVault, createVaultKey } from "./local_vault.js";

describe("EncryptedCaseRepository", () => {
  it("creates, reads, lists, updates, and deletes a case through the vault", async () => {
    const key = await createVaultKey();
    const repository = new EncryptedCaseRepository(new IndexedDbLocalVault(key));
    const created = await repository.create({
      title: "Streetlight not working",
      description: "The streetlight has been off for three nights.",
      location: "Public road",
      category: "Infrastructure",
    });

    expect(created.id).toBeTruthy();
    expect(await repository.get(created.id)).toEqual(created);
    expect(await repository.list()).toEqual([created]);

    const updated = await repository.updateStatus(created.id, "ready_for_review");
    expect(updated.status).toBe("ready_for_review");

    expect(await repository.delete(created.id)).toBe(true);
    expect(await repository.get(created.id)).toBeNull();
  });
});
