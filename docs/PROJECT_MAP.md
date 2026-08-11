# JANAVANI — PROJECT MAP

**Version:** 1.1  
**Status:** ACTIVE  
**Repository:** netzen-abm/janavani  
**Branch:** main  
**Last Updated:** 11 August 2026  
**Purpose:** Repository structure, ownership boundaries, and architectural navigation

---

# 1. PURPOSE

This document provides a practical map of the Janavani repository.

It answers:

1. Where does production code live?
2. What is the responsibility of each major directory?
3. Where should new code be placed?
4. How do the major platform layers relate?
5. Which areas are current, legacy, or future?
6. What architectural boundaries must be preserved?

This document is a repository navigation and ownership document.

It does not replace:

- `docs/SOURCE_OF_TRUTH.md`
- `docs/ARCHITECTURE.md`
- `docs/JANAVANI_NORTH_STAR.md`
- `docs/JANAVANI_PRODUCT_LANDSCAPE.md`
- `docs/REPOSITORY_RULES.md`
- `docs/REPOSITORY_AUDIT.md`
- `ROADMAP.md`

---

# 2. JANAVANI MISSION

Janavani is a privacy-first Citizen Governance Platform.

Its purpose is to help citizens transform government-related problems into informed, lawful, documented, and effective civic action.

The platform is designed to progressively support:

```text
Citizen Problem
      ↓
Understanding
      ↓
Relevant Authority
      ↓
Evidence
      ↓
Legal / Civic Action
      ↓
Document
      ↓
Submission
      ↓
Tracking
      ↓
Follow-up
      ↓
Escalation
      ↓
Accountability
The current product is narrower than the long-term vision.
The immediate priority is to build reliable citizen workflows before expanding into the broader Janavani ecosystem.
________________________________________
3. ENGINEERING PRINCIPLES
Janavani follows these principles:
1.	Privacy at the Core 
2.	Security by Default 
3.	Open Source First 
4.	Offline First where practical 
5.	Data Minimization 
6.	User Data Ownership as a long-term design goal 
7.	Modular Architecture 
8.	Replaceability over Coupling 
9.	Testability over Convenience 
10.	Human-Centered Design 
11.	Workflow-Driven Architecture 
12.	Clear Responsibility Boundaries 
13.	Evidence Before Destructive Changes 
14.	Documentation Before Complexity 
________________________________________
4. REPOSITORY STRUCTURE
The current repository contains the following major areas:
janavani/
│
├── src/
├── docs/
├── planning/
├── database/
├── scripts/
├── archive/
├── api/
├── tests/
│
├── Dockerfile
├── docker-compose.yml
├── docker-compose.decentralized.yml
├── render.yaml
├── Procfile
├── requirements.txt
├── pyproject.toml
├── README.md
└── ROADMAP.md
Additional files and directories may exist.
This map records the intended responsibility of the major areas.
________________________________________
5. src/ — APPLICATION CODE
src/ is the primary application source tree.
Current major areas include:
src/
├── adapters/
├── app/
├── bot_telegram.py
├── bot_whatsapp.py
├── bot_messenger.py
├── commands/
├── conversation/
├── core/
├── documents/
├── domain/
├── engine/
├── legal_brain.py
├── models/
├── services/
├── storage/
├── utils/
├── web/
├── web.py
└── workflow/
The exact contents may evolve.
New production application logic should normally belong inside src/.
Before adding a new top-level source directory, determine whether an existing module already owns the responsibility.
________________________________________
6. conversation/
Responsibility
The conversation layer manages citizen interaction flows.
It may contain:
•	conversation steps 
•	conversation state handling 
•	routing 
•	session interaction 
•	interface-specific conversation orchestration 
The conversation layer should not become the owner of core business rules that are required by multiple interfaces.
Principle
Conversation
    ↓
Platform Workflow
Not:
Business Logic
    ↓
Telegram Conversation
________________________________________
7. workflow/
Responsibility
The workflow layer defines Janavani business workflows.
Examples include future workflows such as:
•	complaint workflow 
•	RTI workflow 
•	petition workflow 
•	appeal workflow 
•	follow-up workflow 
•	escalation workflow 
Workflow logic should remain independent of a specific interface.
________________________________________
8. engine/
Responsibility
The engine provides workflow orchestration and execution infrastructure.
Its responsibilities may include:
•	workflow execution 
•	state transitions 
•	workflow registry 
•	workflow context 
•	step execution 
The engine should orchestrate.
It should not become a dumping ground for business logic.
________________________________________
9. domain/
Responsibility
The domain layer represents core Janavani business concepts and models.
Examples may include:
•	citizen 
•	complaint 
•	office 
•	authority 
•	document 
•	evidence 
•	workflow 
•	case 
Domain concepts should remain independent of Telegram, Web, WhatsApp, or other interfaces.
________________________________________
10. services/
Responsibility
Services coordinate application-level operations and integrations.
Examples may include:
•	office lookup 
•	document services 
•	AI services 
•	external service integrations 
•	notification services 
•	government-data integrations 
Services should not duplicate domain responsibilities.
They should coordinate reusable platform capabilities.
________________________________________
11. documents/
Responsibility
The document layer owns document composition and generation.
Examples:
•	complaint documents 
•	RTI documents 
•	representation letters 
•	petitions 
•	appeals 
•	PDF generation 
•	future document formats 
The long-term architectural direction is:
Structured Case
      ↓
Document Builder
      ↓
Document Standards
      ↓
Output Format
Document generation should not be duplicated across interfaces.
________________________________________
12. storage/
Responsibility
storage/ is the intended persistence boundary.
It should own:
•	persistence operations 
•	data access 
•	repositories 
•	storage adapters 
•	future database implementations 
Business logic should not directly manipulate storage where a storage abstraction is appropriate.
________________________________________
13. adapters/
Responsibility
Adapters connect Janavani to external interfaces or technologies.
Examples may include:
•	external APIs 
•	communication systems 
•	protocol adapters 
•	future decentralized infrastructure 
Adapters should remain thin.
They should translate between external systems and Janavani's internal interfaces.
________________________________________
14. core/
Responsibility
core/ contains shared application configuration and foundational components.
Examples may include:
•	configuration 
•	application-wide constants 
•	foundational utilities 
Core code must not become a second business-logic layer.
________________________________________
15. commands/
Responsibility
commands/ contains interface command handlers where applicable.
Examples:
/start
/search
/rate
/complaint
/check
Command handlers should remain thin and delegate actual business operations to the appropriate platform layers.
________________________________________
16. models/
Responsibility
models/ contains application data models where applicable.
Models should have a clearly defined responsibility and should not duplicate domain concepts without justification.
If two model systems begin representing the same concept, they must be reconciled rather than allowed to diverge indefinitely.
________________________________________
17. web/ AND WEB APPLICATION
The Web interface is the current development priority.
The Web application should consume shared Janavani capabilities.
Correct architecture:
Citizen
   ↓
Web Interface
   ↓
Janavani Platform
   ↓
Workflow
   ↓
Services / Domain / Documents / Storage
Incorrect architecture:
Web
 ↓
Telegram
The Web interface must not depend on Telegram.
________________________________________
18. TELEGRAM INTERFACE
Telegram is the first Janavani interface.
Current flow:
Citizen
   ↓
Telegram
   ↓
Conversation
   ↓
Workflow
   ↓
Office / Document Services
   ↓
Complaint
   ↓
Preview
   ↓
PDF
   ↓
Delivery
Telegram is an interface, not the Janavani platform itself.
Future interfaces should consume the same platform capabilities independently.
________________________________________
19. FUTURE INTERFACES
Potential future interfaces include:
Web
Telegram
WhatsApp
Android
iOS
Messenger
API
Future interfaces
The architectural principle is:
             JANAVANI PLATFORM
                    ↑
        ┌───────────┼───────────┐
        ↑           ↑           ↑
       Web       Telegram    WhatsApp
        ↑           ↑           ↑
      Mobile      Future      API
No interface should depend on another interface.
________________________________________
20. database/
Current Role
database/ currently contains static datasets and data resources used by the project.
Examples may include:
•	CSV 
•	JSON 
•	JSONL 
•	seed data 
•	reference datasets 
The directory should not become a location for application business logic.
Long-term persistence responsibilities should be progressively consolidated under storage/ where appropriate.
________________________________________
21. api/
Responsibility
api/ contains API-related infrastructure and endpoints where applicable.
The API layer should expose Janavani capabilities without duplicating business logic.
Preferred pattern:
API
 ↓
Platform Service / Workflow
 ↓
Domain / Storage
Not:
API
 ↓
Independent Business Logic
________________________________________
22. scripts/
Responsibility
scripts/ contains development and operational utilities.
Examples:
•	migration utilities 
•	inspection tools 
•	maintenance scripts 
•	data preparation 
•	development helpers 
Scripts should not become hidden production application entry points.
They should be explicitly documented when they affect production data or deployment.
________________________________________
23. tests/
Responsibility
tests/ contains automated verification.
Testing should progressively cover:
•	unit behaviour 
•	workflows 
•	conversation flows 
•	services 
•	office lookup 
•	document generation 
•	PDF generation 
•	Web integration 
•	Telegram integration 
•	regression scenarios 
The goal is to make the core citizen journey reproducible and verifiable.
________________________________________
24. docs/
Responsibility
docs/ contains architecture and engineering documentation.
Important documents include:
docs/
├── JANAVANI_NORTH_STAR.md
├── JANAVANI_PRODUCT_LANDSCAPE.md
├── SOURCE_OF_TRUTH.md
├── ARCHITECTURE.md
├── ARCHITECTURE_DECISIONS.md
├── PROJECT_MAP.md
├── REPOSITORY_AUDIT.md
├── REPOSITORY_RULES.md
├── SYSTEM_QUALITY_STANDARD.md
├── RELEASE_1_CHECKLIST.md
├── DEVELOPER_GUIDE.md
└── ...
Documentation should describe verified architecture and clearly distinguish future intentions from current implementation.
________________________________________
25. planning/
Responsibility
planning/ contains strategic and exploratory material.
Examples:
•	research 
•	future architecture 
•	product concepts 
•	founder-level planning 
•	future modules 
•	experiments 
•	long-term ecosystem planning 
Planning documents are not production code.
________________________________________
26. archive/
Responsibility
archive/ contains deprecated or historical material.
Archived code should not be imported by active production code.
Before moving code into archive/, verify that it is not an active dependency.
Archive is for preservation, not an alternative runtime.
________________________________________
27. APPLICATION ENTRY POINTS
The repository contains multiple interface/application entry points.
The architecture should distinguish between:
Platform/application entry
src/main.py
Interface entry points
Examples:
src/bot_telegram.py
src/bot_whatsapp.py
src/bot_messenger.py
src/web.py
The existence of multiple entry points is not inherently an architectural problem.
The important rule is that they must consume shared Janavani capabilities rather than duplicate business logic.
________________________________________
28. WORKFLOW ARCHITECTURE
The intended workflow architecture is:
Interface
    ↓
Conversation / Request Handling
    ↓
Workflow
    ↓
Workflow Engine
    ↓
Workflow Context
    ↓
Workflow Step
    ↓
Domain / Services
    ↓
Document / Delivery
A workflow should not bypass the platform architecture merely because one interface makes it convenient.
________________________________________
29. CURRENT CITIZEN DOCUMENT FLOW
The current core product journey is:
Citizen Problem
      ↓
Issue Capture
      ↓
Document Selection
      ↓
Location / District
      ↓
Office Identification
      ↓
Office Selection / Fallback
      ↓
Identity
      ↓
Complaint Construction
      ↓
Preview
      ↓
Document Generation
      ↓
PDF
      ↓
Download / Delivery
This is the current foundation for the Web MVP.
________________________________________
30. FUTURE INTELLIGENCE FLOW
AI should be introduced as a controlled platform capability.
Target architecture:
Citizen Input
      ↓
Issue Structuring
      ↓
Legal / Civic Classification
      ↓
Authority Identification
      ↓
Document Assistance
      ↓
Human Review
      ↓
Final Document
AI is not intended to become an unrestricted general-purpose chatbot within Janavani.
The current AI direction is professional, legal/civic, controlled assistance.
________________________________________
31. FUTURE EVIDENCE FLOW
Future evidence capabilities may include:
Citizen Evidence
      ↓
Validation
      ↓
Metadata Minimization
      ↓
Secure Storage
      ↓
Case / Complaint
      ↓
Document
Potential evidence types include:
•	photographs 
•	documents 
•	screenshots 
•	structured records 
•	other supported evidence 
Evidence handling must follow privacy and security requirements.
________________________________________
32. FUTURE GOVERNANCE INTELLIGENCE
The long-term Janavani platform may include:
•	citizen feedback 
•	office performance indicators 
•	service-delivery metrics 
•	complaint trends 
•	government performance information 
•	public budget information 
•	public project information 
•	representative performance information 
•	public accountability tools 
These are future platform capabilities.
They must not be treated as current MVP functionality unless implemented and verified.
________________________________________
33. FUTURE LEGAL / CIVIC SERVICES
Potential future modules include:
Complaint
RTI
Representation
Grievance Petition
Appeal
Follow-up
Escalation
Legal Document Analysis
Public Notice Analysis
Government Order Analysis
Each module should be implemented as a controlled workflow rather than unrestricted conversational AI.
________________________________________
34. FUTURE PRIVACY / SECURITY SERVICES
Potential future platform capabilities include:
Identity Protection
Consent Management
Data Minimization
Citizen Data Vault
Secure Evidence Storage
Audit Trail
Encryption
Access Control
Privacy-Preserving Analytics
Zero-Knowledge Techniques
These are future capabilities unless explicitly implemented and verified.
________________________________________
35. FUTURE DECENTRALIZED INFRASTRUCTURE
The long-term Janavani vision may evaluate decentralized technologies where they provide measurable benefits.
Potential technologies include:
•	Nostr 
•	Matrix 
•	Reticulum 
•	Nym 
•	blockchain systems 
•	zero-knowledge proofs 
•	decentralized storage 
•	offline-first communication 
•	other open protocols 
These technologies must not be introduced merely because they are technically interesting.
Each must pass:
Citizen Benefit
      ↓
Privacy Benefit
      ↓
Security Benefit
      ↓
Reliability
      ↓
Operational Feasibility
      ↓
Maintainability
________________________________________
36. FUTURE MODULES
Potential future modules include:
Identity Protection
Evidence
RTI
Petition
Appeal
Follow-up
Escalation
Email Delivery
Digital Signature
Audit Trail
Citizen Vault
Consent Manager
Notification Engine
Knowledge Graph
Controlled AI Legal Assistance
Open Government Data
Governance Intelligence
Bhu-Janavani
Citizen Performance Feedback
Public Accountability
These belong to the product roadmap and must not be interpreted as current implementation status.
________________________________________
37. OWNERSHIP RULES
Each major layer has a primary responsibility.
Layer	Primary Responsibility
conversation/	Citizen interaction flow
workflow/	Business workflows
engine/	Workflow orchestration
domain/	Core business concepts
services/	Application services and integrations
documents/	Document composition and generation
storage/	Persistence
adapters/	External-system translation
commands/	Interface command handling
web/	Web interface
scripts/	Development/operational utilities
tests/	Verification
docs/	Architecture and engineering documentation
planning/	Strategic/future planning
archive/	Deprecated historical material
________________________________________
38. DEPENDENCY DIRECTION
The preferred dependency direction is:
Interfaces
    ↓
Workflow / Application
    ↓
Domain
    ↓
Services
    ↓
Storage / External Systems
The exact dependency graph may vary by implementation.
However, the following principle remains mandatory:
Lower-level infrastructure must not force the platform to become dependent on a specific user interface.
________________________________________
39. FORBIDDEN COUPLING
The following patterns should be avoided:
Web → Telegram
Telegram → Web
WhatsApp → Telegram
Mobile → Telegram
Domain → Telegram
Domain → Web
Domain → UI
Instead:
Interface
    ↓
Shared Janavani Platform
________________________________________
40. NEW FILE RULE
Before adding a new file, ask:
1.	Does an existing module already own this responsibility? 
2.	Is a new module actually necessary? 
3.	Does the file belong in src/, docs/, planning/, scripts/, tests/, or another existing area? 
4.	Will it create duplicate responsibility? 
5.	Does it introduce unnecessary coupling? 
6.	Does it require an architecture decision? 
7.	Does the relevant documentation need updating? 
Do not create new folders merely to avoid understanding the existing architecture.
________________________________________
41. PROJECT MAP MAINTENANCE RULE
The Project Map should be updated when a structural change materially affects:
•	directory ownership 
•	application entry points 
•	architectural boundaries 
•	major modules 
•	dependency direction 
•	production source locations 
Routine feature changes do not require rewriting this document.
The rule is:
Update the Project Map when the architecture changes, not every time a file changes.
________________________________________
42. RELATIONSHIP WITH OTHER DOCUMENTS
The Janavani documentation hierarchy is:
JANAVANI_NORTH_STAR.md
        ↓
SOURCE_OF_TRUTH.md
        ↓
JANAVANI_PRODUCT_LANDSCAPE.md
        ↓
ROADMAP.md
        ↓
PROJECT_MAP.md
        ↓
REPOSITORY_AUDIT.md
        ↓
RELEASE_1_CHECKLIST.md
        ↓
CODE + TESTS
Each document has a different purpose.
North Star
Defines long-term strategic destination.
Source of Truth
Defines canonical architectural principles and rules.
Product Landscape
Defines product capabilities and ecosystem direction.
Roadmap
Defines execution sequence and priorities.
Project Map
Defines repository structure and ownership.
Repository Audit
Records technical debt and repository condition.
Release Checklist
Records release readiness.
Code and Tests
Provide the final implementation evidence.
________________________________________
43. CURRENT DEVELOPMENT PRIORITY
The current priority is:
WEB MVP
The immediate objective is:
Citizen
 ↓
Web
 ↓
Describe Problem
 ↓
Select / Determine Document
 ↓
Location
 ↓
Office
 ↓
Identity
 ↓
Preview
 ↓
Generate
 ↓
PDF
 ↓
Download
The Web MVP should reuse existing Janavani capabilities wherever possible.
________________________________________
44. ARCHITECTURAL DISCIPLINE
Janavani should avoid premature complexity.
Before introducing a new technology, framework, service, database, protocol, or architectural layer, ask:
Why is it required?
What citizen problem does it solve?
Can the current architecture solve it?
Does it introduce coupling?
Does it increase privacy risk?
Does it increase operational complexity?
Can it be replaced later?
How will it be tested?
How will it be deployed?
If the answer is unclear:
Defer the technology.
________________________________________
45. FINAL RULE
The Project Map exists to keep the repository understandable.
The governing principles are:
One responsibility per module.
One canonical implementation per responsibility.
Interfaces remain replaceable.
Business logic remains platform-owned.
Storage remains behind a clear boundary.
Documentation describes verified architecture.
Future architecture must not be mistaken for current implementation.
Build the product before the ecosystem.
________________________________________
END OF JANAVANI PROJECT MAP

