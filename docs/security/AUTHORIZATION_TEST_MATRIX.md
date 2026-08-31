# Authorization Boundary Test Matrix

This matrix defines the executable security contract for Janavani's shared authorization boundary.

| Scenario | Expected result |
|---|---|
| Anonymous + explicitly public capability | ALLOW |
| Anonymous + unknown capability | DENY |
| Anonymous + protected capability | DENY |
| Authenticated principal + explicit capability grant | ALLOW |
| Authenticated principal + missing capability grant | DENY |
| Workflow state without capability mapping | No implicit authority |
| Protected workflow state | Must pass capability authorization before handler execution |

## Boundary rule

A command, workflow state, agent intent, or interface identity is not itself authority. Authority comes from the shared capability policy evaluated at the execution boundary.

## Fail-closed rule

Unknown capabilities and protected capabilities without an explicit grant must not execute.

These tests are deliberately provider-neutral so the same policy can be reused by Web, Telegram, WhatsApp, Messenger, mobile and future agent interfaces.
