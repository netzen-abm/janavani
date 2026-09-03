# Janavani External Transmission Boundary

**Status:** DESIGNED / ENFORCED AS A POLICY GATE

Janavani separates creation of a civic document from transmission of that document to an external destination.

## Required flow

```text
Document generation
        ↓
Citizen reviews output
        ↓
Transmission capability authorization
        ↓
Explicit consent / approval
        ↓
Destination authorization
        ↓
Actual transmission
        ↓
Destination outcome evidence
```

## Important rule

Generating a PDF or document does **not** authorize Janavani to send it anywhere.

The transmission policy gate does not itself perform network transmission. It returns authorization evidence that a separate transport adapter may consume.

## Default Janavani behaviour

For generated letters, complaints and objections, the current product requirement is to provide the completed document to the citizen for printing/download. Janavani must not silently email or submit it merely because the document was generated.

If a future capability offers electronic submission, it must identify the destination, obtain explicit user approval, minimize the payload, use an approved transport, and record the outcome accurately.

## Security properties

- Authorization is required.
- Explicit consent is required.
- Destination is explicit.
- Authentication does not imply consent.
- Consent does not imply authorization.
- Authorization does not imply successful delivery.
- Failed/unknown delivery must not be represented as confirmed delivery.
- Interface credentials are never placed in citizen identity context.
