# ARCHIVED DOCUMENT

**Archived:** 23 August 2026
**Reason:** Superseded by canonical deployment and architecture documentation.

Retained as historical evidence only. The original document used MVP-era terminology and an older FastHTML/AI-agent topology. Do not treat it as current runtime architecture.

---

[Historical content preserved]

                        [ Public HTTP Requests (Port 8080) ]
                                         │
                                         ▼
                     ┌──────────────────────────────────────┐
                     │ Janavani FastHTML Frontend Container │
                     └───────────────────┬──────────────────┘
                                         │ (Internal Bridged API Calls)
                                         ▼
[ Public HTTPS (443) ] ──► [ NGINX Proxy Gateway ] ──► [ Python AI Agent Core ]

Historical note: this topology predates the current capability-first, multi-interface ecosystem architecture.
