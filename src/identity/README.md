# Janavani Identity Boundary

This package is the shared identity context boundary for all Janavani interfaces.

## Rule

Adapters resolve their channel-specific caller information into a normalized `Principal`. The identity package does **not** decide authorization, consent, or capability execution.

```text
Interface / Adapter
        ↓
Principal / IdentityContext
        ↓
Authorization policy
        ↓
Capability
```

## Current implementation

- Supports anonymous, local, authenticated, and cryptographic identity modes.
- Supports explicit authentication-method metadata without implementing a provider.
- Uses opaque principal IDs.
- Keeps session identity separate from conversation workflow state.
- Provides an anonymous-context helper for capabilities that do not require authentication.

## Security boundary

Do not place passwords, access tokens, refresh tokens, API keys, private keys, phone numbers, email addresses, or other secrets/PII into `Principal`.

Provider adapters and secure credential/session services will be added behind this boundary in later phases.
