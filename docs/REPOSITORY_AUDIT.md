# Janavani Repository Audit

Version: 1.0

---

# Active Modules

| Module | Status | Notes |
|---------|--------|------|
| conversation | ✅ Active | Conversation handling |
| workflow | ✅ Active | Business workflows |
| engine | ✅ Active | Workflow engine |
| services | ✅ Active | Business services |
| storage | ✅ Active | Persistence |
| domain | ✅ Active | Domain model |

---

# Legacy Modules

| Module | Replacement | Status |
|---------|-------------|--------|
| database | storage | Review |
| tools | services | Review |
| bot.py | src/main.py | Review |
| bot_async.py | src/main.py | Review |

---

# Duplicate Responsibilities

| Area | Current | Future |
|------|----------|---------|
| Workflow | conversation/workflow.py | workflow/ |
| Database | database/ | storage/ |
| PDF | tools/generate_pdf.py | services/document_service.py |
| Search | tools/search_directory.py | services/search_service.py |

---

# Technical Debt

(To be filled during audit)

---

# Recommended Actions

(To be filled)

---

# Safe To Delete

(To be filled after verification)
