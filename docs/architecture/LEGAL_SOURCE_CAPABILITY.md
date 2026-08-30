# Janavani — Legal/Public Source Capability

## Purpose
Provide reusable, source-grounded public/legal reference data to document generation, authority routing, civic explanation, AI assistance and future access surfaces.

## Architectural rule
Legal/public-source knowledge is a shared capability. No WebApp, Telegram handler, document renderer, AI provider, or other access surface may independently encode legal conclusions or source data.

```text
Public / Legal Source
        ↓
Source Provider
        ↓
Normalization + Verification
        ↓
Legal/Public Source Capability
        ↓
┌───────┼────────┬──────────┐
↓       ↓        ↓          ↓
Case  Document  AI/RAG   Civic guidance
```

## Source-grounding requirements
Every material reference should carry, where available:

- source identifier;
- title;
- jurisdiction;
- source URL or authoritative locator;
- effective/publication date;
- retrieval/verification timestamp;
- verification status;
- provider identity/version;
- scope or applicability;
- confidence/qualification when the source is incomplete or ambiguous.

The capability MUST distinguish source text/facts from generated explanation.

## Provider neutrality
Potential providers include government publications, official datasets, legislation repositories, verified civic datasets, local/community-maintained datasets, and future decentralized providers. Providers are replaceable adapters.

## Safety
The capability must not silently convert an unverified model output into an official legal conclusion. AI may assist with retrieval, classification, summarization or explanation, but authoritative status must come from the source/verification layer.

## Privacy
Public-source lookup should use non-personal, minimized context whenever possible. Private Case data must not be sent to a provider merely to answer a public-source question.

## Reuse
Consumers may include:

- WebApp;
- Telegram Bot;
- Telegram Mini App;
- Android/iOS;
- WhatsApp/Messenger;
- DApp;
- Document generation;
- Authority discovery;
- AI/RAG;
- Agent tools;
- future Janavani surfaces.

No consumer owns this capability.
