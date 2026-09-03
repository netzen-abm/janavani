# Janavani Protected Capability Request Flow

The first production enforcement boundary is framework-neutral so Web, Telegram, WhatsApp, Android, iOS and future interfaces can converge on the same contract.

```text
Incoming request
      ↓
Interface adapter
      ↓
Resolve service credential (if internal call)
      ↓
Resolve citizen identity (if applicable)
      ↓
IdentityContext / Principal
      ↓
AuthorizationPolicy
      ├── denied → stop
      └── allowed
             ↓
        capability handler
             ↓
        consent policy
             ↓
        side effect / external dispatch
```

## Important distinction

`TELEGRAM_BOT_TOKEN`, web interface tokens, and similar credentials authenticate a **Janavani service/interface** to another Janavani service. They do not authenticate the citizen.

Citizen authentication, when required, must produce a normalized `Principal`. The authorization layer consumes that principal and does not inspect provider-specific tokens.

## Fail-closed requirements

- Missing service credential → reject service call.
- Invalid service credential → reject service call.
- Missing capability grant → deny capability.
- Unknown capability → deny capability.
- Consent is never inferred from authentication.
- Secrets are never placed in identity context or conversation state.
