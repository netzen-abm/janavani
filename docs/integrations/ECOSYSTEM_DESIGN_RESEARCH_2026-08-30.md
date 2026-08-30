# JanaVani Ecosystem Design Research — 2026-08-30

## Sources reviewed

- InnovatAR `yondar-mono`
- go.yondar.me / Yondar problem-tree concept
- NostrApps catalogue reference supplied by the project
- forms-oriented tooling references supplied by the project
- Shakespeare DIY reference supplied by the project

## Yondar / Problem Tree

Yondar's README points to a Nostr-based Problem Tree and uses a map-centric interface. This is highly relevant as a *research pattern* for structuring citizen problems spatially and hierarchically. The repository uses Mapbox during development. See `innovatario/yondar-mono/README.md`.

### JanaVani use

Consider a future optional shared capability:

Citizen problem → location → problem category → related cases/public context.

Do not copy Yondar's branding, visual identity or proprietary trademarks. The repository code is licensed CC BY-SA 4.0, while Yondar names/logos/trademarks are reserved. See `innovatario/yondar-mono/LICENSE`.

## Nostr

The supplied NostrApps catalogue should be treated as an ecosystem-discovery source only. JanaVani may later expose public, non-sensitive civic outputs through decentralized protocols, but Nostr must not become a dependency of the core case engine.

Potential future shared capability: optional public civic signal/public-interest publication, explicitly separated from the private case workspace.

## Forms tooling

Form-building references may inform a configurable civic form renderer. The reusable capability should be `SchemaDrivenFormRenderer`, not a hard dependency on one external product.

Potential uses: authority selection, structured issue intake, RTI question review, correction/verification forms, evidence metadata forms.

## Shakespeare DIY

Treat as an experimentation/reference source only until its code/licence and concrete reusable components are independently verified. Do not make it a core dependency based on the supplied URL alone.

## Core design rule

External projects provide patterns or adapters. JanaVani's core remains provider-neutral, privacy-first and citizen-participation focused.

No external project is allowed to become the owner of case state, legal decision logic, user identity, or document-delivery policy.
