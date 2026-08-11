# 🇮🇳 JANAVANI — PRODUCT ROADMAP

**Version:** 1.0  
**Status:** ACTIVE  
**Last Updated:** 11 August 2026
**Purpose:** Execution roadmap for the Janavani platform

---

# 1. VISION

Janavani enables citizens to transform a government-related problem into informed, lawful, and effective civic action through simple, privacy-first digital workflows.

The immediate product journey is:

```text
Citizen Problem
      ↓
Understand the Issue
      ↓
Identify the Relevant Authority
      ↓
Prepare the Appropriate Document
      ↓
Review
      ↓
Generate
      ↓
Submit
      ↓
Track
      ↓
Follow Up
      ↓
Escalate When Appropriate

The long-term objective is to evolve this workflow into a broader citizen-governance platform.

2. ROADMAP STATUS LEGEND
✅ Completed
🟢 Current
🟡 Next
🔵 Planned
⚪ Long-Term
⏸ Deferred
3. PHASE 0 — FOUNDATION
Status

✅ COMPLETED

Repository
 GitHub Repository
 Git Workflow
 Repository Documentation
 Project Structure
 Development Environment
Architecture
 Modular Architecture
 Conversation Layer
 Workflow Layer
 Workflow Engine
 State Registry
 Workflow Registry
 Workflow Context
 Domain Layer
 Services Layer
 Documents Layer
 Storage Layer
Engineering Principles
 Privacy First
 Security by Design
 Replaceable Components
 Separation of Concerns
 Workflow-Driven Architecture
 Open Source First
 Human-Centered Design
4. PHASE 1 — TELEGRAM MVP
Status

🟢 FUNCTIONAL / FROZEN

Telegram is the first production interface for Janavani.

The Telegram implementation should now be treated as a stable interface.

Future development should avoid unnecessary restructuring of the working Telegram flow.

Current Citizen Flow
Citizen
    ↓
Describe Issue
    ↓
Select Document
    ↓
Select District
    ↓
Search Office
    ↓
Select Office / Fallback
    ↓
Identity
    ↓
Preview
    ↓
Document Generation
    ↓
PDF
    ↓
Download
Completed Capabilities
 Telegram interface
 Issue capture
 Conversation states
 Session handling
 Document selection
 District selection
 Office search
 Office fallback
 Identity selection
 Preview
 Complaint generation
 PDF generation
 Document delivery
Telegram Rule

Telegram is an interface.

It must not become the owner of Janavani business logic.

5. PHASE 2 — WEB MVP
Status

🟢 CURRENT PRIORITY

The Web App is the current development focus.

The Web interface must consume Janavani capabilities rather than recreate Telegram-specific business logic.

Goal

Provide the same core citizen capability through a browser.

Citizen
    ↓
Web Interface
    ↓
Janavani Platform
    ↓
Workflow
    ↓
Office / Document Services
    ↓
Complaint
    ↓
PDF
Web MVP Priorities
 Web application entry point
 Citizen issue input
 Document selection
 District/location selection
 Office search
 Identity selection
 Complaint preview
 Complaint generation
 PDF generation
 PDF download
 Error handling
 Responsive citizen interface
 Privacy-first data handling
Web Principle

The Web App must not depend on Telegram.

Web ───────→ Janavani Platform
Telegram ──→ Janavani Platform

Not:

Web → Telegram
6. PHASE 3 — MVP RELIABILITY
Status

🟡 NEXT

Before expanding the feature set, the core citizen journey must become reliable.

Testing
 Unit tests
 Workflow tests
 Conversation tests
 Document tests
 Office search tests
 PDF generation tests
 Web integration tests
 Telegram integration tests
Reliability
 Centralized error handling
 Structured logging
 State validation
 Input validation
 Configuration validation
 Deployment health checks
 Backup strategy
 Monitoring
Security
 Secrets management review
 Rate limiting
 Privacy review
 PII minimization
 Audit logging
 Secure document handling
7. PHASE 4 — CITIZEN EXPERIENCE
Status

🔵 PLANNED

Improve the first citizen journey before creating many new document types.

Identity
 Anonymous mode
 Name-only mode
 Full identity mode
 Clear explanation of data requirements
Evidence
 Photo upload
 Document attachments
 Evidence metadata
 Evidence privacy controls
User Experience
 Better preview
 Edit before generation
 Clear confirmation
 Submission guidance
 Complaint reference ID
 Download history
8. PHASE 5 — AI ASSISTANCE
Status

🔵 PLANNED

AI must remain a controlled assistance layer.

AI is not the product.

AI must not become an unrestricted chatbot inside Janavani.

AI Capabilities
 Issue understanding
 Issue structuring
 Subject generation
 Complaint drafting assistance
 Department classification
 Office recommendation
 Language normalization
 Malayalam / English assistance
 Manglish normalization
AI Safety Principles
 Structured outputs
 Deterministic fallback
 Human review before final document
 No unnecessary personal-data exposure
 Clear distinction between legal information and legal advice
 Confidence handling
 Hallucination safeguards
9. PHASE 6 — DOCUMENT PLATFORM
Status

🔵 PLANNED

Janavani should evolve from a complaint generator into a reusable document composition platform.

Document Types
 Complaint
 Grievance
 RTI
 Representation
 Petition
 Appeal
 Follow-up
 Escalation
Document Composition

Reusable components should eventually include:

Header
Recipient
Subject
Reference
Facts
Legal / Policy Basis
Requests
Documents Requested
Response Request
Acknowledgement
Submission Metadata
Signature
Enclosures
Copy To
Delivery Profiles
 Email
 Registered Post
 Speed Post
 Hand Delivery
 Government Portal
 Future digital channels
10. PHASE 7 — CITIZEN ACTION & TRACKING
Status

🔵 PLANNED

Janavani should eventually continue after document generation.

Generate
   ↓
Submit
   ↓
Reference ID
   ↓
Track
   ↓
Follow Up
   ↓
Escalate
Capabilities
 Complaint ID
 Submission record
 Submission method
 Submission metadata
 Status tracking
 Follow-up reminders
 Follow-up document generation
 Escalation workflow
 Response recording
 Resolution recording
11. PHASE 8 — INTELLIGENT GOVERNANCE SERVICES
Status

⚪ LONG-TERM

Once the core citizen workflow is reliable, Janavani can expand into broader governance intelligence.

Location Intelligence
 District intelligence
 Local-body mapping
 Panchayat / Municipality mapping
 Geographic office matching
 Location-aware routing
Office Intelligence
 Office aliases
 Department mapping
 Confidence scoring
 Office ranking
 Office verification
 Citizen corrections
Government Information
 Public scheme information
 Service information
 Government process guidance
 Public-document intelligence
 Legal-information library
12. PHASE 9 — CITIZEN FEEDBACK & ACCOUNTABILITY
Status

⚪ LONG-TERM

Janavani can eventually create a feedback loop between citizen experience and governance performance.

Capabilities
 Office feedback
 Service ratings
 Response-time data
 Resolution data
 Department-level patterns
 Geographic patterns
 Citizen feedback analysis
Accountability Intelligence
 Office performance indicators
 Department performance indicators
 Public service responsiveness
 Complaint-resolution patterns
 Public accountability dashboards

All public-facing accountability features must have strong verification, privacy, anti-abuse, and fairness safeguards.

13. PHASE 10 — MULTI-INTERFACE PLATFORM
Status

⚪ LONG-TERM

Janavani should eventually support multiple independent interfaces.

Interfaces
 Telegram
[🟢] Web
 Android
 iOS
 WhatsApp
 Messenger
 Public API
Architecture Rule

Every interface must consume the shared Janavani platform.

                 Janavani Platform
                       │
        ┌──────────────┼──────────────┐
        ↓              ↓              ↓
     Telegram         Web          Mobile
        ↓              ↓              ↓
        └──────────────┼──────────────┘
                       ↓
                 Shared Services

No interface should become the dependency of another interface.

14. PHASE 11 — COMMUNITY & DATA QUALITY
Status

⚪ LONG-TERM

Citizen participation can eventually improve the quality of Janavani's governance data.

Capabilities
 Volunteer participation
 Office verification
 Office suggestions
 Data correction
 Data moderation
 Community validation
 Source verification
15. PHASE 12 — SPECIALIZED GOVERNANCE SERVICES
Status

⚪ LONG-TERM / RESEARCH

Future specialized modules may include:

 Land / Bhu-Janavani
 Legal document demystification
 RTI assistance
 Public-service entitlement checking
 Ration entitlement auditing
 Public project intelligence
 Governance data analysis
 Public accountability intelligence

These are future capabilities.

They must not delay completion of the core citizen workflow.

16. CURRENTLY DEFERRED TECHNOLOGIES

The following should remain research / future considerations rather than MVP priorities:

Blockchain
IPFS
Nostr
Nym
Decentralized identity
Advanced cryptographic infrastructure
Large-scale autonomous AI agents

Technology should only be introduced when a demonstrated citizen or system requirement justifies it.

17. CURRENT TECHNICAL DEBT

These items should be addressed through controlled maintenance rather than another architecture rewrite.

 Review remaining legacy code
 Verify duplicate implementations
 Complete automated test coverage
 Improve error handling
 Improve structured logging
 Review deployment configuration
 Audit GitHub workflows
 Verify configuration consistency
 Verify unused dependencies
 Verify deprecated modules before deletion

Nothing should be deleted solely because it appears old.

Deletion requires:

Replacement exists.
Imports are removed.
Tests pass.
Runtime is verified.
Git history is preserved.
18. DOCUMENTATION AUTHORITY

Janavani documentation follows this hierarchy:

JANAVANI NORTH STAR
        ↓
SOURCE OF TRUTH
        ↓
ARCHITECTURE
        ↓
PRODUCT LANDSCAPE
        ↓
ROADMAP
        ↓
PROJECT MAP
        ↓
RELEASE CHECKLIST
        ↓
CODE

Each document answers a different question.

North Star

Why does Janavani exist?

Source of Truth

What architectural principles govern Janavani?

Architecture

How is the system structured?

Product Landscape

What can Janavani become?

Roadmap

What are we building and when?

Project Map

Where does the code live?

Release Checklist

What is actually complete?

Code

What is actually implemented?

19. EXECUTION RULE

From this point forward:

One citizen journey before one new platform capability.

Do not begin a new major feature while an existing citizen journey remains unreliable.

20. CURRENT EXECUTION PRIORITY
🔴 PRIORITY 1

Complete and stabilize the Web MVP.

Web
 ↓
Issue
 ↓
Document
 ↓
Location
 ↓
Office
 ↓
Identity
 ↓
Preview
 ↓
Complaint
 ↓
PDF
 ↓
Download
🟠 PRIORITY 2

Make the shared complaint capability reliable across Telegram and Web.

🟡 PRIORITY 3

Testing, security, privacy, logging, and operational reliability.

🟢 PRIORITY 4

Evidence, tracking, follow-up, and escalation.

🔵 PRIORITY 5

AI assistance and multilingual capabilities.

⚪ PRIORITY 6

Governance intelligence and the broader Janavani ecosystem.

21. MVP DEFINITION

The Janavani MVP is considered complete when a citizen can reliably:

Describe a government-related problem.
Select or receive the appropriate document type.
Provide only the necessary information.
Identify or receive a relevant authority.
Review the resulting document.
Select the appropriate identity mode.
Generate a professional document.
Download the document.
Understand how to submit it.

The MVP must work reliably through the current supported interface(s).

22. NORTH STAR

The immediate product is:

Citizen Problem → Government-Ready Document

The long-term platform is:

Citizen Reality → Understanding → Evidence → Action → Government Response → Follow-up → Accountability → Public Learning

The second objective must never cause us to neglect the first.

23. CURRENT RULE
BUILD THE PRODUCT BEFORE THE ECOSYSTEM.

Do not build the future Janavani ecosystem before the core citizen journey is reliable.

Every major development decision should ask:

Does this help a citizen?
Does this preserve privacy?
Does this improve reliability?
Does this reduce unnecessary complexity?
Does this move Janavani toward the next verified milestone?

If not, defer it.

END
