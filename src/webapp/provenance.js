/**
 * Channel-neutral provenance for Case/Evidence artifacts.
 * Provenance is metadata only; it never contains raw attachment bytes.
 */
export const PROVENANCE_SCHEMA_VERSION = 1;

const EVENTS = new Set(["created", "captured", "imported", "transformed", "hashed", "reviewed", "shared", "deleted"]);

export function createProvenanceEvent({ artifact_id, event, occurred_at, actor = "user", source = "device", details = {} }) {
  if (!artifact_id) throw new Error("Artifact id is required");
  if (!EVENTS.has(event)) throw new Error("Unsupported provenance event");
  return {
    schema_version: PROVENANCE_SCHEMA_VERSION,
    id: crypto.randomUUID(),
    artifact_id,
    event,
    occurred_at: occurred_at ?? new Date().toISOString(),
    actor,
    source,
    details: sanitizeDetails(details),
  };
}

function sanitizeDetails(details) {
  if (!details || typeof details !== "object") return {};
  const allowed = ["content_hash", "media_type", "size", "provider", "provider_version", "transformation"];
  return Object.fromEntries(allowed.filter((key) => Object.hasOwn(details, key)).map((key) => [key, details[key]]));
}

export class LocalProvenanceStore {
  constructor(vault) { this.vault = vault; }
  async append(event) {
    const record = createProvenanceEvent(event);
    await this.vault.put("provenance", record.id, record);
    return record;
  }
  async listForArtifact(artifactId) {
    return (await this.vault.list("provenance")).filter((item) => item.artifact_id === artifactId);
  }
}
