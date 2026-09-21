# Janavani Security Policy

## Security posture

Janavani is a full citizen-governance ecosystem. Security controls are shared infrastructure, not surface-specific implementations.

Current canonical security flow:

```
Identity
  ↓
Authorization
  ↓
Consent
  ↓
Safety / Privacy
  ↓
Execution Context
  ↓
Capability
  ↓
Provider
  ↓
Truthful Result + Audit Evidence
```

WebApp, Telegram and future surfaces must consume these shared controls and must not create parallel authorization, consent, Case-ownership or protected-data paths.

## Reporting a vulnerability

Do not disclose exploitable security details publicly.

For a vulnerability, open a private security report through the repository's GitHub security reporting mechanism when available. Include:

- affected component/path;
- reproducible steps;
- security impact;
- relevant logs or evidence with secrets and personal data removed;
- whether the issue affects one surface or shared infrastructure.

Do not include passwords, API tokens, private keys, session credentials or unnecessary personal data.

## Security engineering requirements

Changes affecting authentication, authorization, consent, protected data, consequential actions, provider access or deployment boundaries require:

1. content/caller verification;
2. negative security tests where applicable;
3. provenance and audit evidence;
4. CI verification;
5. archive-first handling for retired implementations.

Historical security records under `archive/` are evidence and are not treated as active runtime policy.
