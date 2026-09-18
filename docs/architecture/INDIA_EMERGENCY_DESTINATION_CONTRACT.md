# Janavani India Emergency Destination Contract

## Status

Canonical data boundary — initial implementation

## Purpose

Janavani may help a citizen reach an official emergency service, but it must not represent a user action as a successful emergency submission unless the selected provider supplies an authoritative acknowledgement.

The first nationally scoped emergency destination is 112, based on the National Portal of India helpline directory:
https://www.india.gov.in/directory/helpline

The portal describes 112 as the Integrated Helpline / Emergency Response Support System for emergency response including police, fire & rescue and health services.

## Canonical destination

- ref: india:national-emergency:112
- number: 112
- scope: india
- services: POLICE | FIRE | HEALTH
- action: CALL

## Architectural rule

The destination registry is not a transport implementation. It may be consumed by Web, Android, iOS, Telegram/Mini App where platform capabilities permit, and future emergency-capable surfaces. Each surface owns its platform-specific call UX.

## Explicit user confirmation

A normal emergency call is a consequential external action. The surface must explain the action, obtain applicable explicit confirmation, invoke the supported call mechanism, and report only what the platform actually establishes.

The backend must never fabricate call, connection, acceptance, dispatch, delivery, or acknowledgement states.

## No silent dialing

Janavani must not silently initiate an emergency call from a background workflow, AI agent, notification, or autonomous process. If a platform does not permit direct calling, provide the number and a manual fallback.

## Relationship to SOS

Surface -> SOS Capability -> Safety/Privacy Decision -> Authorization / Consequential Gate -> User-confirmed emergency action -> Surface-specific call adapter.

The 112 destination does not bypass the SOS policy boundary.

## Location and evidence

Calling 112 does not by itself imply transmission of GPS/location, audio, video, photographs, evidence, or identity information. Those are separate data-sharing decisions governed by existing safety, privacy, consent, evidence and authorization contracts.

## Other helplines

The National Portal also lists other emergency and support numbers, including 102, 100, 101, 1930, 1915, 181, 1098, 14567, 139 and 1947. They should not be hard-coded into the SOS core merely because they exist. They belong in a separately governed, source-backed public-service directory with scope, service category, jurisdiction and freshness metadata.

## Freshness

Government contact information can change. Emergency destination data must carry source metadata and be periodically reviewed.

## Non-goals

This contract does not implement police/control-room HTTP submission, automatic dispatch, call recording, emergency location sharing, evidence upload, SMS delivery, mesh/satellite transport, or autonomous emergency decisions.
