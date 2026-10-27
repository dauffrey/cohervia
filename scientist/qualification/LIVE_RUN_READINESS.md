# Controlled live Scientist qualification — readiness gate

Status: **NOT AUTHORIZED TO EXECUTE** until all checks below are verified in the runner. This document is an implementation and review checklist, not a live workflow.

## Scope

- Exactly one seven-case pass under the existing versioned `PROTOCOL.md`, with at most six provider calls per case (42 total).
- OpenAI API provider; pin a specific available model and repository commit before execution.
- Maximum approved spend: **US$5** for this pass. This is a budget authorization, not proof of a hard cap.
- No AWS activation, holdout access, experiment execution, repository write token, or automatic scientific claim promotion.

## Mandatory safeguards before live execution

1. **Credentials:** use an Actions secret named `OPENAI_API_KEY` only in a trusted, manually dispatched job. Confirm exact secret name and model access without exposing the key. Never expose secrets to untrusted PR code, fork events, or uploaded artifacts.
2. **Cost guard:** implement a runner-side conservative upper-bound preflight and before-each-call reservation using model-specific input/output pricing and maximum request/response token budgets. Stop *before* a request whose maximum possible billed cost would exceed US$5, including any already-reserved calls. Fail closed when pricing, usage or model identity is unknown. Verify provider billing semantics; dashboard budget alerts alone are not a hard cap.
3. **Call guard:** limit to one run, seven cases, at most 42 calls, zero automatic retries, and existing timeout/output constraints. Concurrency must not bypass the budget reservation.
4. **Audit:** persist every request, response, error, rejection, and case summary. Run `verify-qualification` and retain immutable downloadable artifacts, hashes, complete denominator, model ID, source commit and execution parameters. Never log API credentials.
5. **Access control:** workflow `permissions: contents: read`, manual `workflow_dispatch` only, no privileged pull-request execution, no writable holdout mounts; use protected environment approval where available.
6. **Tests:** demonstrate stop behavior at the dollar threshold, unknown pricing, malformed usage, mid-run errors, concurrent attempts, and missing secret. Test without live API charges.
7. **Review:** independent review of cost enforcement and evidence capture before first paid execution. Human review of all seven rubric dimensions after the run. Automated structural success does not constitute scientific qualification.

## Existing verified baseline

GitHub Actions Scientist tests for commit `cc5df1b0b009ac31346484f949d6e3e99d5673ca` passed on Python 3.11, 3.12 and 3.13. The Python 3.11 scripted run reported 7 cases, 92 verified artifacts, `scientific_evidence: false`, and `pending_human_review`. Those results are not a live-model assessment.

Tracking: issue #17. The workflow and spending guard still need implementation and verification; **do not run paid calls on the strength of this document**.
