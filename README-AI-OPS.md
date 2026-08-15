# Janavani Agentic AI Operations, Safety & Privacy Verification Manual

This document details the processes required to run, audit, and verify the independent Janavani Agentic AI service layer.

## 🛡️ Core Verification Matrix

### 1. Confirming Local De-identification (Privacy-by-Default)
To verify that personal data (PII) is intercepted locally and never leaves the environment container, execute the verification suite:
```bash
pytest tests/test_ai_agent_components.py -k test_privacy_preserving_tokenizer_scrubbing -v
```
* **Expected Result:** The tokenizer converts Indian identification formats (Aadhaar, PAN, phone numbers) into abstract strings (`[REDACTED_AADHAAR]`) before issuing outbound requests.

### 2. Confirming Anti-Chat Enforcement (Safety-by-Design)
To verify that the platform rejects general chat, greeting loops, or generic search strings:
```bash
pytest tests/test_ai_agent_components.py -k test_legal_document_schema_anti_chat_enforcement -v
```
* **Expected Result:** Inputs that fall outside the scope of structural public complaints fail validation, return `is_valid_civic_issue: false`, and trigger an immediate termination response.

---

## 🚀 Live Production Initialization Sequence

Run this command sequence on your production host environment to bring up your infrastructure safely:

```bash
# 1. Inject server variables securely into host memory profiles
export OPENROUTER_API_KEY="your-production-token"
export HUGGINGFACE_API_KEY="your-production-token"

# 2. Make deployment files executable and run the update engine
chmod +x deploy.sh
./deploy.sh
```

---

## 🔍 Non-Intrusive Live Debugging Procedures

If one of your interfaces (such as the Telegram bot container or the Web UI) experiences a connection drop, check the isolated logs without exposing user content:

```bash
# Audit NGINX traffic footprints to inspect network routing errors or potential DoS scans
docker compose logs reverse-proxy-gateway --tail=100

# Inspect internal application layer exit statuses without recording raw user input strings
docker compose logs ai-agent-service --tail=100
```
