# JANAVANI — PRODUCT LANDSCAPE

**Status:** LOCKED  
**Version:** 1.0  
**Purpose:** Birds-eye view of Janavani's present capabilities, current priorities, planned capabilities, and long-term ecosystem.

---

# 1. WHAT THIS DOCUMENT DOES

This document provides the birds-eye view of Janavani as a product ecosystem.

It answers four questions:

1. What does Janavani have now?
2. What are we actively building now?
3. What comes next?
4. What is the long-term Janavani vision?

This document is intentionally different from:

`docs/SOURCE_OF_TRUTH.md`

The Source of Truth defines the architecture and engineering rules.

This document defines the product landscape.

---

# 2. JANAVANI IN ONE SENTENCE

Janavani is a privacy-first citizen governance platform that helps citizens understand government-related problems, identify appropriate authorities, create legally structured documents, and progressively interact with and evaluate governance systems.

---

# 3. JANAVANI IS AN ECOSYSTEM

Janavani is NOT a Telegram bot.

Telegram is one interface.

The long-term ecosystem may include:

- Web App
- Telegram Bot
- Android App
- iOS App
- WhatsApp
- Messenger
- API
- AI capabilities
- Governance intelligence
- Citizen feedback systems
- Government-performance intelligence
- Future specialized governance services

The interfaces should remain independently deployable and independently replaceable.

---

# 4. PRODUCT LAYERS

Janavani can be viewed as six broad product layers.

```text
LAYER 1 — CITIZEN INTERFACES
Web
Telegram
Android
iOS
WhatsApp
Messenger
API

        ↓

LAYER 2 — CITIZEN INTERACTION
Conversation
Guidance
Forms
State
Session
Language

        ↓

LAYER 3 — GOVERNANCE INTELLIGENCE
Issue understanding
Classification
Department identification
Office matching
Location intelligence
Legal-information assistance
AI drafting

        ↓

LAYER 4 — GOVERNANCE ACTION
Complaint
Grievance
RTI
Representation
Petition
Appeal
Follow-up
Escalation

        ↓

LAYER 5 — DELIVERY + TRACKING
PDF
Digital delivery
Submission guidance
Complaint ID
Status
Follow-up
Feedback

        ↓

LAYER 6 — GOVERNANCE INTELLIGENCE
Office performance
Department performance
Complaint patterns
Resolution rates
Citizen feedback
Public accountability
Governance analytics

Not every layer is currently production-complete.

This diagram represents the product direction.

5. CURRENT STATE — VERIFIED / WORKING
5.1 Telegram Citizen Flow

Status:

WORKING

The Telegram interface has already demonstrated the complete basic complaint-generation flow.

Current flow:

Citizen
    ↓
Describe Issue
    ↓
Issue Classification
    ↓
Select Document
    ↓
Select District
    ↓
Office Search
    ↓
Office Selection / Fallback
    ↓
Identity
    ↓
Name / Address where required
    ↓
Preview
    ↓
Format Selection
    ↓
Document Generation
    ↓
PDF
    ↓
Download

The Telegram flow is currently frozen while Web development proceeds.

6. CURRENT DOCUMENT CAPABILITY

Current document-generation capability includes complaint creation and PDF generation.

Existing document architecture also contains support for future document types.

Current / existing document concepts include:

Complaint
Grievance
Petition
RTI
Representation
Document engine
Document standards
PDF generation
Delivery profiles

The immediate priority remains making the complaint workflow robust and reusable.

7. CURRENT OFFICE INTELLIGENCE

Current office capability includes:

Office database
District filtering
Department/type filtering
Office selection
Automatic office matching
Manual office entry
No-office fallback

Current principle:

Verified office data
        ↓
Automatic matching
        ↓
If no reliable match
        ↓
Manual citizen input

The system must never invent an office merely to complete a workflow.

8. CURRENT CLASSIFICATION

Janavani already contains issue-classification capability.

Current purpose:

Citizen Issue
     ↓
Category
     ↓
Department

This is the foundation for future AI-assisted classification.

9. CURRENT RATING CAPABILITY

Janavani already contains rating-related services and data structures.

The initial product focus includes testing government/service efficiency through structured ratings.

Rating should evolve toward useful governance feedback rather than becoming a simple popularity score.

Potential dimensions may include:

Service experience
Responsiveness
Delay
Resolution
Office experience
Citizen feedback

The detailed scoring methodology should be developed separately and verified before implementation.

10. CURRENT WEB APP STATUS

Status:

CURRENT DEVELOPMENT PRIORITY

The Web App is the next major interface.

The objective is NOT to redesign Janavani's underlying workflow.

The objective is to expose existing Janavani capabilities through an independent Web interface.

Target:

Web
 ↓
Shared Janavani capabilities
 ↓
Complaint
 ↓
PDF
 ↓
Download

The Web App must not depend on Telegram.

11. IMMEDIATE PRODUCT TARGET

The immediate target is:

ONE COMPLETE WEB CITIZEN JOURNEY

The first Web milestone is achieved when:

User enters issue
        ↓
Web guides user
        ↓
Issue is understood
        ↓
Required information is collected
        ↓
Department is identified
        ↓
Office is identified
        ↓
Complaint is generated
        ↓
PDF is generated
        ↓
PDF download works

This is the immediate execution target.

12. AI — CURRENT DIRECTION

AI is a major Janavani capability.

However:

AI IS NOT A GENERAL CHATBOT

AI should primarily function as controlled governance intelligence.

The intended AI role includes:

12.1 Issue Understanding

Convert natural citizen language into structured information.

Example:
"road bad for 3 months"

into structured information such as:

Problem:
Road damage

Duration:
3 months

Potential impact:
Public access / safety

Possible authority:
Local government / PWD

12.2 Issue Classification

Determine:

Category
Department
Problem type
Priority where justified
12.3 Complaint Drafting

Convert raw citizen language into:

Clear facts
Structured description
Appropriate subject
Formal government-ready language

AI must preserve the citizen's factual meaning.

It must not fabricate facts.

12.4 Legal-Information Assistance

AI may assist in identifying potentially relevant legal or constitutional provisions.

The system must distinguish:

Verified legal source
AI suggestion
User-provided information

AI output must not be treated as automatically authoritative.

12.5 Language Normalization

Planned capability includes:

Malayalam
Manglish
Hindi
English

Example:
Malayalam / Manglish / Hindi
        ↓
Language normalization
        ↓
Structured issue
        ↓
Complaint

13. AI — WHAT IT SHOULD NOT BECOME

Janavani AI should not primarily be:

Casual chatbot
General-purpose assistant
Entertainment chatbot
Open-ended conversational AI

The AI should remain purpose-driven and governance-oriented.

Core principle:

AI should reduce the citizen's bureaucratic burden.

14. NEXT INTELLIGENCE LAYER

After the basic Web complaint flow is stable, intelligence can become progressively stronger.

Potential capabilities:

Smart Office Routing
Issue
 +
Location
 +
Department
        ↓
Ranked office candidates

Location Intelligence

Potential information:

State
District
Taluk
Village
Ward
Panchayat
Municipality
Corporation
Landmark
Coordinates
Fallback Intelligence

If exact office information is unavailable:

No exact office
        ↓
Identify likely authority
        ↓
Show uncertainty
        ↓
Allow manual correction

15. DOCUMENT ECOSYSTEM

After the complaint workflow is stable, Janavani can expand document capabilities.

Potential document types:

Complaint
Grievance
RTI
Representation
Petition
Appeal
Notice
Follow-up Letter
Escalation Letter

Complaint
Grievance
RTI
Representation
Petition
Appeal
Notice
Follow-up Letter
Escalation Letter

The preferred architecture is a reusable document-composition engine rather than separate disconnected template systems.

16. EVIDENCE SYSTEM

Future evidence capabilities may include:

Photos
Videos
Documents
Voice recordings
GPS/location
Multiple evidence items

Long-term:

Citizen Issue
    ↓
Evidence
    ↓
Structured Complaint
    ↓
Government Document

AI-assisted image analysis may become a future capability, but must remain subject to privacy and verification rules.

17. COMPLAINT IDENTITY AND TRACKING

A future complaint lifecycle can include:

Complaint Created
        ↓
Complaint ID
        ↓
Document Generated
        ↓
Submitted
        ↓
Acknowledged
        ↓
Pending
        ↓
Resolved / Unresolved

A unique complaint identifier can support:

Tracking
Follow-up
Escalation
Citizen history
Analytics
18. FOLLOW-UP SYSTEM

Future capability:

If a complaint remains unresolved:

Complaint
    ↓
Waiting period
    ↓
No response
    ↓
Follow-up generator
    ↓
Citizen review
    ↓
Follow-up document

The system should not automatically make legal claims without verified rules.

19. ESCALATION SYSTEM

Future capability:

Complaint
    ↓
No response / unresolved
    ↓
Identify escalation authority
    ↓
Generate escalation document
    ↓
Citizen approval
    ↓
Submit

The escalation path must be based on verified rules and available authority data.

20. MULTI-DOCUMENT GOVERNANCE WORKFLOW

Long-term Janavani should move beyond one complaint.

Possible workflow:

Problem
 ↓
Complaint
 ↓
Submission
 ↓
Tracking
 ↓
Follow-up
 ↓
Escalation
 ↓
Appeal
 ↓
Resolution
 ↓
Feedback

This creates a complete citizen-government interaction lifecycle.

21. CITIZEN HISTORY

Future citizen capabilities may include:

Complaint history
Generated documents
Submission records
Status
Outcomes
Follow-ups
Feedback

Privacy principles remain mandatory.

Anonymous workflows should remain possible where appropriate.

22. GOVERNMENT SERVICE / OFFICE RATINGS

Government efficiency feedback is part of the broader Janavani vision.

Potential dimensions:

Office
 ↓
Citizen experiences
 ↓
Structured feedback
 ↓
Aggregated performance signals

The system should avoid reducing governance quality to a single simplistic number.

A future scorecard could consider:

Responsiveness
Resolution time
Complaint volume
Resolution rate
Citizen feedback
Service quality

Methodology must be evidence-based and transparent.

23. GOVERNMENT PERFORMANCE INTELLIGENCE

Long-term governance intelligence may include:

Government Performance Tracking

Potential data:

Budget usage
Public projects
Project status
Service delivery
Complaint patterns
Department Scorecards

Potential indicators:

Complaint volume
Resolution rate
Response time
Pending cases
Citizen feedback
Office Performance

Potential indicators:

Responsiveness
Service experience
Delay patterns
Resolution patterns

These are future capabilities, not current MVP requirements.

24. CITIZEN DASHBOARD

Future Web capability:

Citizen Dashboard

My Complaints
My Documents
Complaint Status
Follow-ups
Outcomes
Feedback

The dashboard should provide useful citizen control without collecting unnecessary personal data.

25. PUBLIC ACCOUNTABILITY LAYER

Long-term Janavani may provide public-facing governance intelligence.

Potential subjects:

Departments
Offices
Public services
Projects
Elected representatives where legally and technically appropriate

The objective is evidence-based public accountability, not political campaigning or popularity scoring.

26. GOVERNANCE ANALYTICS

Future analytics may identify:

Regional issue patterns
Department-level patterns
Service-delivery bottlenecks
Complaint concentrations
Resolution patterns

Potential output:

Citizen complaints
        ↓
Aggregated data
        ↓
Pattern detection
        ↓
Governance intelligence

Privacy-preserving aggregation is mandatory.

27. CORRUPTION / GOVERNANCE HEAT MAP

A future research capability discussed for Janavani is a governance/corruption heat map based on aggregated complaint signals.

Potential concept:

Anonymous / privacy-preserving complaints
        ↓
Verified aggregation
        ↓
Geographic patterns
        ↓
Governance intensity map

This must never expose individual citizens or unsupported accusations.

It is a future intelligence capability, not an MVP feature.

28. COMMUNITY DATA NETWORK

Long-term Janavani can use citizen and volunteer participation to improve government-office data.

Possible contributions:

Add missing office
Correct office information
Verify address
Verify contact details
Report outdated information
Upload supporting evidence

Possible verification model:

Citizen contribution
        ↓
Verification
        ↓
Confidence level
        ↓
Trusted directory

29. MOBILE ECOSYSTEM

Future interfaces:

Android

Independent Janavani interface.

Potential capabilities:

Complaint
Evidence
Location
Tracking
Notifications
Citizen dashboard
iOS

Independent Janavani interface.

The same shared platform capabilities should be exposed without depending on Telegram or Android.

30. MESSAGING ECOSYSTEM

Future interfaces include:

WhatsApp

Independent interface.

Messenger

Independent interface.

Telegram

Existing interface.

All should eventually consume shared Janavani capabilities.

No messaging platform should become the Janavani core.

31. API ECOSYSTEM

The API layer can eventually expose Janavani capabilities to:

Web
Mobile
Messaging platforms
External applications
Partner systems
Internal services

Potential API domains:

Issues
Complaints
Offices
Documents
Tracking
Ratings
Governance data
AI services

Authentication, authorization, privacy and rate limiting must be implemented before public exposure.

32. KNOWLEDGE / RAG SYSTEM

Janavani has an intended Open Source AI / Retrieval-Augmented Generation direction.

Potential knowledge sources:

Government rules
Official procedures
Legal sources
Office directories
Public datasets
Verified governance information

RAG should improve grounding and reduce unsupported AI output.

33. DECENTRALIZED / ADVANCED INFRASTRUCTURE

The repository contains legacy/prototype work related to:

Blockchain
IPFS
Nostr
Nym
Decentralized infrastructure

These remain long-term research possibilities.

They are NOT current execution priorities.

They must not delay the working citizen journey.

34. Bhu-Janavani / LAND INTELLIGENCE

A future strategic direction discussed for Janavani includes land/governance intelligence.

Possible capabilities may include:

Land-related complaints
Location intelligence
Public land information
Geographic governance analysis

This belongs to a later product phase.

It must not interfere with the immediate complaint platform.

35. PRODUCT MATURITY MODEL

Janavani can be understood as progressing through these levels:

LEVEL 1 — DOCUMENT GENERATOR

Citizen problem
→ document
→ PDF

This is the foundation.

LEVEL 2 — CITIZEN GUIDANCE SYSTEM

Citizen problem
→ understand
→ classify
→ identify authority
→ document

LEVEL 3 — CITIZEN ACTION SYSTEM

Problem
→ document
→ submission
→ tracking
→ follow-up
→ escalation

LEVEL 4 — CITIZEN GOVERNANCE PLATFORM

Problem
→ action
→ outcome
→ feedback
→ service intelligence

LEVEL 5 — GOVERNANCE INTELLIGENCE PLATFORM

Aggregated citizen experiences
→ patterns
→ department intelligence
→ public accountability
→ governance improvement

36. PRESENT VS FUTURE
PRESENT / VERIFIED
Janavani platform architecture
Conversation engine
Workflow/state system
Issue classification
Office database/search
Manual office fallback
Complaint builder
PDF generation
Identity modes
Telegram interface
Rating-related services/data
Storage infrastructure
Web application foundation
CURRENT BUILD
Web App
Complete Web complaint journey
Web PDF generation/download
AI-assisted complaint capability
Better office intelligence
Reliable data/fallback handling
NEXT
AI issue structuring
AI complaint drafting
Language normalization
Smarter office routing
Evidence
Complaint tracking
Follow-up
Rating methodology
Citizen dashboard
LATER
RTI automation
Representation/Petition/Appeal workflows
Escalation engine
Volunteer verification
Public accountability
Government performance analytics
Department scorecards
Governance heat maps
LONG-TERM
Android
iOS
WhatsApp
Messenger
Expanded API ecosystem
Advanced RAG
Large-scale governance intelligence
Bhu-Janavani
Decentralized infrastructure research
37. PRIORITY RULE

The existence of a feature in this document does NOT mean it should be built immediately.

Priority is determined by:

Current execution target
Citizen value
Dependency order
Verification
Security/privacy impact
Engineering readiness
38. CURRENT EXECUTION LOCK

Until the Web MVP is complete:

WEB APP
   ↓
ONE COMPLETE CITIZEN FLOW
   ↓
COMPLAINT
   ↓
PDF
   ↓
DOWNLOAD

Telegram remains frozen.

Future ecosystem features remain documented but do not interrupt the current execution cycle.

39. GOLDEN PRODUCT PRINCIPLE

Janavani should continuously reduce the distance between:

Citizen Problem
        ↓
Understanding
        ↓
Correct Authority
        ↓
Government Action
        ↓
Accountability
        ↓
Better Governance

The platform should evolve from a document-generation tool into a citizen-governance infrastructure layer.

But it must earn that expansion by making the first citizen journey work exceptionally well.

40. FINAL PRODUCT MAP

                         JANAVANI
                            │
             ┌──────────────┴──────────────┐
             │                             │
       CITIZEN ACTION                 GOVERNANCE
             │                         INTELLIGENCE
             │                             │
             ▼                             ▼
        Complaint                    Performance
        Grievance                    Scorecards
        RTI                          Analytics
        Petition                     Feedback
        Appeal                       Patterns
        Follow-up                    Public Intelligence
        Escalation                   Accountability
             │                             │
             └──────────────┬──────────────┘
                            │
                            ▼
                    SHARED PLATFORM
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
   Conversation         Intelligence        Documents
   Workflow             AI / RAG             PDF
   Domain               Classification       Templates
   Services             Office routing       Delivery
   Storage
        │
        ▼
                  INDEPENDENT INTERFACES
        ┌─────────┬──────────┬──────────┬──────────┐
        ▼         ▼          ▼          ▼          ▼
       Web     Telegram    Android      iOS     WhatsApp
                                                    │
                                               Messenger
                                                    │
                                                   API

41. NORTH STAR

Janavani's long-term objective is not to create the largest collection of features.

It is to create the most useful citizen-governance pathway:

A citizen describes reality. Janavani helps transform that reality into informed, structured, actionable engagement with government.

42. EXECUTION DISCIPLINE

The project must always distinguish:

VISION
    ↓
PRODUCT CAPABILITY
    ↓
PLANNED FEATURE
    ↓
CURRENT BUILD
    ↓
VERIFIED FEATURE
    ↓
PRODUCTION FEATURE

A planned capability must never be described as completed.

A prototype must never be described as production-ready.

A future idea must never become an immediate coding task merely because it exists in the roadmap.

43. RELATIONSHIP TO OTHER DOCUMENTS

This document works together with:

docs/SOURCE_OF_TRUTH.md

README.md

ROADMAP.md

planning/PRODUCT_REQUIREMENTS.md

planning/MVP_CONSTITUTION.md

planning/SYSTEM_DOMAIN_MODEL.md

planning/WORKFLOWS.md

planning/WORKFLOW_CONTRACT.md

docs/ARCHITECTURE.md

docs/PROJECT_MAP.md

The Source of Truth defines architecture.

This document defines the product landscape.

The roadmap defines sequencing.

The planning documents define detailed technical/product contracts.

44. LOCKED CURRENT TARGET
BUILD THE WEB APP.

The immediate success condition is:

User
 ↓
Web App
 ↓
Describe issue
 ↓
Guided flow
 ↓
Correct information
 ↓
Complaint
 ↓
PDF
 ↓
Download

Once this works reliably, we proceed to the next capability.

END OF JANAVANI PRODUCT LANDSCAPE
