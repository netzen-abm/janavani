# Janavani Session & Token Lifecycle

## Design

Janavani uses opaque, short-lived session tokens for authenticated sessions where persistent authentication is genuinely required. The session token is not the citizen's identity.

```text
Authentication event
        ↓
opaque session token generated
        ↓
only token hash retained server-side
        ↓
request presents session ID + token
        ↓
hash + expiry + revocation validation
        ↓
Principal / IdentityContext
        ↓
AuthorizationPolicy
```

## Rules

- Default access remains anonymous where a capability permits it.
- Session tokens are short-lived by default.
- Raw tokens are returned only to the caller that creates the session.
- Server-side storage retains only a cryptographic hash of the token.
- Token comparison uses constant-time comparison.
- Expired and revoked sessions fail closed.
- Session credentials are never put into workflow state or ordinary logs.
- Session identity is represented in `Principal` only through opaque IDs and metadata.
- Authentication does not grant consent.
- Authentication does not grant unrelated capabilities.

## Production storage

The current implementation uses an in-memory registry as a safe lifecycle reference implementation. Before production, replace the storage mechanism with a managed secure session store and add concurrency, persistence, eviction, rotation, CSRF protection where cookie sessions are used, and operational revocation controls.

The `Principal` contract should remain unchanged.

## Provider neutrality

Passkey, OIDC, verified challenges, and cryptographic authentication are upstream authentication mechanisms. They should all converge into the same session/Principal boundary rather than creating separate downstream authorization models.
