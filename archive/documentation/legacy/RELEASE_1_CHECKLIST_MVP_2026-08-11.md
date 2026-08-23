# ARCHIVED — JANAVANI RELEASE 1 / MVP CHECKLIST

**Archive reason:** Superseded by the full-ecosystem roadmap and Master Task Checklist.
**Original date:** 11 August 2026
**Historical value:** Preserved as evidence of the earlier Release 1 construction plan.

> This document is historical. It is not a current product boundary, roadmap, release gate, or engineering instruction.

---

# Original document

# Janavani Release 1 Checklist

**Version:** 1.0  
**Status:** Active MVP Release Checklist (historical)  
**Last Updated:** 11 August 2026

---

# 1. PURPOSE

This document defined the verified readiness criteria for Janavani Release 1.

Release 1 focused on a reliable citizen workflow rather than the complete long-term Janavani ecosystem.

The target journey was:

Citizen Problem
↓
Document Selection
↓
Location
↓
Authority / Office
↓
Identity
↓
Complaint Preview
↓
Document Generation
↓
Document Delivery

---

# 2. RELEASE PRINCIPLE

A capability was marked COMPLETE only when:

1. It existed in the repository.
2. It was connected to the active workflow.
3. It had been tested.
4. It did not introduce a known blocking error.

Documentation alone did not constitute implementation.

---

# 3. CORE PLATFORM

## Architecture

- [x] Modular repository structure
- [x] Conversation layer
- [x] Workflow layer
- [x] Workflow engine
- [x] State management
- [x] Session management
- [x] Domain layer
- [x] Services layer
- [x] Documents layer
- [x] Storage layer

---

# 4. TELEGRAM INTERFACE

## Historical Status

**FUNCTIONAL / FROZEN**

- [x] Telegram bot starts
- [x] `/start`
- [x] Issue capture
- [x] Conversation routing
- [x] Document selection
- [x] District/location selection
- [x] Office search
- [x] Office fallback
- [x] Identity selection
- [x] Complaint preview
- [x] Complaint generation
- [x] PDF generation
- [x] Document delivery

## Stabilisation

- [ ] Full end-to-end regression test
- [ ] State transition audit
- [ ] Invalid-input handling audit
- [ ] Duplicate prompt audit
- [ ] Error-handler implementation
- [ ] Single-instance deployment verification

---

# 5. WEB MVP

Historical Web checklist omitted from current scope; current Web work is governed by `ROADMAP.md`, `docs/JANAVANI_MASTER_ARCHITECTURE.md`, and `docs/MASTER_TASK_CHECKLIST.md`.

---

# 6. DOCUMENT SYSTEM

Historical Release 1 document scope included complaint generation, PDF generation, and later expansion of RTI, representation, grievance, appeal and legal-document families.

---

# 7. IDENTITY AND PRIVACY

Historical checklist covered identity selection, anonymous mode, data minimisation, metadata minimisation, consent and privacy review.

---

# 8. OFFICE DIRECTORY

Historical checklist used CSV-backed office data and manual fallback while identifying the need for production-quality government directory data.

---

# 9. AI

AI was not required for the historical basic document-generation workflow and was intentionally bounded to professional legal/civic assistance.

---

# 10–13. SECURITY / TESTING / RELIABILITY / DEPLOYMENT

Historical Release 1 gates included security, testing, error handling, monitoring, deployment, storage and backup verification.

---

# 14. HISTORICAL RELEASE DEFINITION

The historical Release 1 goal was for a citizen to describe a government-related problem, select a document, provide location, identify an authority, select an identity mode, review the complaint, generate the document, and receive/download it.

---

# 15. HISTORICAL OUT-OF-SCOPE ITEMS

The historical checklist deferred RTI automation, government intelligence, accountability scoring, Bhu-Janavani, advanced analytics, Web3, Nostr, Reticulum/off-grid infrastructure, ZKP systems, large-scale multilingual AI and the broader citizen-governance intelligence platform.

These are **not current exclusions**. They are preserved only as historical evidence of the earlier scope definition.

---

# 16. HISTORICAL GOVERNING RULE

The former document ended with a product-first/MVP framing. That framing has been superseded.

**Current rule:** Janavani is being built as one full citizen-governance ecosystem. Individual releases, pilots and verified workflows are construction units inside that ecosystem.

**END OF ARCHIVED DOCUMENT**
