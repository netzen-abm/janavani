/** Deterministic, explainable ranking for public authority candidates. */
export const AUTHORITY_RANKING_VERSION = 1;
const MAX_FRESHNESS_DAYS = 90;

function daysSince(value, now = Date.now()) {
  const time = Date.parse(value);
  return Number.isFinite(time) ? Math.max(0, (now - time) / 86400000) : Infinity;
}

export function scoreAuthorityCandidate(candidate, { jurisdiction = null, authority_type = null, now = Date.now() } = {}) {
  const freshnessDays = daysSince(candidate.retrieved_at, now);
  const jurisdictionMatch = jurisdiction && candidate.jurisdiction === jurisdiction ? 1 : 0;
  const typeMatch = authority_type && candidate.authority_type === authority_type ? 1 : 0;
  const freshness = Number.isFinite(freshnessDays) ? Math.max(0, 1 - freshnessDays / MAX_FRESHNESS_DAYS) : 0;
  const sourceBonus = candidate.source_url ? 0.1 : 0;
  const providerConfidence = candidate.confidence ?? 0;
  const score = (jurisdictionMatch * 0.4) + (typeMatch * 0.15) + (freshness * 0.2) + (providerConfidence * 0.2) + sourceBonus;
  return { ...candidate, ranking_version: AUTHORITY_RANKING_VERSION, freshness_days: freshnessDays, ranking_score: Number(score.toFixed(6)) };
}

export function rankAuthorityCandidates(candidates, context = {}) {
  return [...candidates].map((candidate) => scoreAuthorityCandidate(candidate, context))
    .sort((a, b) => b.ranking_score - a.ranking_score || a.name.localeCompare(b.name));
}
