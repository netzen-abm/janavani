import { describe, expect, it } from "vitest";
import { IndexedDbLocalVault, createVaultKey, decryptValue, encryptValue } from "./local_vault.js";

describe("WebApp local vault crypto boundary", () => {
  it("encrypts and decrypts a value without plaintext in the envelope", async () => {
    const key = await createVaultKey();
    const value = { id: "case-1", title: "Broken streetlight" };
    const envelope = await encryptValue(value, key);

    expect(envelope.algorithm).toBe("AES-GCM");
    expect(envelope.ciphertext).not.toContain("Broken streetlight");
    await expect(decryptValue(envelope, key)).resolves.toEqual(value);
  });

  it("rejects an unsupported envelope", async () => {
    const key = await createVaultKey();
    await expect(decryptValue({ version: 2, algorithm: "AES-GCM", iv: "", ciphertext: "" }, key))
      .rejects.toThrow("Unsupported encrypted envelope");
  });

  it("requires a key for the vault", () => {
    expect(() => new IndexedDbLocalVault(null)).toThrow("A non-null vault key is required");
  });
});
