# Local Vault — Web Implementation Boundary

## Purpose

Janavani personal Case state is local-first. The Python platform defines the
contract; the Web client owns the actual browser persistence and cryptographic
keys.

## Required Web implementation

```text
Web Case state
    ↓
Web Crypto API
    ↓
AES-GCM encryption
    ↓
IndexedDB
```

The browser implementation must:

- generate or obtain encryption keys without sending key material to Janavani;
- encrypt Case/Evidence state before persistence;
- store only encrypted envelopes in IndexedDB;
- keep decryption inside the trusted client boundary;
- reject plaintext records;
- support delete and export/recovery planning;
- make key loss a visible recovery state rather than silently resetting data.

## Server boundary

The backend must treat encrypted envelopes as opaque. It must not accept a
browser key, decrypt a Case, or require remote persistence for local-first
operation.

## Production gate

The local vault is not production-complete until Web Crypto implementation,
key lifecycle, IndexedDB persistence, migration, export/recovery, multi-device
behavior, cryptographic test vectors, and threat-model testing are verified.
