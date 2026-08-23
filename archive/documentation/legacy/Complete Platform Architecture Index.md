# ARCHIVED DOCUMENT

This document is retained for historical traceability only.

**Archived:** 23 August 2026
**Reason:** Superseded by the canonical ecosystem documentation hierarchy.

Original document preserved below.

---

Complete Platform Architecture Index Reference
Your workspace repository layout is now fully built, secure, and ready for deployment. Below is your final file system structure:
• janavani/docker-compose.yml — Runs your multi-container environment (FastHTML frontend, FastAPI AI agent, Redis cache, and NGINX security proxy) as a single, coordinated system.
• janavani/nginx.conf — Your public security firewall that manages SSL/TLS encryption and prevents web application scanning attempts.
• janavani/run_all_tests.sh — A single script that runs your complete test suite, verifying your code privacy parameters before updates go live.
• janavani/deploy.sh — Handles smooth updates on your live servers without causing service interruptions for citizens.
• janavani/src/web_mvp/main.py — The standalone web interface layout built with FastHTML to process civic grievances and display live bill updates.
• janavani/src/utils/feedback_validators.py — Validates public review formatting and strips malicious script injections out of comments.
• janavani/src/core/representatives_directory.py — A built-in directory containing correct communication address logs for MPs, MLAs, and LSGD offices across South and North East India.
• janavani/src/core/legislative_monitor.py — Tracks proposed bills and screens text clauses against your fundamental "Golden Triangle" constitutional protections.
• janavani/src/core/vernacular_headers.py — Pre-fills traditional administrative headings in local regional languages (Malayalam, Kannada, Tamil, Assamese) depending on the target state profile.
• janavani/src/services/document_generator.py — Compiles structured legal letters into both print-ready PDFs and editable Word documents (.docx).
