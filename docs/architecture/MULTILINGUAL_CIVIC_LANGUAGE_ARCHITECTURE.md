# Multilingual Civic Language Architecture

## Goal

A citizen should be able to explain a civic problem in a supported Indian language or English, receive the workflow in a chosen language, and generate a document in a chosen output language without creating language-specific business logic.

## Separate four concerns

```text
Input language
      ↓
Semantic civic representation
      ↓
Capability/workflow
      ↓
Output language
```

The platform must distinguish:

- interface/UI language;
- citizen input language;
- internal semantic representation;
- document output language.

## Language pipeline

```text
Citizen speech/text
      ↓
Language identification
      ↓
Local-first normalization / transcription
      ↓
Structured issue representation
      ↓
Deterministic civic routing
      ↓
Optional AI assistance through privacy gate
      ↓
Localized explanation / draft
      ↓
Citizen review
```

## Major-language support

Initial production language support should be selected by deployment evidence and quality testing rather than claiming all languages are equally supported on day one. The architecture must nevertheless be language-extensible from the beginning so adding a language is primarily a locale/model/QA task, not a rewrite of civic capabilities.

For Indian-language coverage, maintain language packs and test suites for UI strings, civic terminology, names, addresses, dates, numerals, honorifics, legal/administrative terms, and document formatting.

## AI safety

Language processing is an AI-capable infrastructure service, not permission to transmit personal data. Personal and sensitive content remains local by default. Remote AI receives only minimized, explicitly permitted context. Where local language processing is available, prefer it for private content.

## Human verification

Critical extracted facts must remain editable by the citizen. Names, addresses, dates, application/reference numbers, amounts, authority details, and legal citations require structured-field preservation and validation.

## Quality model

For each supported language measure:

- language identification accuracy;
- transcription quality where speech is supported;
- civic intent classification;
- entity/address preservation;
- translation fidelity;
- document formatting;
- hallucination/error rate;
- user correction rate;
- fallback success.

A language is not "production supported" merely because a model can generate text in it.
