import { AuthorityProvider, normalizeAuthorityCandidate } from "./authority.js";

/**
 * Provider adapter for a public, non-personal authority directory.
 * The provider receives only civic discovery context; caller-owned Case data
 * must be sanitized before this boundary.
 */
export class PublicAuthorityDirectoryProvider extends AuthorityProvider {
  constructor(fetchDirectory) {
    super();
    if (typeof fetchDirectory !== "function") throw new Error("A public directory fetcher is required");
    this.fetchDirectory = fetchDirectory;
  }

  async discover(query) {
    const safeQuery = {
      issue_type: String(query?.issue_type ?? "").slice(0, 200),
      jurisdiction: String(query?.jurisdiction ?? "").slice(0, 200),
      authority_type: query?.authority_type ? String(query.authority_type).slice(0, 100) : null,
    };
    const candidates = await this.fetchDirectory(safeQuery);
    if (!Array.isArray(candidates)) throw new Error("Authority directory must return an array");
    return candidates.map(normalizeAuthorityCandidate);
  }
}
