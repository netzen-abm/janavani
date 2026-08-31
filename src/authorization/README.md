# Janavani Authorization Boundary

Authorization is a shared policy boundary between normalized identity and capability execution.

```text
Interface / Adapter
        ↓
Principal / IdentityContext
        ↓
AuthorizationPolicy
        ↓
Capability
```

## Rules

- Deny by default.
- A capability may explicitly permit anonymous access.
- Otherwise the normalized principal must hold the capability.
- Authorization does not authenticate callers.
- Authorization does not grant consent.
- Provider credentials are not authorization state.
- Capability names are stable contracts; providers and interfaces remain replaceable.

This package is intentionally small so every Janavani surface can use the same policy boundary.
