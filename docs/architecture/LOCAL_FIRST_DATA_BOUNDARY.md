# Janavani Local-First Data Boundary

## Non-negotiable invariant

Citizen personal data is owned and retained on the user's device by default. No AI or Agentic AI provider may receive personal data.

## Boundary model

```text
User device
  -> local encrypted vault
  -> capability-specific minimization
  -> explicit policy/consent
  -> opaque encrypted envelope only when remote transport is required
  -> provider adapter
```

## Rules

1. Device-held keys never enter server/API/provider payloads.
2. Remote services receive only the minimum data required for the declared purpose.
3. AI/Agentic AI receives non-personal, allow-listed, sanitized context only.
4. Encryption is not a license to transmit personal data to AI; ciphertext containing personal data remains prohibited for AI/agent providers.
5. Providers must not be able to infer or reconstruct a user's identity from Janavani metadata where avoidable.
6. Capability failure must not force personal-data upload.
7. Local-only operation remains a valid path for critical workflows.
8. Any future decentralized provider (Freenet, Nostr, IPFS, etc.) enters through an adapter and this same policy boundary.

## Implementation status

The current `EncryptedEnvelope` is a transport contract, not a complete cryptographic implementation. Production cryptography, key lifecycle, device recovery, secure storage, and platform-specific implementations must be completed and independently tested before production claims.
