# JANAVANI — ARCHITECTURE CONSTITUTION

**Version:** 1.1  
**Status:** LOCKED  
**Owner:** Janavani Core Team  
**Purpose:** Canonical architectural principles and boundaries

---

# 1. MISSION

Janavani exists to help citizens transform government-related problems into informed, lawful, documented, and effective civic action while preserving:

- Privacy
- Security
- Dignity
- Transparency
- Simplicity
- Reliability
- Citizen agency

The architecture must support the present MVP while remaining capable of evolving into the broader Janavani platform described in the North Star.

---

# 2. CORE PHILOSOPHY

Janavani is built around the following principles:

- Citizen First
- Privacy at the Core
- Security by Design
- Open Source First
- Simplicity over unnecessary complexity
- Replaceable Components
- Domain-Driven Design
- Workflow-Driven Architecture
- Human-Centered Design
- Long-Term Thinking
- Testability
- Clear Responsibility Boundaries

---

# 3. FIRST PRINCIPLE

## Citizens should describe their problem.

Janavani should progressively discover and structure the complexity required to act on that problem.

The citizen should not be required to understand:

- Government hierarchy
- Departments
- Offices
- Administrative procedures
- Legal procedures
- Forms
- Bureaucratic terminology

Janavani should carry as much of that complexity as reasonably possible.

The interface should therefore remain simple even when the underlying governance workflow is complex.

---

# 4. ARCHITECTURAL OBJECTIVE

The architecture must separate:

```text
Citizen Interfaces
        ↓
Application / Workflow
        ↓
Domain
        ↓
Services / Infrastructure
        ↓
Storage / External Systems
The exact implementation may evolve.
The architectural boundaries must remain clear.
________________________________________
5. HIGH-LEVEL ARCHITECTURE
The Janavani platform consists of several conceptual layers.
                    CITIZEN
                       ↓
                 INTERFACES
                       ↓
          APPLICATION / WORKFLOW
                       ↓
                WORKFLOW ENGINE
                       ↓
                    DOMAIN
                       ↓
                  SERVICES
                       ↓
            STORAGE / INTEGRATIONS
Potential interfaces include:
•	Web 
•	Telegram 
•	WhatsApp 
•	Mobile 
•	Messenger 
•	API 
•	Future interfaces 
The platform capabilities must not belong to any single interface.
________________________________________
6. INTERFACE INDEPENDENCE
Interfaces are entry points into Janavani.
Examples:
Web       ──┐
Telegram   ─┤
WhatsApp   ─┤
Mobile     ─┼──→ Janavani Platform
Messenger  ─┤
API        ─┘
An interface must not become the owner of shared business logic.
The following coupling is prohibited:
Web → Telegram
Telegram → Web
WhatsApp → Telegram
Mobile → Telegram
Domain → Telegram
Domain → Web
Instead:
Interface
    ↓
Shared Janavani Platform
________________________________________
7. CURRENT INTERFACE PRIORITY
Telegram is the first production interface.
The Web App is the current development priority.
Both must consume shared Janavani capabilities.
The Web App must not depend on Telegram.
The Telegram implementation must not become the architectural foundation of the entire platform.
________________________________________
8. DEPENDENCY PRINCIPLE
Dependencies should generally flow toward stable internal abstractions and away from interface-specific implementation details.
Preferred direction:
Interface
    ↓
Application / Workflow
    ↓
Domain
    ↓
Services
    ↓
Infrastructure / Storage
Infrastructure-specific implementations must not force the domain or workflow layers to depend on a particular vendor or interface.
________________________________________
9. DOMAIN INDEPENDENCE
The domain layer must remain independent of:
•	Telegram 
•	Web frameworks 
•	WhatsApp 
•	Databases 
•	Supabase 
•	PostgreSQL 
•	Cloud providers 
•	Specific storage technologies 
The domain represents Janavani's core concepts and rules.
________________________________________
10. FOLDER RESPONSIBILITIES
adapters/
Adapters translate between Janavani and external systems or technologies.
Examples may include:
•	Communication platforms 
•	External APIs 
•	Protocols 
•	Infrastructure integrations 
Adapters should remain thin.
They should not become a second business-logic layer.
________________________________________
conversation/
The conversation layer handles citizen interaction flows where conversational interaction is required.
Responsibilities may include:
•	Conversation state 
•	Interaction sequencing 
•	Input collection 
•	Conversation routing 
•	Interface-specific interaction handling 
Conversation logic should delegate reusable business operations to the platform workflow/application layers.
________________________________________
workflow/
The workflow layer defines citizen and application workflows.
Examples include:
•	Complaint 
•	RTI 
•	Representation 
•	Petition 
•	Appeal 
•	Follow-up 
•	Escalation 
Adding a new workflow should not require rewriting the workflow engine.
________________________________________
engine/
The workflow engine provides workflow execution and orchestration.
Responsibilities may include:
•	Workflow registry 
•	Workflow context 
•	State management 
•	Step execution 
•	Workflow transitions 
The engine should orchestrate workflows.
It should not become a repository for unrelated business rules.
________________________________________
domain/
The domain layer represents core Janavani concepts and business rules.
Examples:
•	Citizen 
•	Issue 
•	Office 
•	Authority 
•	Document 
•	Evidence 
•	Case 
•	Workflow 
Domain logic must remain independent of interfaces and infrastructure.
________________________________________
services/
Services coordinate application operations and integrations.
Examples may include:
•	Office search 
•	Classification 
•	AI assistance 
•	Notifications 
•	Language services 
•	External integrations 
•	Security-related services 
Services should have clearly defined responsibilities.
They must not duplicate domain ownership.
________________________________________
documents/
The document layer owns document composition and generation.
Examples:
•	Complaint 
•	RTI 
•	Representation 
•	Petition 
•	Appeal 
•	PDF generation 
•	Document formatting 
Document generation should be reusable across interfaces.
________________________________________
storage/
The storage layer owns persistence.
Potential implementations include:
•	Supabase 
•	PostgreSQL 
•	Object storage 
•	Other storage systems 
Storage implementations should be replaceable where practical through clear interfaces or service boundaries.
The domain should not directly depend on a specific database implementation.
________________________________________
11. WORKFLOW ARCHITECTURE
The preferred workflow structure is:
Interface
    ↓
Request / Conversation Handling
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
A workflow should remain independent of a specific interface.
The same workflow capability should be reusable by:
•	Web 
•	Telegram 
•	Mobile 
•	API 
•	Future interfaces 
where appropriate.
________________________________________
12. DOCUMENT ARCHITECTURE
The document pipeline should progressively follow:
Citizen Problem
      ↓
Structured Information
      ↓
Authority / Office
      ↓
Evidence
      ↓
Identity
      ↓
Document Builder
      ↓
Document Standards
      ↓
Output
      ↓
Delivery
The document layer owns document creation.
Interfaces should not independently implement document-generation logic.
________________________________________
13. CURRENT CORE CITIZEN FLOW
The current Janavani MVP workflow is conceptually:
Citizen
    ↓
Describe Issue
    ↓
Select Document
    ↓
Select District / Location
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
Download / Delivery
This workflow is the immediate foundation for the Web MVP.
________________________________________
14. AI ARCHITECTURE
AI is a supporting capability, not the owner of Janavani.
The preferred model is:
Citizen Input
      ↓
Issue Structuring
      ↓
Classification
      ↓
Authority Identification
      ↓
Document Assistance
      ↓
Human Review
      ↓
Final Output
AI output must be treated according to the risk of the task.
For legal, civic, or government-related outputs, Janavani should favour:
•	transparency 
•	source grounding 
•	explainability 
•	human review 
•	uncertainty disclosure 
•	controlled workflows 
AI must not silently make consequential decisions on behalf of citizens.
________________________________________
15. SECURITY AT THE CORE
Security is an architectural property.
It is not merely a feature added after implementation.
Core principles include:
•	Secure defaults 
•	Default deny where appropriate 
•	Least privilege 
•	Secrets never hardcoded 
•	Secure communication 
•	Input validation 
•	Authentication and authorization where required 
•	Minimal attack surface 
•	Auditability 
•	Dependency management 
•	Safe error handling 
Security requirements must be considered during design, implementation, testing, and deployment.
________________________________________
16. PRIVACY AT THE CORE
Privacy is a fundamental architectural property.
Janavani should follow:
•	Data minimization 
•	Purpose limitation 
•	Minimal collection 
•	Minimal retention 
•	Privacy-preserving defaults 
•	Consent where appropriate 
•	Identity protection 
•	Secure evidence handling 
•	No unnecessary profiling 
•	No unnecessary surveillance 
•	User control over personal information 
Anonymous or pseudonymous participation should be supported where legally and operationally appropriate.
Not every workflow can be anonymous.
The system must distinguish between:
Anonymous
Pseudonymous
Identified
Verified Identity
rather than treating identity as a single binary state.
________________________________________
17. DATA OWNERSHIP PRINCIPLE
Janavani should move toward architectures in which citizens have meaningful control over their personal data.
This does not mean every current storage implementation is already fully citizen-controlled.
The long-term objective is:
Collect Less
     ↓
Protect Better
     ↓
Give Users More Control
     ↓
Retain Only What Is Necessary
________________________________________
18. REPLACEABILITY PRINCIPLE
Janavani should avoid unnecessary dependence on a single technology.
Examples:
Interface
    ↓
Adapter
    ↓
Platform Capability
A future interface should be capable of replacing an existing interface without requiring the entire domain model to be rewritten.
Similarly:
Application
    ↓
Storage Abstraction
    ↓
Current Storage
should allow future storage evolution where practical.
Replaceability is a design goal, not a claim that every component can be swapped without engineering work.
________________________________________
19. COMPOSITION OVER INHERITANCE
Prefer:
•	small components 
•	explicit interfaces 
•	reusable services 
•	composable workflows 
•	clear contracts 
Avoid deep inheritance hierarchies unless they provide a clear architectural benefit.
________________________________________
20. SINGLE RESPONSIBILITY
Every major module should have one clearly defined primary responsibility.
Examples:
conversation → interaction
workflow     → business workflow
engine       → orchestration
domain       → business concepts/rules
services     → application services
documents    → document generation
storage      → persistence
adapters     → external translation
If two modules begin owning the same responsibility, the duplication should be reviewed.
________________________________________
21. OPEN / CLOSED PRINCIPLE
The architecture should favour extension without unnecessary modification of stable infrastructure.
For example:
Adding a new workflow should primarily involve:
New Workflow
    ↓
Existing Engine
rather than rewriting the workflow engine.
This principle should be applied pragmatically.
________________________________________
22. TESTABILITY
Architectural boundaries should make components testable independently.
Testing should progressively cover:
•	Domain logic 
•	Services 
•	Workflow steps 
•	Workflow execution 
•	Conversation flows 
•	Office search 
•	Document generation 
•	PDF generation 
•	Web integration 
•	Telegram integration 
•	Security-sensitive operations 
A feature is not complete merely because the happy path works manually.
________________________________________
23. STATE MANAGEMENT
State should have a clearly defined owner.
The architecture should avoid:
•	hidden global state 
•	duplicated session state 
•	interface-specific copies of business state 
•	inconsistent workflow state 
Where state must persist, it should pass through the appropriate application/storage boundary.
________________________________________
24. ERROR HANDLING
Errors must be handled deliberately.
The system should:
•	validate inputs 
•	fail safely 
•	avoid exposing secrets 
•	avoid exposing unnecessary internal details 
•	preserve useful diagnostic information in appropriate logs 
•	provide understandable citizen-facing messages 
•	avoid silently losing workflow state 
Error handling should be centralized where practical.
________________________________________
25. OBSERVABILITY
Production systems require appropriate visibility into:
•	errors 
•	workflow failures 
•	service failures 
•	performance 
•	availability 
•	security events 
•	important operational events 
Logging must respect privacy.
Sensitive citizen information must not be unnecessarily written to logs.
________________________________________
26. SIMPLICITY PRINCIPLE
Every feature should make Janavani:
•	simpler, 
•	more trustworthy, 
•	more capable, 
or provide a necessary safety, privacy, security, or reliability improvement.
If a feature does none of these things, it should be questioned before being added.
Technical sophistication is not itself a product benefit.
________________________________________
27. PRIVACY AND SECURITY BEFORE CONVENIENCE
When convenience conflicts with:
•	privacy, 
•	security, 
•	reliability, 
•	legal correctness, 
Janavani should not automatically choose convenience.
The trade-off must be explicitly considered.
________________________________________
28. CURRENT ARCHITECTURAL PRIORITY
The immediate architectural priority is to support the Web MVP using existing Janavani capabilities.
The Web interface should:
Web
 ↓
Shared Janavani Platform
 ↓
Existing Workflow / Services
 ↓
Document Generation
 ↓
PDF
The objective is reuse rather than creating a second implementation of the platform.
________________________________________
29. FUTURE ARCHITECTURAL CAPABILITIES
The architecture should remain capable of supporting future modules such as:
•	RTI 
•	Petitions 
•	Appeals 
•	Evidence management 
•	Follow-up 
•	Escalation 
•	Notifications 
•	Citizen data vault 
•	Consent management 
•	Audit trails 
•	Governance intelligence 
•	Public accountability 
•	Government data integration 
•	Privacy-preserving analytics 
•	Decentralized infrastructure 
These are architectural possibilities, not current implementation claims.
________________________________________
30. DECENTRALIZED TECHNOLOGY
Janavani may evaluate decentralized and privacy-preserving technologies where they provide clear benefits.
Potential areas include:
•	Offline-first communication 
•	Nostr 
•	Matrix 
•	Reticulum 
•	Nym 
•	Decentralized storage 
•	Blockchain 
•	Zero-Knowledge Proofs 
Technology adoption must be justified by actual requirements.
The decision process should be:
Citizen Need
      ↓
Problem Definition
      ↓
Security / Privacy Requirement
      ↓
Architecture Requirement
      ↓
Technology Evaluation
      ↓
Implementation
Not:
Interesting Technology
      ↓
Find Something To Build With It
________________________________________
31. LONG-TERM ARCHITECTURAL VISION
Janavani is not intended to remain merely:
•	a chatbot, 
•	a complaint generator, 
•	a document generator, 
•	or a collection of disconnected civic tools. 
The long-term architectural vision is a broader Citizen Governance Platform in which citizens can move from:
Problem
  ↓
Understanding
  ↓
Evidence
  ↓
Action
  ↓
Government Response
  ↓
Follow-up
  ↓
Escalation
  ↓
Accountability
  ↓
Public Learning
The architecture must evolve toward this vision without compromising the reliability of the current MVP.
________________________________________
32. BUILD THE PRODUCT BEFORE THE ECOSYSTEM
The current architecture must support disciplined execution.
The rule is:
Build the core citizen product before building the full ecosystem.
Do not introduce major architectural complexity merely because it belongs to the long-term vision.
Every major architectural decision should ask:
1.	Does this solve a current problem? 
2.	Does this improve citizen experience? 
3.	Does this improve privacy? 
4.	Does this improve security? 
5.	Does this improve reliability? 
6.	Can it be replaced later? 
7.	Does it create unnecessary coupling? 
8.	Can the simpler architecture solve the problem? 
________________________________________
33. RELATIONSHIP TO OTHER JANAVANI DOCUMENTS
This document is part of the Janavani documentation hierarchy.
JANAVANI_NORTH_STAR.md
        ↓
SOURCE_OF_TRUTH.md
        ↓
JANAVANI_PRODUCT_LANDSCAPE.md
        ↓
ROADMAP.md
        ↓
ARCHITECTURE.md
        ↓
PROJECT_MAP.md
        ↓
REPOSITORY_AUDIT.md
        ↓
RELEASE_1_CHECKLIST.md
Each document has a distinct purpose.
North Star
Defines the long-term strategic destination.
Source of Truth
Defines canonical platform and architectural rules.
Product Landscape
Defines the product ecosystem and capability direction.
Roadmap
Defines execution priorities.
Architecture Constitution
Defines architectural principles and boundaries.
Project Map
Defines repository structure and module ownership.
Repository Audit
Defines current repository condition and technical debt.
Release Checklist
Defines release readiness.
________________________________________
34. FINAL ARCHITECTURAL RULES
The following rules govern Janavani architecture:
1.	Citizen experience comes first. 
2.	Interfaces are replaceable. 
3.	Business logic belongs to the platform, not the interface. 
4.	Domain logic remains infrastructure-independent. 
5.	Each module has a clear responsibility. 
6.	Duplicate responsibilities must be reconciled. 
7.	Privacy is designed in, not added later. 
8.	Security is designed in, not added later. 
9.	Evidence and sensitive data require deliberate handling. 
10.	AI assists workflows; it does not silently replace citizen judgment. 
11.	Technology choices must serve requirements. 
12.	Complexity must be justified. 
13.	Current implementation must not be confused with future vision. 
14.	The MVP must remain reliable while the platform evolves. 
15.	Build the product before the ecosystem. 
________________________________________
END OF JANAVANI ARCHITECTURE CONSTITUTION
