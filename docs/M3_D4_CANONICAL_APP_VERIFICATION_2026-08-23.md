# JANAVANI — M3-D.4 CANONICAL APPLICATION VERIFICATION

**Date:** 23 August 2026  
**Phase:** M3-D.4  
**Mode:** TEST/VERIFICATION ARTIFACT  
**Repository:** `netzen-abm/janavani`

## 1. Objective

Add a minimal automated verification layer for `src.web.canonical_app:app` before further domain extraction.

## 2. Verification added

Created:

```text
tests/test_canonical_app.py
```

The test suite checks:

1. canonical application imports;
2. canonical application title;
3. `/liveness` response;
4. `/version` response;
5. feedback route registration;
6. legislative route registration;
7. constitutional route registration;
8. land route registration;
9. canonical assembly does not import the legacy `src.web.app` module.

## 3. Important limitation

The GitHub repository connector used for this step can write repository files and inspect source, but it does not provide a direct local Python test-execution facility in this workflow. Therefore this step records the **test implementation**, not a fabricated passing test run.

A passing runtime result must be established in the user's local development environment/CI.

Recommended command:

```powershell
python -m pytest tests/test_canonical_app.py -q
```

If dependencies are installed through a project-specific environment, run the same command through that environment.

## 4. Expected verification

Expected outcomes:

```text
canonical app imports successfully
/liveness -> 200
/version -> 200
all four domain route families are registered
src.web.app is not imported
```

## 5. Next gate

Do not migrate Agent/SOS yet solely because the test file exists.

First run the test locally/CI and record the actual result.

If green:

**M3-D.5 — Agent route extraction design**

If red:

**M3-D.4 remediation**

with the failure captured before changing architecture.

## 6. Status

**M3-D.4 TEST ARTIFACT: COMPLETE**  
**Test execution verified by this workflow:** NO  
**Reason:** no direct repository-local Python execution capability available in this step  
**Application code changed:** NO  
**Legacy app changed:** NO  
**Routes deleted:** NO  
**Production deployment changed:** NO

**END OF DOCUMENT**
