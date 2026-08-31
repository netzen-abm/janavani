# Interface Credential Policy

Janavani interface-to-service credentials are **service credentials**, not citizen identity.

## Required environment variables

- `JANAVANI_WEB_INTERFACE_TOKEN`
- `JANAVANI_TELEGRAM_INTERFACE_TOKEN`

Values must be supplied by the deployment/runtime secret store. They must never be committed to Git, embedded in client-side code, placed in `Principal`, or written to logs.

## Boundary

```text
Citizen identity (optional)
        │
        ▼
Principal / IdentityContext
        │
        ▼
AuthorizationPolicy
        │
        ▼
Capability

Interface service credential ─────► service boundary only
```

The browser must not receive the web service credential. A public web frontend should call a server-side Janavani endpoint that holds the credential at runtime.
