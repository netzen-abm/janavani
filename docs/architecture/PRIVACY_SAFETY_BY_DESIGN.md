# Janavani Privacy & Safety by Design

## Non-negotiable invariants

1. Citizen data remains on the user's device by default.
2. Personal data is never required by the platform merely because a capability exists.
3. If remote processing is genuinely required, only the minimum necessary data may leave the device.
4. Any remotely transmitted payload must be encrypted in transit and protected according to the selected transport/storage contract.
5. Personal data must not be sent to AI, Agentic AI, analytics, decentralized providers, or external APIs by default.
6. No provider may receive raw personal data unless the user explicitly authorizes the specific operation and policy permits it.
7. Capability providers must operate on minimized, purpose-bound data wherever possible.
8. The platform must distinguish public civic facts from citizen personal data.
9. Identity linking across channels is opt-in and must not be inferred from shared identifiers.
10. Deletion, export, correction, and consent withdrawal must be first-class capabilities.
11. AI/agents must not use personal data for training or secondary purposes through Janavani's platform contracts.
12. Consequential external actions require explicit user confirmation.
13. Failure of remote services must not force disclosure of personal data or prevent a privacy-preserving local workflow.
14. Decentralized providers are subject to the same data-minimization and consent rules as centralized providers.

## Architecture

```text
User Device
  |
  +-- Local Case Store (canonical personal state)
  +-- Local Evidence Store
  +-- Local Identity / Consent
  +-- Local Encryption Keys
  |
  +--> Privacy Policy / Data Minimizer
          |
          +--> deterministic/local capability
          |
          +--> encrypted minimized payload
                    |
                    +--> optional provider
                           |
                           +--> AI / Agent
                           +--> Government API
                           +--> Storage
                           +--> Freenet / Nostr / other decentralized provider
```

The server/platform should hold capability state and public/operational civic information where required, not a hidden shadow copy of the citizen's private case.

## Product rule

"Optional" always means optional for the citizen. Janavani itself must retain the full capability. User choice determines invocation and consent, not whether the capability exists in the platform.
