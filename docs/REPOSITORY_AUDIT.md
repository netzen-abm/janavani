# JANAVANI — REPOSITORY AUDIT

**Version:** 1.1  
**Status:** ACTIVE  
**Purpose:** Repository structure, technical-debt, legacy-code, duplication, and cleanup audit  
**Repository:** netzen-abm/janavani  
**Branch:** main  
**Last Updated:** 11 August 2026

---

# 1. PURPOSE

This document records the current structural condition of the Janavani repository.

It exists to answer:

1. What is active?
2. What is legacy?
3. Where are responsibilities duplicated?
4. What technical debt remains?
5. What should be reviewed?
6. What can safely be removed?
7. What must NOT be changed while the current MVP is being developed?

This document is an audit register.

It is not a replacement for:

- `docs/SOURCE_OF_TRUTH.md`
- `docs/ARCHITECTURE.md`
- `docs/JANAVANI_NORTH_STAR.md`
- `docs/JANAVANI_PRODUCT_LANDSCAPE.md`
- `ROADMAP.md`

Those documents define architecture, product direction, and execution.

This document records repository condition and technical debt.

---

# 2. AUDIT PRINCIPLE

The repository must be changed according to evidence.

No file should be deleted merely because:

- it appears old
- it looks duplicated
- a newer implementation exists
- it is not currently imported
- it appears unnecessary

Before deletion, the following must be verified:

```text
File
 ↓
Imports
 ↓
Runtime references
 ↓
Tests
 ↓
Deployment references
 ↓
Documentation references
 ↓
Replacement capability
 ↓
Deletion safety
Only after verification should a file be classified as safe to delete.
________________________________________
3. CURRENT REPOSITORY STATE
The repository is structurally suitable for continued MVP development.
The current architecture contains the major platform layers required for the Janavani workflow:
Interfaces
    ↓
Conversation
    ↓
Workflow
    ↓
Engine
    ↓
Domain
    ↓
Services
    ↓
Documents
    ↓
Storage
The repository should now prioritize:
Feature reliability over another general cleanup cycle.
The current Web MVP should not be delayed by unnecessary restructuring.
________________________________________
4. ACTIVE CORE MODULES
Module	Status	Responsibility
conversation/	ACTIVE	Citizen conversation and interaction flow
workflow/	ACTIVE	Business workflow definitions and execution
engine/	ACTIVE	Workflow execution, state and orchestration
domain/	ACTIVE	Core Janavani domain concepts
services/	ACTIVE	Business and application services
documents/	ACTIVE	Document composition and generation
storage/	ACTIVE	Persistence and data access
src/	ACTIVE	Production application code
These modules should remain modular and replaceable.
No interface-specific business logic should be allowed to leak into the core platform.
________________________________________
5. ACTIVE INTERFACES
Telegram
Status: FUNCTIONAL / FROZEN
Telegram is the first Janavani interface.
It should remain operational while the Web interface is developed.
The Telegram interface must not become the owner of:
•	domain logic 
•	workflow definitions 
•	document business rules 
•	storage logic 
•	governance intelligence 
________________________________________
Web
Status: CURRENT DEVELOPMENT PRIORITY
The Web interface is the current development focus.
The Web application should consume shared Janavani platform capabilities.
Correct:
Web
 ↓
Janavani Platform
Incorrect:
Web
 ↓
Telegram
________________________________________
6. LEGACY / REVIEW MODULES
The following areas have previously been identified as legacy, duplicated, or candidates for migration.
They remain REVIEW, not automatically removable.
Area	Current / Legacy Location	Intended Replacement	Status
Database	database/	storage/	REVIEW
Tools	tools/	services/	REVIEW
Legacy bot entry	bot.py	src/main.py	REVIEW
Legacy async bot	bot_async.py	src/main.py	REVIEW
Legacy workflow logic	conversation/workflow.py	workflow/	REVIEW
Legacy PDF generation	tools/generate_pdf.py	services/ / document layer	REVIEW
Legacy directory search	tools/search_directory.py	services/	REVIEW
The replacement must be proven functional before legacy code is removed.
________________________________________
7. DUPLICATE RESPONSIBILITIES
Known areas requiring architectural reconciliation:
Responsibility	Legacy / Current Location	Intended Location	Action
Workflow	conversation/workflow.py	workflow/	Verify dependencies
Database access	database/	storage/	Verify active references
PDF generation	tools/generate_pdf.py	documents/ / services	Verify active references
Directory search	tools/search_directory.py	services/	Verify active references
Bot entry	bot.py, bot_async.py	src/main.py	Verify deployment references
The existence of these files does not by itself prove that they are unused.
________________________________________
8. TECHNICAL DEBT REGISTER
TD-001 — Legacy Code Coexistence
Status: OPEN
Legacy modules and newer modular implementations coexist.
Risk
Maintaining multiple implementations of similar responsibilities can cause:
•	confusion 
•	inconsistent behaviour 
•	duplicated fixes 
•	accidental imports 
•	increased maintenance cost 
Action
Identify actual runtime and import dependencies.
Then:
Verify
 ↓
Migrate
 ↓
Test
 ↓
Deprecate
 ↓
Delete only when proven safe
________________________________________
TD-002 — Workflow Responsibility Reconciliation
Status: OPEN
Workflow-related logic has historically existed in more than one location.
Risk
Two workflow implementations can diverge.
Action
The canonical workflow implementation should remain in the designated workflow layer.
Legacy workflow code should be migrated or retired only after dependency verification.
________________________________________
TD-003 — Storage Responsibility Reconciliation
Status: OPEN
Older database-related code and the newer storage architecture coexist.
Risk
Multiple persistence paths may create:
•	inconsistent data handling 
•	duplicated logic 
•	unclear ownership 
•	migration problems 
Action
storage/ should become the canonical persistence boundary.
Legacy database code should be reviewed for:
•	imports 
•	scripts 
•	tests 
•	deployment usage 
•	data migration requirements 
________________________________________
TD-004 — Document Generation Reconciliation
Status: OPEN
PDF/document-generation responsibilities have existed across different locations.
Risk
Multiple document-generation implementations may create inconsistent output.
Action
The document layer should become the canonical owner of document composition and generation.
Legacy implementations should be retained until replacement behaviour is verified.
________________________________________
TD-005 — Directory / Office Search Reconciliation
Status: OPEN
Directory-search functionality has historically existed in legacy tools and newer service structures.
Risk
Office-selection behaviour could diverge between implementations.
Action
Establish one canonical office-search service.
The service must support:
•	office lookup 
•	district/location filtering 
•	department/type filtering 
•	manual fallback 
•	reliable handling when no office is found 
The system must never invent an office merely to complete a workflow.
________________________________________
TD-006 — Automated Testing Coverage
Status: OPEN
The repository requires stronger automated verification of the complete citizen journey.
Required areas
•	Unit tests 
•	Workflow tests 
•	Conversation tests 
•	Document tests 
•	Office-search tests 
•	PDF-generation tests 
•	Web integration tests 
•	Telegram integration tests 
Priority
HIGH
Testing should increase as the Web MVP becomes operational.
________________________________________
TD-007 — Error Handling
Status: OPEN
Centralized and consistent error handling remains an important reliability requirement.
Required direction
Input Error
 ↓
Validation
 ↓
Controlled Error
 ↓
User-Friendly Message
 ↓
Recoverable Workflow State
Errors must not expose:
•	secrets 
•	internal paths 
•	stack traces 
•	unnecessary personal information 
________________________________________
TD-008 — Structured Logging
Status: OPEN
The platform requires reliable operational logging.
Logging should support:
•	debugging 
•	failure analysis 
•	workflow tracing 
•	operational monitoring 
Logs must follow privacy and data-minimization principles.
Sensitive citizen information should not be unnecessarily logged.
________________________________________
TD-009 — Privacy / Metadata Minimization
Status: OPEN
Privacy is a core Janavani architectural principle.
Future implementation should progressively strengthen:
•	data minimization 
•	metadata minimization 
•	consent handling 
•	retention rules 
•	secure storage 
•	access control 
•	auditability 
Privacy requirements must be applied to every new feature.
________________________________________
TD-010 — Security Hardening
Status: OPEN
Security requirements still need progressive implementation and verification.
Areas include:
•	secrets management 
•	authentication 
•	authorization 
•	rate limiting 
•	abuse prevention 
•	secure configuration 
•	audit logging 
•	backup strategy 
•	production monitoring 
Security should be treated as part of feature development rather than a final-stage task.
________________________________________
TD-011 — Web Integration Verification
Status: OPEN / CURRENT PRIORITY
The Web application is the current product-development priority.
The complete Web flow must be tested end-to-end:
Citizen
 ↓
Web
 ↓
Issue
 ↓
Guided Workflow
 ↓
Authority
 ↓
Complaint
 ↓
Preview
 ↓
PDF
 ↓
Download
The Web MVP should not be considered complete until this journey is reliable.
________________________________________
TD-012 — Documentation Synchronisation
Status: OPEN
Janavani now contains several important documentation layers.
They must remain synchronized.
Primary documents include:
docs/JANAVANI_NORTH_STAR.md
        ↓
docs/SOURCE_OF_TRUTH.md
        ↓
docs/JANAVANI_PRODUCT_LANDSCAPE.md
        ↓
ROADMAP.md
        ↓
docs/RELEASE_1_CHECKLIST.md
        ↓
Actual Repository
        ↓
Tests
Documentation must not claim functionality that the code and tests do not support.
________________________________________
9. DOCUMENTATION DEBT
The repository previously contained documentation that did not fully reflect the current implementation.
The following documents have been identified for reconciliation:
Document	Status	Action
JANAVANI_NORTH_STAR.md	CURRENT	Keep / Lock
SOURCE_OF_TRUTH.md	CURRENT	Keep / Lock
ARCHITECTURE.md	REVIEW	Reconcile terminology later
PROJECT_MAP.md	REVIEW	Reconcile with actual repository
REPOSITORY_AUDIT.md	CURRENT	Maintain as audit register
REPOSITORY_RULES.md	CURRENT	Keep / Lock
SYSTEM_QUALITY_STANDARD.md	CURRENT	Keep / Lock
RELEASE_1_CHECKLIST.md	REVIEW	Reconcile with actual implementation
ROADMAP.md	CURRENT	Maintain as execution roadmap
JANAVANI_PRODUCT_LANDSCAPE.md	CURRENT	Maintain as product landscape
Documentation changes should be grouped logically and committed cleanly.
________________________________________
10. SAFE-TO-DELETE STATUS
Current Status
NO LEGACY FILE IS YET CLASSIFIED AS SAFE TO DELETE BY THIS DOCUMENT ALONE.
This is intentional.
A file becomes safe to delete only after verification.
Required checklist:
[ ] No production imports
[ ] No test imports
[ ] No deployment references
[ ] No script dependencies
[ ] No active documentation dependency
[ ] Replacement implementation verified
[ ] Data migration completed where required
[ ] Tests pass
[ ] Deployment verified
[ ] Deletion reviewed
Only after all applicable checks are satisfied should the file be deleted.
________________________________________
11. DO NOT DELETE DURING CURRENT WEB MVP
The following should not be removed merely for the sake of cleanup while the Web MVP is being developed:
•	Working Telegram components 
•	Shared workflow components 
•	Existing office data 
•	Existing document-generation components 
•	Existing storage components 
•	Legacy components with unknown dependencies 
•	Configuration required by deployment 
•	Scripts whose dependencies have not been verified 
The priority is:
Stability before cleanup.
________________________________________
12. CURRENT CLEANUP STRATEGY
Janavani should use controlled migration rather than a large cleanup operation.
Preferred sequence:
Identify
   ↓
Understand
   ↓
Verify
   ↓
Test
   ↓
Migrate
   ↓
Deprecate
   ↓
Monitor
   ↓
Delete
Avoid:
Find old file
   ↓
Delete immediately
________________________________________
13. REPOSITORY QUALITY RULES
The following principles apply to future repository changes.
Rule 1 — One Responsibility
Each module should have a clearly defined responsibility.
Rule 2 — One Canonical Implementation
There should eventually be one authoritative implementation for each business responsibility.
Rule 3 — Interfaces Stay Thin
Interfaces should translate user interaction into platform operations.
They should not own business logic.
Rule 4 — Domain Independence
Core domain logic must not depend on Telegram or another interface.
Rule 5 — Storage Boundary
Storage owns persistence.
Rule 6 — Services Coordinate
Services coordinate application/business operations.
Rule 7 — Documents Own Document Generation
Document generation should have a clear canonical owner.
Rule 8 — Privacy Before Convenience
Convenience must not justify unnecessary collection or exposure of citizen information.
Rule 9 — Security Is Continuous
Security is part of every feature.
Rule 10 — Evidence Before Deletion
No destructive repository change should be made without verification.
________________________________________
14. CURRENT PRIORITY
The repository audit does not create a new cleanup sprint.
Current priority remains:
WEB MVP
   ↓
ONE COMPLETE CITIZEN JOURNEY
   ↓
COMPLAINT
   ↓
PDF
   ↓
DOWNLOAD
The audit exists to prevent technical debt from becoming invisible.
It does not exist to interrupt current product development.
________________________________________
15. NEXT AUDIT PHASE
After the Web MVP reaches a reliable milestone, perform a targeted repository audit.
The next audit should verify:
Code
•	Actual imports 
•	Runtime dependencies 
•	Duplicate implementations 
•	Dead code 
•	Unused modules 
Data
•	Database ownership 
•	Storage ownership 
•	Data migration requirements 
•	Static datasets 
•	Backup requirements 
Deployment
•	Railway configuration 
•	Web deployment configuration 
•	Environment variables 
•	Build configuration 
•	Runtime entry points 
Testing
•	Unit coverage 
•	Integration coverage 
•	Workflow coverage 
•	Regression coverage 
Security
•	Secrets 
•	Authentication 
•	Authorization 
•	Rate limiting 
•	Logging 
•	Data exposure 
Documentation
•	Architecture 
•	Project map 
•	Roadmap 
•	Product landscape 
•	Release checklist 
________________________________________
16. AUDIT DECISION FRAMEWORK
Every future repository change should be classified as one of:
KEEP
Use when the component is active and correctly placed.
REFACTOR
Use when the component is valid but its implementation needs improvement.
MIGRATE
Use when responsibility belongs in another canonical module.
DEPRECATE
Use when a replacement exists but removal requires a transition period.
DELETE
Use only after dependency and replacement verification.
RETAIN FOR RESEARCH
Use for experimental or future-oriented work that has strategic value but is not part of the current MVP.
________________________________________
17. ARCHITECTURAL DIRECTION
The repository should progressively converge toward:
                    JANAVANI
                        │
                        ▼
                  INTERFACES
                        │
                        ▼
                 PLATFORM CORE
                        │
          ┌─────────────┼─────────────┐
          ▼             ▼             ▼
      WORKFLOW       DOMAIN        SERVICES
          │             │             │
          └─────────────┼─────────────┘
                        ▼
                   DOCUMENTS
                        │
                        ▼
                    STORAGE
The architecture must remain:
•	modular 
•	replaceable 
•	testable 
•	privacy-first 
•	security-conscious 
•	interface-independent 
________________________________________
18. AUDIT CONCLUSION
The Janavani repository does not currently require another broad restructuring exercise.
The repository has sufficient architectural structure to continue MVP development.
The major remaining repository concerns are:
1.	Legacy-code reconciliation 
2.	Duplicate-responsibility verification 
3.	Automated testing 
4.	Error handling 
5.	Structured logging 
6.	Privacy hardening 
7.	Security hardening 
8.	Web integration verification 
9.	Documentation synchronization 
These should be addressed progressively.
The immediate priority remains the Web MVP.
________________________________________
19. NORTH STAR ALIGNMENT
Repository decisions must remain subordinate to the Janavani North Star.
The repository exists to support the product mission.
Therefore:
JANAVANI NORTH STAR
        ↓
PRODUCT DIRECTION
        ↓
ROADMAP
        ↓
ARCHITECTURE
        ↓
CODE
        ↓
TESTS
Technical decisions must serve the citizen journey.
The repository must not become an end in itself.
________________________________________
20. FINAL RULE
BUILD THE PRODUCT BEFORE THE ECOSYSTEM.
And for repository maintenance:
VERIFY BEFORE REFACTORING.
TEST BEFORE DELETING.
STABILIZE BEFORE OPTIMIZING.
DOCUMENT WHAT EXISTS, NOT WHAT WE HOPE EXISTS.
________________________________________
END OF JANAVANI REPOSITORY AUDIT

### What this accomplishes

This version deliberately **does not pretend we have completed a code-level dependency audit**. That's important.

It converts the old:

> `(To be filled during audit)`

into an actual controlled register, while keeping uncertain legacy files at **REVIEW** rather than falsely declaring them dead.

For your current project sequence, this is the correct state:

**North Star → Source of Truth → Product Landscape → Roadmap → Repository Audit → Release Checklist → final cross-document check → one commit.**

Now replace the contents of:

```text
