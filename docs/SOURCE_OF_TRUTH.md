# JANAVANI — CANONICAL SOURCE OF TRUTH

**Status:** LOCKED  
**Version:** 1.0  
**Repository:** netzen-abm/janavani  
**Branch:** main  
**Purpose:** Permanent architectural and execution reference

---

# 1. WHAT JANAVANI IS

Janavani is a privacy-first citizen governance platform.

Janavani is NOT a Telegram bot.

Telegram is one interface through which citizens can access Janavani.

The long-term Janavani ecosystem may provide the same underlying capabilities through:

- Web App
- Telegram Bot
- Android App
- iOS App
- WhatsApp
- Messenger
- API
- Future interfaces and services

The underlying Janavani capabilities must not belong to any single interface.

---

# 2. CORE ARCHITECTURAL PRINCIPLE

Janavani has a shared platform layer and multiple independent interfaces.

The architecture is:

Citizen
    ↓
Interface
    ↓
Shared Janavani Platform
    ↓
Services / Domain / Workflow / Documents / Storage

Examples of interfaces:

Web App
Telegram
Android
iOS
WhatsApp
Messenger
API
Future interfaces

Each interface is an independent consumer of Janavani capabilities.

---

# 3. INTERFACE INDEPENDENCE

No interface should depend on another interface for its operation.

The following are NOT allowed:

Web → Telegram
Telegram → Web
WhatsApp → Telegram
Telegram → WhatsApp
Android → Telegram
iOS → Telegram

Instead:

Web → Janavani Platform
Telegram → Janavani Platform
WhatsApp → Janavani Platform
Android → Janavani Platform
iOS → Janavani Platform
Messenger → Janavani Platform
API → Janavani Platform

If one interface crashes, another interface must remain capable of functioning independently, subject to shared infrastructure availability.

---

# 4. DEPLOYMENT PRINCIPLE

## ONE INDEPENDENT RUNTIME PER DEPLOYMENT

Each deployment should run one interface/runtime appropriate to that deployment.

Examples:

Web deployment
    ↓
Web runtime
    ↓
Janavani Platform

Telegram deployment
    ↓
Telegram runtime
    ↓
Janavani Platform

Future Android/API/backend deployments may have their own appropriate runtime architecture.

An interface must NOT start another interface as part of its normal runtime.

For example:

Web must NOT start Telegram.

Telegram must NOT start Web.

This rule exists to maintain failure isolation, deployment clarity, maintainability, and scalability.

---

# 5. CURRENT REPOSITORY PRINCIPLE

The existing repository structure should NOT be unnecessarily reorganized.

The Telegram citizen flow is already working through a complete MVP cycle.

Therefore:

- Do not restructure working Telegram code without a demonstrated need.
- Do not rename files merely for cosmetic reasons.
- Do not move large numbers of files simply to make the architecture look cleaner.
- Prefer incremental changes.
- Verify the actual repository before changing code.
- Preserve working functionality.

Architecture changes must be justified by an actual technical requirement.

---

# 6. CURRENT SHARED PLATFORM

The shared Janavani platform currently consists of several layers.

## Conversation

Location:

src/conversation/

Purpose:

- Citizen interaction flow
- Conversation state
- Session handling
- Conversation steps
- Routing

Important files include:

- engine.py
- router.py
- session.py
- state.py
- constants.py
- steps/

---

## Workflow

Location:

src/workflow/

Purpose:

- Workflow definitions
- Reusable workflow steps
- Platform-level workflow logic

---

## Engine

Location:

src/engine/

Purpose:

- Workflow execution
- State registry
- Workflow registry
- Workflow context

Important files include:

- state_registry.py
- workflow_context.py
- workflow_engine.py
- workflow_registry.py

---

## Domain

Location:

src/domain/

Purpose:

Core Janavani concepts such as:

- Citizen
- Issue
- Office
- Department
- Location
- Document
- Evidence
- Remedy
- Submission

---

## Services

Location:

src/services/

Purpose:

Shared business/application capabilities.

Examples include:

- AI service
- Classification
- Complaint service
- Document service
- Office service
- Privacy service
- Rating service
- Search service
- Complaint tracking
- Escalation

These capabilities must remain independent of a particular user interface wherever practical.

---

## Documents

Location:

src/documents/

Purpose:

- Complaint construction
- Document generation
- PDF generation
- Grievance documents
- Petition documents
- RTI documents
- Document standards
- Delivery profiles

Document generation is a shared Janavani capability, not a Telegram-only capability.

---

## Storage

Location:

src/storage/

Purpose:

- Persistence
- Repositories
- Database access
- Citizen data
- Issue data
- Office data
- Supabase integration

Storage must remain independent of any specific interface.

---

## Models

Location:

src/models/

Purpose:

Application/data models such as:

- Complaint
- Office
- Rating

---

## Configuration

Location:

src/core/

Current purpose:

- Configuration
- Settings
- Environment configuration

IMPORTANT:

src/core/ does NOT mean that every core Janavani capability must be moved into this folder.

The Janavani "core platform" is the combination of the shared application layers described above.

Do not create unnecessary restructuring merely because the folder is named "core".

---

# 7. INTERFACES

Interfaces are entry layers through which citizens or external systems access Janavani.

Current and future interfaces include:

## Telegram

Current file:

src/bot_telegram.py

Status:

WORKING / FROZEN FOR NOW

The Telegram bot currently provides the working citizen complaint-generation flow.

Do not modify it while Web development is the current priority unless a verified dependency requires it.

Future cleanup may rename this file to bot.py if and when that change is useful.

That rename is NOT required now.

---

## Web

Current Web implementation includes:

src/web/app.py

Status:

CURRENT DEVELOPMENT PRIORITY

The Web App is the next interface to be developed.

The Web App must consume shared Janavani capabilities rather than duplicate Telegram-specific business logic.

---

## WhatsApp

Current/future files include:

src/bot_whatsapp.py
src/whatsapp/

Status:

FUTURE

Do not make WhatsApp a dependency of Telegram or Web.

---

## Messenger

Current/future file:

src/bot_messenger.py

Status:

FUTURE

Do not make Messenger a dependency of Telegram or Web.

---

## API

Repository-level API infrastructure already exists.

Location:

api/

Status:

FUTURE / EXPANDING

The API should eventually provide independent access to Janavani capabilities for applications and external integrations.

---

## Android and iOS

Status:

FUTURE

Android and iOS applications will become independent interfaces to Janavani capabilities.

They must not depend on Telegram.

---

# 8. CURRENT TELEGRAM STATUS

The Telegram Bot has already demonstrated the complete basic complaint flow.

Current verified flow:

User enters issue
    ↓
Issue classification
    ↓
Document selection
    ↓
District
    ↓
Office search
    ↓
Office selection/fallback
    ↓
Identity
    ↓
Name/address where required
    ↓
Preview
    ↓
Format selection
    ↓
Document generation
    ↓
PDF download

The Telegram flow is currently considered stable enough to freeze while Web development proceeds.

Do not repeatedly refactor the Telegram flow while the Web App is being developed.

---

# 9. CURRENT DEVELOPMENT PRIORITY

## PRIMARY PRIORITY: WEB APP

Telegram is temporarily frozen because the working flow has already been demonstrated.

The next major task is to build a fully functioning Web App using the existing Janavani platform capabilities.

The Web App should eventually provide the same fundamental citizen capability without depending on Telegram.

---

# 10. INITIAL PRODUCT FOCUS

The initial Janavani product focus is:

## AI-CAPABLE CITIZEN COMPLAINT PLATFORM

The primary capability is helping a citizen:

1. Describe a problem in natural language.
2. Understand/classify the issue.
3. Identify the relevant category and department.
4. Identify the appropriate document/remedy.
5. Identify the appropriate district/location.
6. Find the appropriate government office.
7. Allow manual fallback when reliable data is unavailable.
8. Collect only necessary citizen information.
9. Produce a legally informed complaint.
10. Generate a usable document.
11. Allow the citizen to download the document.

AI should assist the system but must not silently invent government-office information or legal facts.

When structured data is unavailable, the system should clearly distinguish:

- Verified data
- User-provided data
- AI-assisted inference
- Unverified information

The citizen must be allowed to continue through an appropriate manual path when automated data is unavailable.

---

# 11. SECONDARY TESTING CAPABILITY

Government office/service efficiency rating is also part of the initial product testing scope.

Existing capabilities include rating-related services and data.

This capability should remain part of Janavani but should not destabilize the primary complaint workflow.

---

# 12. AI PRINCIPLE

AI is a shared Janavani capability.

AI must NOT become a Telegram-specific feature.

Potential AI capabilities include:

- Issue understanding
- Classification
- Department identification
- Office matching
- Missing-information detection
- Language assistance
- Legal-information assistance
- Document drafting assistance
- RAG-based knowledge retrieval
- Citizen guidance

AI must operate within verification and privacy rules.

AI must not be treated as an unquestionable source of truth.

---

# 13. DATA VERIFICATION PRINCIPLE

Janavani must prefer verified structured data whenever available.

For example:

Office search should follow:

Verified office database
    ↓
Matching/filtering
    ↓
Reliable result

If no verified result is available:

    ↓
Inform citizen
    ↓
Allow manual input
    ↓
Clearly mark information as user-provided/unverified
    ↓
Allow later verification where appropriate

The system must not fabricate an office merely to complete a workflow.

---

# 14. PRIVACY PRINCIPLE

Janavani follows:

- Privacy by Design
- Privacy by Default
- Minimum Data Collection
- Anonymous by Default where practical
- Security at the Core
- Citizen First

Identity information must be collected only when required by the selected workflow or document.

---

# 15. MVP ACCEPTANCE TARGET

The initial MVP is considered successful when ONE complete citizen flow works reliably.

The primary acceptance target is:

User types issue
    ↓
System guides user step-by-step
    ↓
Relevant complaint is created
    ↓
PDF is generated
    ↓
PDF download works

This is the immediate execution target.

Additional features must not distract from completing and validating this core flow.

---

# 16. DEVELOPMENT ORDER

Current execution order:

STEP 1
Lock architecture and Source of Truth

STEP 2
Build and validate Web App

STEP 3
Connect Web App to existing shared Janavani capabilities

STEP 4
Complete one full Web citizen complaint flow

STEP 5
Validate PDF generation and download

STEP 6
Validate AI assistance and verification behaviour

STEP 7
Validate office data and fallback behaviour

STEP 8
Validate rating capability

STEP 9
Production hardening

STEP 10
Return to Telegram and improve AI capabilities

STEP 11
Expand to API / WhatsApp / Messenger / Android / iOS

The order may change only after verification and explicit architectural review.

---

# 17. PRODUCTION PRINCIPLE

Production readiness means more than deployment.

Before declaring a product production-ready, verify:

- Application reliability
- Database persistence
- Error handling
- Logging
- Security
- Privacy
- Input validation
- Document generation
- File delivery
- AI failure handling
- Data verification
- Recovery behaviour
- Independent interface operation
- Deployment configuration
- Tests

---

# 18. SOURCE-OF-TRUTH RULE

This document is the canonical architectural reference for Janavani.

When another document, code file, README, roadmap, deployment configuration, or previous discussion appears to conflict with this document:

1. Do not silently guess.
2. Verify the current repository.
3. Identify the conflict.
4. Determine whether the Source of Truth needs updating.
5. Make the smallest justified change.
6. Record significant architectural changes explicitly.

The actual code repository remains the implementation authority for what currently exists.

This document defines the intended architecture and development direction.

---

# 19. NO-GUESSING DEVELOPMENT RULE

Before providing replacement code:

1. Verify the current file.
2. Verify its imports and dependencies.
3. Verify related state/constants/services.
4. Verify the repository structure when relevant.
5. Check whether another file already implements the required capability.
6. Avoid duplicate functionality.
7. Provide complete replacement code only after verification.
8. Keep code reasonably compact and maintainable.
9. Avoid unnecessary restructuring.
10. Test/validate the proposed change before recommending replacement whenever the available environment permits.

Never invent a file, function, state, import, or dependency without verification.

---

# 20. STRUCTURE CHANGE RULE

The current repository has working functionality.

Therefore:

Prefer:

small verified change
    ↓
test
    ↓
commit
    ↓
continue

Avoid:

large restructuring
    ↓
many simultaneous changes
    ↓
uncertain dependencies
    ↓
broken working functionality

Folder and file renaming can happen later when there is a demonstrated benefit.

---

# 21. CURRENT WORKING STRUCTURE

The current structure remains intentionally close to the existing repository:

src/
├── adapters/
├── app/
├── commands/
├── conversation/
├── core/
├── documents/
├── domain/
├── engine/
├── models/
├── services/
├── storage/
├── utils/
├── web/
├── whatsapp/
├── workflow/
│
├── bot_telegram.py
├── bot_messenger.py
├── bot_whatsapp.py
├── legal_brain.py
├── main.py
├── test_supabase.py
└── web.py

No broad restructuring is required at this stage.

---

# 22. CURRENT ENTRY-POINT POLICY

Current verified interface entry points include:

Telegram:
src/bot_telegram.py

Web:
src/web/app.py

There are also older/transition files such as:

src/main.py
src/web.py

These must not automatically be treated as the long-term architecture merely because their names look like entry points.

Before changing deployment configuration, verify which file is actually intended and currently used.

---

# 23. TELEGRAM FREEZE

Until the Web App reaches the required MVP milestone:

Telegram is frozen.

Allowed:

- Verification
- Bug fixes required by shared-core changes
- Security fixes
- Critical compatibility fixes

Not allowed:

- Unnecessary refactoring
- Cosmetic restructuring
- Rewriting the working conversation flow
- Moving Telegram files without need

---

# 24. WEB DEVELOPMENT LOCK

The immediate development focus is the Web App.

The objective is NOT to redesign Janavani.

The objective is to expose existing Janavani capabilities through a clean, independent Web interface.

Build incrementally.

Verify every step.

Do not disturb the working Telegram flow.

---

# 25. LONG-TERM VISION

Janavani is intended to evolve into a multi-interface citizen governance ecosystem.

Potential interfaces include:

Web
Telegram
Android
iOS
WhatsApp
Messenger
API
Future channels

All interfaces should ultimately access shared Janavani capabilities.

The citizen should experience Janavani as one platform even though the underlying interfaces and deployments are independent.

---

# 26. FINAL ARCHITECTURE

                         JANAVANI PLATFORM
                                │
          ┌─────────────────────┴─────────────────────┐
          │                                           │
   SHARED PLATFORM                              INTERFACES
          │                                           │
          │                           ┌───────────────┼───────────────┐
          │                           │               │               │
          ▼                           ▼               ▼               ▼
   Conversation                     Web          Telegram          Future
   Workflow                         App             Bot           Interfaces
   Engine
   Domain
   Services
   Documents
   Storage
   Models
          │
          ▼
       Data / State


INTERFACE RULE:

Web      ───────► Shared Janavani Platform
Telegram ───────► Shared Janavani Platform
WhatsApp ───────► Shared Janavani Platform
Android  ───────► Shared Janavani Platform
iOS      ───────► Shared Janavani Platform
Messenger───────► Shared Janavani Platform
API      ───────► Shared Janavani Platform

No interface starts or depends on another interface.

---

# 27. FINAL EXECUTION FOCUS

## ONE TARGET AT A TIME

The immediate target is:

BUILD THE WEB APP.

The first success condition is:

User enters an issue
    ↓
Web App guides the citizen
    ↓
Complaint is created
    ↓
PDF is generated
    ↓
PDF can be downloaded

Only after this is stable should we expand the next capability.

---

# 28. LOCK

This document is the current Janavani architectural Source of Truth.

Do not change the architecture casually.

Do not assume.

Verify first.

Change only what is necessary.

Protect working functionality.

Build one capability at a time.

---

**END OF CANONICAL SOURCE OF TRUTH**
