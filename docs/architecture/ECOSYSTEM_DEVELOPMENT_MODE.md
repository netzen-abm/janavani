# JanaVani — Full Ecosystem Development Mode

**Effective:** 2026-08-30

JanaVani is no longer planned or evaluated as an MVP. Development is for the complete civic-participation ecosystem.

## Planning classes

1. Core Ecosystem — foundational capabilities required by the complete product.
2. Shared Infrastructure — reusable capabilities exposed independently of access channel.
3. Ecosystem Capability — implemented when its dependency and governance layers are ready.
4. Future Extension — architecture and contracts preserved for later implementation.
5. Research / Experimental — evaluated without becoming a production dependency prematurely.

## Mandatory Shared Infrastructure Gate

For every new skill, capability, feature, or function, ask before implementation:

- Can it be reused by more than one access surface or product capability?
- Can its business logic live in the shared core rather than Web/Telegram/etc.?
- Can it expose a stable contract/provider interface?
- Can implementations remain replaceable?
- Can privacy, provenance, authorization, and safety boundaries be enforced centrally?

If yes, design it as shared infrastructure unless there is a documented reason not to.

## Current document boundary

The document capability ends at delivery of the final user-selected PDF or DOCX file. JanaVani does not send the document by email, post it, print it, or choose the user's submission method. Future communication/submission capabilities may exist elsewhere in the full ecosystem, but must not be silently introduced into this document service.

## Privacy boundary

Personal and sensitive source material remains on the user's device by default. Shared services should receive only the minimum necessary information. Optional cryptographic, decentralized, or privacy-transport technologies must not be treated as permission to distribute sensitive citizen data.

## AI boundary

AI is an optional shared capability **for the user**. JanaVani's core correctness, provenance, procedural verification, and safety rules must not depend on a particular AI provider or model.
