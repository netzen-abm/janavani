# Shared Capability Infrastructure Principle

## Non-negotiable rule

Every capability or feature built in Janavani must be designed as reusable shared infrastructure first. A WebApp screen, Telegram flow, mobile client, WhatsApp interface, DApp, or future access surface must consume the same capability contracts rather than reimplementing business logic.

## Architecture

```text
                    JANAVANI CAPABILITY FABRIC
                              |
          +-------------------+-------------------+
          |                   |                   |
        CASE              EVIDENCE            AUTHORITY
          |                   |                   |
      DOCUMENT           SUBMISSION           KNOWLEDGE
          |                   |                   |
          +-------------------+-------------------+
                              |
                  PRIVACY / SAFETY CONTROL PLANE
                              |
                 PROVIDER / ADAPTER BOUNDARY
                              |
       +-----------+----------+-----------+-----------+
       |           |                      |           |
     Local      Cloud              Decentralized    Future
     Provider  Provider              Provider      Provider
       |           |                      |
       +-----------+----------------------+-----------+
                              |
                      ACCESS SURFACES
         Web | Mobile | Telegram | WhatsApp | DApp | Future
```

## Design requirements

1. Capability contracts are channel-neutral.
2. Business rules live in shared services/domain layers, never in a client.
3. Providers are adapters behind stable interfaces.
4. User choice controls invocation, not whether the platform contains the capability.
5. Privacy and safety policies apply before provider selection.
6. Personal data remains on the user's device by default and is never sent to AI/Agentic AI.
7. New infrastructure must be attachable without rewriting existing access surfaces.
8. A capability must be testable independently of its UI and provider.
9. Versioned contracts must support future clients and provider replacement.
10. Shared capabilities should be documented as reusable ecosystem primitives.

## Definition of done for a new capability

A feature is not considered platform-complete merely because a WebApp screen works. It must have:

- a domain/contract boundary;
- a provider-neutral service interface;
- policy/privacy enforcement;
- independent automated tests;
- an adapter point for future providers;
- an access-surface integration;
- documentation describing reuse by future clients;
- migration/versioning considerations.

## Future compatibility

Freenet, Nostr, IPFS, local-first storage, AI providers, Agentic AI providers, identity providers, messaging channels, and future technologies must enter through adapter/provider contracts. The WebApp must discover and consume capabilities rather than hard-code technology-specific implementations.
