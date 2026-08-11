# ðŸ‡®ðŸ‡³ JANAVANI â€” PRODUCT ROADMAP

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
      â†“
Understand the Issue
      â†“
Identify the Relevant Authority
      â†“
Prepare the Appropriate Document
      â†“
Review
      â†“
Generate
      â†“
Submit
      â†“
Track
      â†“
Follow Up
      â†“
Escalate When Appropriate

The long-term objective is to evolve this workflow into a broader citizen-governance platform.

2. ROADMAP STATUS LEGEND
âœ… Completed
ðŸŸ¢ Current
ðŸŸ¡ Next
ðŸ”µ Planned
âšª Long-Term
â¸ Deferred
3. PHASE 0 â€” FOUNDATION
Status

âœ… COMPLETED

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
4. PHASE 1 â€” TELEGRAM MVP
Status

ðŸŸ¢ FUNCTIONAL / FROZEN

Telegram is the first production interface for Janavani.

The Telegram implementation should now be treated as a stable interface.

Future development should avoid unnecessary restructuring of the working Telegram flow.

Current Citizen Flow
Citizen
    â†“
Describe Issue
    â†“
Select Document
    â†“
Select District
    â†“
Search Office
    â†“
Select Office / Fallback
    â†“
Identity
    â†“
Preview
    â†“
Document Generation
    â†“
PDF
    â†“
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

5. PHASE 2 â€” WEB MVP
Status

ðŸŸ¢ CURRENT PRIORITY

The Web App is the current development focus.

The Web interface must consume Janavani capabilities rather than recreate Telegram-specific business logic.

Goal

Provide the same core citizen capability through a browser.

Citizen
    â†“
Web Interface
    â†“
Janavani Platform
    â†“
Workflow
    â†“
Office / Document Services
    â†“
Complaint
    â†“
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

Web â”€â”€â”€â”€â”€â”€â”€â†’ Janavani Platform
Telegram â”€â”€â†’ Janavani Platform

Not:

Web â†’ Telegram
6. PHASE 3 â€” MVP RELIABILITY
Status

ðŸŸ¡ NEXT

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
7. PHASE 4 â€” CITIZEN EXPERIENCE
Status

ðŸ”µ PLANNED

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
8. PHASE 5 â€” AI ASSISTANCE
Status

ðŸ”µ PLANNED

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
9. PHASE 6 â€” DOCUMENT PLATFORM
Status

ðŸ”µ PLANNED

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
10. PHASE 7 â€” CITIZEN ACTION & TRACKING
Status

ðŸ”µ PLANNED

Janavani should eventually continue after document generation.

Generate
   â†“
Submit
   â†“
Reference ID
   â†“
Track
   â†“
Follow Up
   â†“
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
11. PHASE 8 â€” INTELLIGENT GOVERNANCE SERVICES
Status

âšª LONG-TERM

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
12. PHASE 9 â€” CITIZEN FEEDBACK & ACCOUNTABILITY
Status

âšª LONG-TERM

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

13. PHASE 10 â€” MULTI-INTERFACE PLATFORM
Status

âšª LONG-TERM

Janavani should eventually support multiple independent interfaces.

Interfaces
 Telegram
[ðŸŸ¢] Web
 Android
 iOS
 WhatsApp
 Messenger
 Public API
Architecture Rule

Every interface must consume the shared Janavani platform.

                 Janavani Platform
                       â”‚
        â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
        â†“              â†“              â†“
     Telegram         Web          Mobile
        â†“              â†“              â†“
        â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                       â†“
                 Shared Services

No interface should become the dependency of another interface.

14. PHASE 11 â€” COMMUNITY & DATA QUALITY
Status

âšª LONG-TERM

Citizen participation can eventually improve the quality of Janavani's governance data.

Capabilities
 Volunteer participation
 Office verification
 Office suggestions
 Data correction
 Data moderation
 Community validation
 Source verification
15. PHASE 12 â€” SPECIALIZED GOVERNANCE SERVICES
Status

âšª LONG-TERM / RESEARCH

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
        â†“
SOURCE OF TRUTH
        â†“
ARCHITECTURE
        â†“
PRODUCT LANDSCAPE
        â†“
ROADMAP
        â†“
PROJECT MAP
        â†“
RELEASE CHECKLIST
        â†“
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
ðŸ”´ PRIORITY 1

Complete and stabilize the Web MVP.

Web
 â†“
Issue
 â†“
Document
 â†“
Location
 â†“
Office
 â†“
Identity
 â†“
Preview
 â†“
Complaint
 â†“
PDF
 â†“
Download
ðŸŸ  PRIORITY 2

Make the shared complaint capability reliable across Telegram and Web.

ðŸŸ¡ PRIORITY 3

Testing, security, privacy, logging, and operational reliability.

ðŸŸ¢ PRIORITY 4

Evidence, tracking, follow-up, and escalation.

ðŸ”µ PRIORITY 5

AI assistance and multilingual capabilities.

âšª PRIORITY 6

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

Citizen Problem â†’ Government-Ready Document

The long-term platform is:

Citizen Reality â†’ Understanding â†’ Evidence â†’ Action â†’ Government Response â†’ Follow-up â†’ Accountability â†’ Public Learning

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
