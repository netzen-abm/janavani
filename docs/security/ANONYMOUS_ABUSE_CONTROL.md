# Janavani Anonymous Abuse-Control Contract

Anonymous access is a product feature, not an absence of security.

## Required controls

Anonymous capabilities must use shared infrastructure for:

- rate limiting;
- bounded input size;
- capability-specific quotas;
- abuse-event handling;
- safe error responses;
- monitoring without creating a behavioural identity graph.

## Identity key

The abuse-control key must be an opaque, bounded identifier supplied by the interface/session layer. It must not be a phone number, email address, raw Telegram identifier, or other PII.

## Current reference implementation

`src/security/abuse_control.py` provides a process-local capability-specific sliding-window limiter.

Default reference budget: **30 requests per 60 seconds per principal/capability**.

This is not yet a distributed production limiter. Production deployments with multiple workers must replace the backing store with a shared atomic store while preserving the same interface.

## Policy

A rate-limit rejection must occur before expensive work or consequential writes.

Rate limiting does not replace:

- authorization;
- consent;
- input validation;
- destination authorization;
- authentication where required.

## Privacy

Abuse-control telemetry must be minimized and retained only as long as necessary for security operations. It must not be repurposed into citizen profiling.
