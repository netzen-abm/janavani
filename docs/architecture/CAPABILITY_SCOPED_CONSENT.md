# Capability-Scoped Consent

## Canonical rule

Consent is never a blanket Janavani permission. It is scoped to the exact capability, purpose, data fields, provider, and processing mode requested.

A user choosing AI does not grant permission to send arbitrary personal data. A consent grant cannot widen the capability's minimum-data contract.

## Evaluation sequence

```text
Capability request
      ↓
Minimum-data policy
      ↓
Data classification / minimization
      ↓
Does this capability require consent?
      ↓
Exact consent grant
      ↓
Capability + purpose + provider + mode + field scope match
      ↓
ALLOW or DENY
```

## Scope

A consent grant is bound to:

- `capability_id`
- `purpose`
- approved data fields
- provider, when applicable
- processing mode (`LOCAL`, `REMOTE`, or `HYBRID`)
- grant time
- optional expiry

The evaluator fails closed for missing, expired, mismatched, or incomplete grants.

## Non-expansion rule

The capability policy defines the minimum fields required by the operation. A grant may authorize those fields, but it cannot add unrelated fields to the operation's scope.

For example, a document-drafting capability that requires `issue_type` and `sanitized_facts` cannot use a grant containing `name` or `phone` to obtain those fields unless a separate capability policy explicitly requires them and a separate matching consent scope authorizes them.

## Consequential actions

Consent to data processing is not consent to consequential action. Submission, external messaging, publication, deletion, financial activity, or other high-impact actions require the separate action/confirmation policy.

## Privacy invariant

Encryption does not create permission. AI selection does not create permission. Channel selection does not create permission. Every remote-processing capability must satisfy its own minimum-data and consent requirements.
