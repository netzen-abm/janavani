# Canonical Follow-Up Capability

## Status

**Architecture contract — implementation follows this contract.**

## Purpose

JanaVani follow-up is a user-support capability that helps a citizen remember,
prepare for, and choose the next action after a document or civic action.

Follow-up is **adaptive**. It is determined by the nature of the matter, the
document(s) generated, the order in which actions occurred, elapsed time,
responses received, and the user's reported outcome.

## Hard boundary

JanaVani may remind, explain, prepare the next document, and record a
user-reported outcome.

JanaVani does **not** send the document or perform the external action.

A reminder never proves that an action occurred.

## Document/action sequences

The capability must support sequences such as:

- Letter
- RTI
- Letter + RTI
- RTI then Letter
- Letter then RTI
- Letter → follow-up Letter
- Letter → escalation to Department Head
- Letter → escalation to Administrative Head
- Letter → escalation to the respective Legislator
- RTI → response review
- RTI → satisfactory response → close/record outcome
- RTI → unsatisfactory/incomplete response → next escalation/action
- RTI → no adequate resolution → BSA-related escalation/action
- BSA-related step → unresolved matter → party-in-person procedural support

The exact next step is not selected merely from the last file type. The case
history and the user's reported facts must be considered.

## Adaptive decision model

```text
CASE + MATTER NATURE
        |
        +-- Documents/actions already completed
        |
        +-- Time elapsed
        |
        +-- Authority response
        |
        +-- User assessment of response
        |
        +-- Evidence / reference numbers
        |
        v
FOLLOW-UP DECISION
        |
        +--> Reminder
        +--> Follow-up Letter
        +--> RTI
        +--> RTI response review
        +--> Department Head escalation
        +--> Administrative Head escalation
        +--> Legislator escalation
        +--> BSA-related next step
        +--> Party-in-person procedural support
        +--> Close / monitor
```

## Follow-up states

Follow-up should distinguish at minimum:

`FOLLOW_UP_DUE`
`REMINDER_SCHEDULED`
`USER_ACTION_PENDING`
`USER_ACTION_REPORTED`
`RESPONSE_PENDING`
`RESPONSE_RECEIVED`
`RESPONSE_SATISFACTORY`
`RESPONSE_UNSATISFACTORY`
`ESCALATION_RECOMMENDED`
`CLOSED`

These states describe JanaVani's support and recorded case state. They do not
assert external delivery unless supported by evidence.

## User-controlled actions

When a follow-up becomes due, JanaVani may present choices such as:

- Remind me later
- I sent it
- I have not sent it
- I received a response
- No response received
- Response is satisfactory
- Response is incomplete/unsatisfactory
- Prepare the next document
- Escalate
- Close the matter

The user's statement must be recorded as a user-reported event, not converted
into fabricated government evidence.

## RTI response pathway

RTI is an information/evidence pathway and may be positioned before, after, or
alongside a complaint/letter depending on the matter.

After an RTI response, JanaVani may help the user assess whether the response
addresses the requested information. If the user reports that it is
unsatisfactory, incomplete, or otherwise inadequate, JanaVani may guide the
next available escalation/action, including the BSA-related path defined for
the matter, followed by further procedural support where appropriate.

JanaVani must not declare a response legally inadequate solely from an AI
classification. Legal/procedural claims require appropriate authoritative
sources and, where necessary, human review.

## Escalation ladder

The follow-up engine should support an authority-aware escalation graph rather
than hard-coded one-size-fits-all steps.

A possible path is:

```text
Initial Letter / RTI
        |
        v
Follow-up
        |
        +--> Department Head
        |
        +--> Administrative Head
        |
        +--> Respective Legislator
        |
        +--> RTI response review
                  |
                  +--> satisfactory → resolve/close
                  |
                  +--> unsatisfactory
                           |
                           v
                      BSA-related step
                           |
                           +--> unresolved
                                  |
                                  v
                         Party-in-person
                         procedural support
```

The graph is configurable by matter type, jurisdiction, authority structure,
and applicable procedure. JanaVani must not assume that every matter follows
every rung.

## Document generation boundary

A follow-up action may request generation of a new document. The Document
Capability then generates PDF/DOCX for user review and download.

```text
Follow-up engine
      |
      v
Request next document
      |
      v
Document Capability
      |
      +--> PDF
      +--> DOCX / Word
      |
      v
User review / correction / download
```

There is no delivery call in this path.

## Reminder design

Reminders should be derived from the case/action context rather than being a
generic timer. Examples include:

- reminder to follow up after an initial letter;
- reminder to check for an RTI response;
- reminder to review an unsatisfactory response;
- reminder to prepare the next escalation;
- reminder to report an outcome.

Timing must remain user-controlled and configurable. The system may recommend a
reasonable follow-up point, but a reminder must not automatically execute the
next external action.

## Provider and surface independence

Follow-up is a shared capability. Telegram, WebApp, Android, iOS, WhatsApp,
DApp, and future surfaces are adapters.

The follow-up decision logic must not depend on Telegram, email, a specific AI
provider, Supabase, or another single infrastructure provider.

## Safety and truthfulness

The follow-up engine must preserve these distinctions:

`GENERATED != DOWNLOADED != SENT_BY_USER != DELIVERED != RECEIVED != ACKNOWLEDGED`

User-reported events and externally verified evidence must remain distinguishable.

AI may assist with classification, summarisation, drafting, or recommendation,
but it must not silently invent authorities, deadlines, responses, delivery,
or legal outcomes.
