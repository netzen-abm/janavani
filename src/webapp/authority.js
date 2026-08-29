/**
 * Provider-neutral Authority Discovery capability.
 * Providers return public authority candidates; the capability normalizes and
 * ranks them without requiring personal citizen data.
 */
export const AUTHORITY_SCHEMA_VERSION = 1;

export class AuthorityProvider {
  async discover(_query) { throw new Error("AuthorityProvider.discover is not implemented"); }
}

export function normalizeAuthorityCandidate(candidate) {
  if (!candidate?.id || !candidate?.name) throw new Error("Authority candidate id and name are required");
  return {
    schema_version: AUTHORITY_SCHEMA_VERSION,
    id: String(candidate.id),
    name: String(candidate.name).slice(0, 300),
    jurisdiction: candidate.jurisdiction ? String(candidate.jurisdiction).slice(0, 300) : null,
    authority_type: candidate.authority_type ? String(candidate.authority_type).slice(0, 100) : null,
    source: candidate.source ? String(candidate.source).slice(0, 500) : null,
    source_url: candidate.source_url ? String(candidate.source_url).slice(0, 2000) : null,
    retrieved_at: candidate.retrieved_at ?? new Date().toISOString(),
    confidence: Number.isFinite(candidate.confidence) ? Math.max(0, Math.min(1, candidate.confidence)) : null,
  };
}

export class AuthorityDirectory {
  constructor(providers = []) { this.providers = [...providers]; }
  register(provider) {
    if (!provider || typeof provider.discover !== "function") throw new Error("Invalid AuthorityProvider");
    this.providers.push(provider);
    return this;
  }
  async discover(query) {
    if (!query || typeof query !== "object") throw new Error("Authority discovery query is required");
    const results = await Promise.all(this.providers.map(async (provider) => provider.discover(query)));
    return results.flat().map(normalizeAuthorityCandidate).sort((a, b) => (b.confidence ?? -1) - (a.confidence ?? -1));
  }
}
