import { assertEvidenceIsLocal, createEvidence } from "./evidence.js";
import { IndexedDbLocalVault } from "./local_vault.js";

const ATTACHMENT_NAMESPACE = "evidence-attachment";
const MAX_BYTES = 25 * 1024 * 1024;

function requireCrypto() {
  if (!globalThis.crypto?.subtle) throw new Error("Web Crypto API is required");
  return globalThis.crypto;
}

async function sha256Hex(buffer) {
  const digest = await requireCrypto().subtle.digest("SHA-256", buffer);
  return [...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function safeMetadata(file) {
  return {
    name: String(file.name || "attachment").slice(0, 255),
    media_type: String(file.type || "application/octet-stream").slice(0, 100),
    size: Number(file.size),
    last_modified: Number.isFinite(file.lastModified) ? file.lastModified : null,
  };
}

export async function createEncryptedAttachment({ caseId, file, vault }) {
  if (!(vault instanceof IndexedDbLocalVault)) throw new Error("IndexedDbLocalVault is required");
  if (!caseId) throw new Error("Case id is required");
  if (!(file instanceof File)) throw new Error("A browser File is required");
  if (file.size > MAX_BYTES) throw new Error("Attachment exceeds the 25 MB local limit");

  const bytes = await file.arrayBuffer();
  const contentHash = await sha256Hex(bytes);
  const id = crypto.randomUUID();
  const evidence = assertEvidenceIsLocal(createEvidence({
    id,
    case_id: caseId,
    type: file.type.startsWith("image/") ? "photo" : file.type.startsWith("audio/") ? "audio" : file.type.startsWith("video/") ? "video" : "document",
    label: file.name,
    local_ref: `attachment:${id}`,
    content_hash: `sha256:${contentHash}`,
  }));

  await vault.put(ATTACHMENT_NAMESPACE, id, {
    schema_version: 1,
    evidence_id: evidence.id,
    metadata: safeMetadata(file),
    content_hash: `sha256:${contentHash}`,
    bytes,
  });
  return evidence;
}

export async function getEncryptedAttachment(id, vault) {
  return vault.get(ATTACHMENT_NAMESPACE, id);
}

export async function removeEncryptedAttachment(id, vault) {
  await vault.remove(ATTACHMENT_NAMESPACE, id);
}
