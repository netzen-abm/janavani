# How to Contribute to Janavani

Janavani is civic infrastructure for meaningful citizen participation. Contributions are welcome from developers and non-developers alike. You do not need to be a programmer to help.

## Ways to Contribute

### Software and product
- **Coding:** improve the Telegram Bot, WebApp, API, accessibility, performance, reliability, or shared capabilities.
- **Testing:** write regression tests, reproduce bugs using synthetic examples, test mobile layouts, and check keyboard and screen-reader accessibility.
- **User experience:** improve onboarding, form clarity, recovery messages, and the distinction between a draft, a saved Case, and a submission.
- **Documentation:** improve developer setup, user guides, architecture references, and troubleshooting steps.

### Citizen-facing content
- **Content creation:** draft plain-language civic guides, explainers, FAQs, and step-by-step instructions using reliable sources.
- **Letter drafting:** propose reusable complaint, representation, grievance, and RTI templates. Clearly distinguish requests for existing records from requests that an authority take action. Do not present templates as legal advice.
- **Proofreading and plain language:** review grammar, spelling, clarity, consistency, readability, and confusing placeholders.
- **Translation and language review:** help with Malayalam and other Indian languages. Translation work must be reviewed by a competent speaker before being described as verified or made the default.
- **Public authority data:** verify office names, jurisdiction, contact details, and source URLs against reliable public sources before proposing updates.

## Safe contribution workflow

1. Search existing issues, source files, tests, and documentation before proposing a new file or a duplicate implementation.
2. Open an issue for a substantial change and explain the user problem, evidence, and proposed outcome. Small documentation corrections can go directly into a focused pull request.
3. Keep changes narrow. Reuse existing shared capabilities and preserve independent WebApp and Telegram operation.
4. Add or update tests for code changes. A successful build alone does not establish that a citizen journey works.
5. Cite primary sources for authority data and legal or civic claims. Mark uncertain information as unverified rather than guessing.

## Privacy and security rules

- **Never** post real citizen narratives, names, phone numbers, addresses, identity documents, private case details, access tokens, API keys, passwords, or production environment values in public issues, pull requests, commits, or screenshots.
- Use synthetic data for demonstrations and regression tests.
- Do not use public issues to report a suspected vulnerability or exposed credential. Report it privately through the repository owner's available security-reporting route.
- Do not claim a draft was filed, a Case was registered, an authority was contacted, or a response was received unless there is direct evidence that the action occurred.
- Do not add new permissions, data collection, external providers, or persistent citizen-content storage without reviewing the existing privacy and security contracts.

## Pull request checklist

- [ ] I checked for an existing implementation, file, issue, or documentation owner.
- [ ] The change has one clear responsibility and does not duplicate shared business logic.
- [ ] Relevant tests pass, or the pull request explains what could not be tested.
- [ ] Documentation and screenshots contain no secrets or real citizen data.
- [ ] Public data has a source and its verification status is explicit.
- [ ] Destructive cleanup preserves required history; archive first and delete only with evidence.

## Get started

Browse the repository, choose an issue, or open a new issue with a focused proposal:

https://github.com/netzen-abm/janavani/issues

You can help through coding, testing, content creation, letter drafting, proofreading, accessibility, translation, public-source verification, or documentation. Every contribution should make Janavani more useful, safe, and understandable for citizens.
