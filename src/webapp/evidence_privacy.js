/** Local-only attachment privacy inspection. No bytes are transmitted. */

const SENSITIVE_NAME_HINTS = /(aadhaar|passport|pan|voter|phone|mobile|email|address|dob|date.of.birth|medical|health|bank|account|private|confidential)/i;

export function inspectAttachmentPrivacy(file) {
  if (!(file instanceof File)) throw new Error("A browser File is required");
  const findings = [];
  const name = String(file.name || "");
  if (SENSITIVE_NAME_HINTS.test(name)) findings.push({ code: "sensitive_filename", severity: "high" });
  if (file.size === 0) findings.push({ code: "empty_file", severity: "medium" });
  if (file.type === "application/octet-stream") findings.push({ code: "unknown_media_type", severity: "low" });
  return {
    version: 1,
    inspected_locally: true,
    findings,
    recommendation: findings.some((item) => item.severity === "high")
      ? "Review filename before attaching. Personal identifiers may be exposed if evidence is later shared."
      : "Review evidence before any future sharing.",
  };
}

export async function sha256File(file) {
  if (!(file instanceof File)) throw new Error("A browser File is required");
  const digest = await crypto.subtle.digest("SHA-256", await file.arrayBuffer());
  return `sha256:${[...new Uint8Array(digest)].map((b) => b.toString(16).padStart(2, "0")).join("")}`;
}
