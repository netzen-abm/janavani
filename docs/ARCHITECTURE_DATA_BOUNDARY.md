# JanaVani Capability & Data Boundary Contract

## Purpose

This document is the architectural contract for building JanaVani as a full civic ecosystem without creating a central personal-data dependency.

## Core rule

**JanaVani does not store personal data by default.**

The citizen device is the primary personal-data domain. JanaVani infrastructure provides independently deployable capabilities and should receive only the minimum payload required by the capability selected by the user.

## Independence rule

Each capability must have its own interface, state boundary, failure boundary, and permission boundary.

A capability may depend on a shared protocol contract, but it must not depend on another optional capability being online.

Examples:

| Capability | May operate without |
|---|---|
| Web app | Web3, AI, Freenet, messaging |
| Android | iOS, DApp, Telegram, WhatsApp |
| iOS | Android, DApp, Telegram, WhatsApp |
| DApp/Web3 | AI, messaging, conventional backend |
| Freenet | central application server |
| Nostr | Freenet, blockchain |
| Nym | Reticulum, blockchain |
| Reticulum | Nym, conventional Internet |
| AI/LLM/SLM | Web3, messaging |
| OCR/CV | cloud AI where local processing is available |
| Messaging adapter | unrelated messaging adapters |

This is an architectural target. Every implementation must be tested against it.

## Data flow

```text
                    ┌──────────────────────────┐
                    │     Citizen Device       │
                    │                          │
                    │  identity / drafts /     │
                    │  evidence / keys /       │
                    │  preferences             │
                    └────────────┬─────────────┘
                                 │
                     explicit capability choice
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
          Local-only       Encrypted API       Decentralized
          capability          transfer           transport
              │                  │                  │
              ▼                  ▼                  ▼
          device state       selected service   selected protocol

No implicit fan-out.
No cross-capability personal-data replication.
```

## Transmission contract

Before sensitive data leaves the device:

1. identify the selected capability;
2. identify the destination;
3. minimize the payload;
4. show the user what will be transmitted where practical;
5. encrypt the transport;
6. avoid logging the payload;
7. avoid storing the payload beyond the necessary processing window;
8. report failure without blocking unrelated capabilities.

## Identity contract

Identity is optional unless required by the selected action.

Supported modes should include anonymous, pseudonymous/local identity, and explicit full identity. Private keys and wallet seed material remain device-controlled and must never be placed in ordinary server storage.

## AI contract

AI providers are capability adapters, not identity stores.

The architecture must support local SLM/LLM/VLM/OCR/CV processing where feasible. Cloud AI is opt-in and receives only the selected task payload. Provider failure must fall back to another permitted mode or a non-AI workflow rather than disabling the civic application.

## Web3 contract

Web3 is an optional capability layer. Wallets, signatures, blockchain transactions, ZK proofs, and decentralized identity must not be prerequisites for ordinary civic workflows.

## Messaging contract

Telegram, Telegram Mini App, WhatsApp, Messenger, email, and future channels are independent adapters. One channel's outage or policy change must not disable the others or the main application.

## Future protocol contract

New capability families such as Web4/Web5/Web6 or future protocols must be addable as adapters implementing stable JanaVani capability contracts. Core civic domain models must not be rewritten for each new transport.

## Failure isolation

Every capability must expose explicit states such as:

- available;
- unavailable;
- degraded;
- offline;
- permission denied;
- user disabled;
- configuration required.

An unavailable optional capability must never be represented as a failure of the whole JanaVani application.

## No hidden data lake

The following are prohibited as architectural defaults:

- central citizen-profile databases;
- advertising identity graphs;
- cross-channel tracking identifiers;
- unnecessary location histories;
- plaintext personal-data logs;
- silent replication of device data into analytics systems;
- embedding API secrets in client applications.

## Review gate

Any pull request that introduces a new capability or data flow should document:

- capability boundary;
- input data;
- output data;
- local versus remote processing;
- encryption boundary;
- retention boundary;
- failure behavior;
- user opt-in/permission behavior;
- dependencies on other capabilities.
