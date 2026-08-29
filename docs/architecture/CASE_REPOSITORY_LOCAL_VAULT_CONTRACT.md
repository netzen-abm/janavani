# Case Repository + Local Vault Contract

## Purpose

The Case domain is shared infrastructure. Access surfaces must depend on a repository contract and must not own persistence logic.

## Canonical boundary

```text
CaseService
   |
   v
CaseRepository
   |
   +-- LocalVault-backed provider (Web)
   +-- Secure native provider (future Android/iOS)
   +-- Test/in-memory provider
   +-- Explicitly approved sync provider (future)
```

## Privacy invariant

Personal Case data is local-first and device-owned. Remote persistence is never an implicit fallback.

AI and Agentic AI providers are a separate boundary and receive only non-personal allow-listed context. An encrypted Case envelope must NOT be sent to an AI/Agent provider merely because it is encrypted.

## Required operations

- create
- get
- list
- update
- delete

All operations must be deterministic and independently testable.

## Provider requirements

A provider must:

1. identify its storage scope;
2. declare whether data remains local or crosses a network boundary;
3. expose failure without silently switching to remote persistence;
4. preserve Case identifiers and schema versioning;
5. support deletion semantics;
6. never expose encryption keys through the repository API.

## Web implementation direction

The Web provider uses IndexedDB for persistence and Web Crypto for encryption. The browser key lifecycle belongs to the client. The server never receives the decryption key.

The implementation must not use `localStorage` for Case content or cryptographic key material.

## Migration rule

The legacy Dioxus v3 storage implementation is not a compatible provider. It uses XOR obfuscation and `localStorage`; it must not be adapted as a secure provider.
