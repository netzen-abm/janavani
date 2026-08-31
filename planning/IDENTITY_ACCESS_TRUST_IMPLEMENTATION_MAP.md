# JANAVANI — IDENTITY, ACCESS & TRUST IMPLEMENTATION MAP

**Status:** AUDITED / IMPLEMENTATION PLAN
**Date:** 31 August 2026

## 1. Audit result

The current repository has conversation/session state but does not yet expose a verified shared citizen authentication and authorization layer.

`src/conversation/session.py` currently maintains in-memory `user_sessions` keyed by `user_id`, including workflow data and identity fields such as `identity_mode`, `name`, `address`, `phone`, and `email`. It also contains a duplicate `get_session` definition and states that storage may later move to Supabase.

`src/bot_telegram.py` authenticates the Janavani application to Telegram with `Config.TELEGRAM_BOT_TOKEN`, then routes Telegram commands/messages into the conversation system. This is integration authentication, not citizen authentication.

## 2. Current versus target

| Boundary | Current | Target |
|---|---|---|
| Interface identity | Channel-provided context | Normalized principal context |
| Anonymous use | Partly represented | Explicit supported identity mode |
| Local identity | Session fields | Device/local identity vault |
| Citizen authentication | Not verified | Shared authentication adapters |
| Authorization | Not verified | Shared policy engine/middleware |
| Capability permission | Not verified | Capability-scoped policy |
| Consent | Workflow-specific/implicit areas | Explicit consent records/gates |
| Sessions | In-memory conversation state | Secure auth sessions separated from workflow state |
| Tokens | Service credentials only | Short-lived access + revocable session credentials where needed |
| Service secrets | Environment configuration | Secret-manager/deployment protected configuration |
| Crypto identity | Environment-configured capabilities | Explicit key ownership and signing boundary |
| Audit/provenance | Not verified as auth audit | Minimized security/provenance events |

## 3. Required separation

Do not turn `conversation/session.py` into the authentication system.

Conversation state answers:

> What is happening in this workflow?

Identity/access state answers:

> Who or what is making this request, how was it authenticated, what may it do, and what approval has been given?

These must remain separate.

## 4. Proposed shared boundary

```text
src/
  identity/
    models.py
    principal.py
    modes.py

  auth/
    service.py
    authenticators/
    sessions.py
    tokens.py

  access/
    policy.py
    authorization.py
    capability_permissions.py
    consent.py

  trust/
    provenance.py
    audit.py
    destinations.py

  security/
    secrets.py
    key_policy.py
    revocation.py
    recovery.py
```

The exact package layout can change after implementation inspection. The architectural boundary must not.

## 5. Principal model

Every request should resolve to a normalized principal context such as:

```text
principal_id
identity_mode
interface
session_id (if authenticated)
authentication_method (if authenticated)
scopes
capabilities
consent_context
risk_context
```

Anonymous principals should not be converted into permanent personal profiles merely to satisfy this model.

## 6. Telegram adapter

Telegram should map the platform's verified channel identity into a Janavani request context without treating the Telegram bot token as the citizen's credential.

Conceptually:

```text
Telegram update
    ↓
Telegram adapter
    ↓
channel principal/context
    ↓
shared capability authorization
    ↓
conversation/workflow engine
```

The bot token remains a service credential used by Janavani to call Telegram.

## 7. Workflow session separation

Current workflow state contains identity fields. During implementation, decide whether those fields are:

- ephemeral workflow inputs;
- local identity references;
- authenticated profile attributes;
- or data destined for an external submission.

They must not automatically become a centralized persistent citizen profile.

## 8. Authorization point

The canonical API assembly boundary and interface adapters should invoke one shared authorization boundary before protected capabilities execute.

Authorization must be evaluated using capability/action/resource context, not only a boolean `authenticated` flag.

## 9. High-risk actions

The following should require explicit approval and appropriate authorization:

- transmitting personal information;
- submitting a document to an external authority;
- publishing evidence publicly;
- signing blockchain transactions;
- sending through an external messaging service;
- invoking an agent with consequential external tools;
- changing security/account recovery settings.

## 10. Implementation order

### Phase A — boundary extraction

1. Preserve current conversation behaviour.
2. Introduce principal/request-context abstractions.
3. Separate workflow session state from identity/access state.
4. Define authorization policy interfaces.

### Phase B — authentication

1. Implement anonymous principal support.
2. Implement a passwordless authenticated mechanism only where a real capability requires it.
3. Implement secure session lifecycle.
4. Implement token validation/rotation/revocation where tokens are actually required.

### Phase C — capability authorization

1. Protect selected Web/API capabilities.
2. Add capability-scoped permissions.
3. Add consent/approval gates.
4. Add external-destination authorization.

### Phase D — cross-interface adapters

1. Web adapter.
2. Telegram adapter.
3. Android/iOS adapters.
4. WhatsApp/Messenger adapters.
5. API/DApp adapters.

Each adapter remains independently operable.

### Phase E — verification

Test both success and denial paths, including expired credentials, revoked sessions, wrong audience/scope, missing consent, anonymous access, cross-interface isolation, and external-destination denial.

## 11. Do not implement yet

Do not add a generic JWT login simply because JWT is familiar.

Do not add a mandatory account wall.

Do not centralize Telegram, Web, mobile and messaging identities into one personal-data table without a demonstrated requirement and privacy review.

Do not store access tokens or private keys in conversation state.

Do not claim the feature is production-ready until security and privacy verification evidence exists.

## 12. Acceptance evidence

The implementation is complete only when code, tests and deployment evidence demonstrate:

- anonymous capability access where intended;
- authenticated access where required;
- authorization denial for insufficient privilege;
- capability permission isolation;
- explicit consent for consequential transmission;
- secure session expiry/revocation;
- service credential isolation;
- no secret leakage into logs/client bundles;
- cross-interface independence;
- privacy-preserving identity handling;
- documented recovery behaviour.
