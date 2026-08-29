import { test, expect } from "@playwright/test";
import { clearVault, deleteCase, getCase, listCaseIds, putCase } from "../src/platform/web_vault.js";

test.describe("Janavani local Web vault", () => {
  test.beforeEach(async () => {
    await clearVault();
  });

  test("round-trips a case through encrypted IndexedDB storage", async () => {
    const original = {
      id: "case-001",
      title: "Road repair",
      privateNote: "Sensitive citizen note",
      evidence: [{ id: "e1", kind: "photo", hash: "abc" }],
    };

    await putCase(original.id, original);
    expect(await getCase(original.id)).toEqual(original);
    expect(await listCaseIds()).toEqual([original.id]);
  });

  test("returns null for an unknown case", async () => {
    expect(await getCase("missing")).toBeNull();
  });

  test("deletes a case without affecting another case", async () => {
    await putCase("one", { id: "one", value: 1 });
    await putCase("two", { id: "two", value: 2 });

    await deleteCase("one");

    expect(await getCase("one")).toBeNull();
    expect(await getCase("two")).toEqual({ id: "two", value: 2 });
    expect(await listCaseIds()).toEqual(["two"]);
  });

  test("tampering with ciphertext fails authenticated decryption", async ({ page }) => {
    await page.goto("about:blank");
    await page.evaluate(() => {
      indexedDB.deleteDatabase("janavani-local-vault");
    });
    await page.evaluate(async () => {
      const module = await import("/src/platform/web_vault.js");
      await module.putCase("tamper", { id: "tamper", value: "secret" });
    });

    await page.evaluate(() => new Promise((resolve, reject) => {
      const request = indexedDB.open("janavani-local-vault", 1);
      request.onsuccess = () => {
        const db = request.result;
        const tx = db.transaction("records", "readwrite");
        const store = tx.objectStore("records");
        const get = store.get("case:tamper");
        get.onsuccess = () => {
          const record = get.result;
          const bytes = Uint8Array.from(atob(record.ciphertext), (c) => c.charCodeAt(0));
          bytes[0] ^= 1;
          record.ciphertext = btoa(String.fromCharCode(...bytes));
          store.put(record);
        };
        tx.oncomplete = () => resolve();
        tx.onerror = () => reject(tx.error);
      };
      request.onerror = () => reject(request.error);
    }));

    const result = await page.evaluate(async () => {
      try {
        const module = await import("/src/platform/web_vault.js");
        await module.getCase("tamper");
        return "unexpected-success";
      } catch (_) {
        return "tamper-detected";
      }
    });

    expect(result).toBe("tamper-detected");
  });
});
