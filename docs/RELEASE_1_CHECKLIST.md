# Janavani Release 1 Checklist

**Version:** 1.0  
**Status:** Active MVP Release Checklist  
**Last Updated:** 11 August 2026

---

# 1. PURPOSE

This document defines the verified readiness criteria for Janavani Release 1.

Release 1 focuses on a reliable citizen workflow rather than the complete long-term Janavani ecosystem.

The target journey is:

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

A capability is marked COMPLETE only when:

1. It exists in the repository.
2. It is connected to the active workflow.
3. It has been tested.
4. It does not introduce a known blocking error.

Documentation alone does not constitute implementation.

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

## Current Status

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

Telegram should not receive unnecessary architectural changes while the Web MVP is being developed.

---

# 5. WEB MVP

## Status

**CURRENT PRIORITY**

- [ ] Web application entry point verified
- [ ] Citizen issue input
- [ ] Document selection
- [ ] Location selection
- [ ] Office search
- [ ] Office fallback
- [ ] Identity selection
- [ ] Complaint preview
- [ ] Complaint generation
- [ ] PDF generation
- [ ] PDF download
- [ ] Error handling
- [ ] Responsive citizen interface
- [ ] Privacy-first data handling

The Web interface must consume shared Janavani platform capabilities.

It must not recreate Telegram-specific business logic.

---

# 6. DOCUMENT SYSTEM

## Complaint

- [x] Structured complaint builder
- [x] Government-ready complaint format
- [x] Complaint ID generation
- [x] Office recipient information
- [x] Legal-ground section
- [x] PDF generation

## Additional Documents

- [ ] RTI
- [ ] Representation Letter
- [ ] Grievance Petition
- [ ] Appeal
- [ ] Legal Notice

These belong to later document-system expansion unless explicitly promoted into Release 1.

---

# 7. IDENTITY AND PRIVACY

- [x] Identity selection exists
- [x] Anonymous mode exists
- [x] Name-based identity modes exist
- [ ] Privacy-flow regression test
- [ ] Data-minimisation audit
- [ ] Metadata-minimisation audit
- [ ] Consent review
- [ ] Privacy threat-model review

---

# 8. OFFICE DIRECTORY

- [x] Office lookup capability
- [x] CSV-based office data currently supported
- [x] Manual office fallback
- [x] Continue without specific office
- [ ] Complete State / District / City / PIN data model
- [ ] Office-data validation
- [ ] Production-quality government directory
- [ ] Automated office-data update process

---

# 9. AI

## Release 1

AI is NOT required for the basic document-generation workflow.

- [ ] Production AI service
- [ ] AI complaint drafting
- [ ] Issue classification
- [ ] Department detection
- [ ] Legal recommendation
- [ ] Document quality review

AI must remain restricted to professional legal/civic assistance.

It must not become a general-purpose conversational chatbot.

---

# 10. SECURITY

- [ ] Threat model
- [ ] Secrets audit
- [ ] Rate limiting
- [ ] Authentication review
- [ ] Authorization review
- [ ] Secure configuration
- [ ] Dependency security review
- [ ] Production security review

---

# 11. TESTING

- [ ] Unit tests
- [ ] Conversation workflow tests
- [ ] State transition tests
- [ ] Office search tests
- [ ] Complaint builder tests
- [ ] PDF generation tests
- [ ] Telegram integration test
- [ ] Web integration tests
- [ ] End-to-end citizen journey test

---

# 12. RELIABILITY

- [ ] Centralised error handling
- [ ] Structured logging
- [ ] State validation
- [ ] Input validation
- [ ] Failure recovery
- [ ] Duplicate-action protection
- [ ] Monitoring
- [ ] Production health checks

---

# 13. DEPLOYMENT

- [ ] Production configuration verified
- [ ] Docker build verified
- [ ] Deployment verified
- [ ] Environment variables verified
- [ ] Database/storage strategy verified
- [ ] Backup strategy verified
- [ ] Monitoring verified
- [ ] Rollback procedure verified

---

# 14. RELEASE 1 DEFINITION

Release 1 is ready when a citizen can reliably:

1. Describe a government-related problem.
2. Select an appropriate document.
3. Provide the required location.
4. Identify or select an appropriate authority.
5. Select an identity mode.
6. Review the complaint.
7. Generate the document.
8. Receive/download the document.

The workflow must complete without a blocking error.

---

# 15. OUT OF SCOPE FOR RELEASE 1

The following are intentionally deferred:

- RTI automation
- Government KPI intelligence
- Budget-performance tracking
- MLA/MP performance scoring
- Office performance scoring
- Public corruption heat map
- Bhu-Janavani
- Advanced governance analytics
- Web3 infrastructure
- Nostr infrastructure
- Reticulum/off-grid infrastructure
- ZKP systems
- Large-scale multilingual AI
- Citizen governance intelligence platform

These remain part of the broader Janavani roadmap and North Star.

---

# 16. RELEASE GATE

Before declaring Release 1 complete:

- [ ] Core workflow tested end-to-end
- [ ] Web MVP tested
- [ ] Telegram regression test passed
- [ ] Document output verified
- [ ] Privacy review passed
- [ ] Security review passed
- [ ] Error handling verified
- [ ] Production deployment verified
- [ ] Release documentation updated

---

# 17. GOVERNING RULE

BUILD THE PRODUCT BEFORE THE ECOSYSTEM.

Release 1 exists to prove that Janavani can reliably convert a citizen problem into a useful government-ready action document.

Future intelligence and governance capabilities must not compromise the reliability of this core journey.

---

**END**
