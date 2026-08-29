import { rankAuthorityCandidates } from "./authority_ranking.js";
import { createProvenanceEvent } from "./provenance.js";

export const AUTHORITY_STATES = Object.freeze({ CANDIDATE: "candidate", VERIFIED: "verified", SELECTED: "selected", USED: "used" });

export function resolveAuthorities(candidates, context = {}) {
  const ranked = rankAuthorityCandidates(candidates, context);
  return ranked.map((candidate) => ({
    ...candidate,
    state: AUTHORITY_STATES.CANDIDATE,
    verification: { status: "unverified", verified_at: null, basis: null },
  }));
}

export function verifyAuthority(candidate, { basis, verifiedAt = new Date().toISOString() } = {}) {
  if (!candidate?.id) throw new Error("Authority candidate is required");
  if (!basis) throw new Error("Verification basis is required");
  return {
    ...candidate,
    state: AUTHORITY_STATES.VERIFIED,
    verification: { status: "verified", verified_at: verifiedAt, basis: String(basis).slice(0, 500) },
  };
}

export function selectAuthority(candidate, caseId) {
  if (candidate?.state !== AUTHORITY_STATES.VERIFIED) throw new Error("Only verified authorities can be selected");
  if (!caseId) throw new Error("Case id is required");
  return { ...candidate, state: AUTHORITY_STATES.SELECTED, case_id: caseId };
}

export function markAuthorityUsed(candidate) {
  if (candidate?.state !== AUTHORITY_STATES.SELECTED) throw new Error("Only selected authorities can be marked used");
  return { ...candidate, state: AUTHORITY_STATES.USED };
}

export function authorityProvenance(candidate, event, details = {}) {
  return createProvenanceEvent({ artifact_id: candidate.id, event, source: "authority-directory", details });
}
