# Janavani India Public Emergency & Service Destination Registry

## Status

Canonical data boundary — initial national registry

## Source

Initial records are based on the National Portal of India Helpline directory:
https://www.india.gov.in/directory/helpline

The registry is a directory of public destinations, not an action engine.

## Purpose

This registry answers: **Which verified public-service destination can a Janavani surface present to a citizen?**

It does not answer: **Did Janavani actually contact that service?**

## Record contract

Every destination has a stable reference, name, public number, service category, jurisdiction/scope, supported action, authoritative source URL, source label, and review-required metadata.

## Safety rule

Registry membership does not establish successful contact. A surface must obtain applicable user confirmation and use its platform-specific contact mechanism. Janavani must not claim connection, acceptance, dispatch, delivery or acknowledgement without evidence from the relevant provider.

## 112 relationship

112 remains the nationally scoped emergency destination in the SOS domain. Other entries are service destinations and must not silently become SOS escalation targets merely because they exist here.

## No provider coupling

The registry contains no HTTP client, telecom provider, SMS gateway, police-control-room API, autonomous dialing, or transport implementation.

## Freshness

Government helpline information can change. Records therefore carry source metadata and require periodic review. State/district records require their own authoritative source and jurisdiction metadata.

## Future extensions

State/UT, district, language, operating hours, emergency classification, call/SMS/web/app action types, verification timestamp, effective/expiry dates, official service URL, accessibility information, and freshness status can be added without creating a second SOS or authorization engine.
