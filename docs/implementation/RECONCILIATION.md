# Scientist / legacy PR reconciliation

## Audited snapshots

Audit date: 2026-10-02. Source snapshots were retrieved through the GitHub connector and compared by Git blob identity. Direct git cloning and local package-index access were unavailable. No historical custody or inaccessible predecessor artifact matching is claimed.

| Source | Pinned commit | Scope and disposition |
| --- | --- | --- |
| main, merged PR #7 | `fc139abfbc92f0d7ef30dfb6bb032402c8e05456` | Preserve Scientist v0.2.1, policies, permissions, research state, fixed qualification protocol and saved archive. |
| PR #2 | `ef8477b11fa00f6d6ab1a0cc461424d6eddcb7b5` | Adopt inventory and proposed contracts; supersede stale README/ROADMAP and Phase 2 scheduling language. |
| PR #3 | `f91f38daa57f38375eefa1cfd708fad2c6f6b7e4` | Adapt research framework, schemas and proposed preregistration to the Scientist architecture; retain review corrections. |
| PR #4 (stacked on #3) | `54423f84cdcd122e23767406c8e6e4cf386d2600` | Selectively rework apparatus under `harness/`; supersede root package/workflow and unsafe diagnostic behavior. |

The integration branch starts from the main snapshot. No old branch is merged, rebased or rewritten. The remote integration commit has the audited main commit as its sole parent. Old PR closure remains a human decision after reviewing the replacement.

## Audit findings and resolution

| Area | What remains valid | Conflict / defect | Resolution |
| --- | --- | --- | --- |
| PR #2 inventory | Pinned predecessor entries, licensing limitations, explicit adopt/adapt/defer decisions | Main README links omit contracts; obsolete scheduling implies Scientist infrastructure does not exist | Import inventory and contracts with a current scope note; preserve licensing and evidence limitations. |
| Observation contract | Identity, units, missingness, causal availability and provenance | Scientist ledgers and harness events are different record types | No implicit conversion. A later observation core must satisfy O1–O4 and acceptance matrix. |
| Trajectory contract | Estimator-neutral state, causal cutoffs, label isolation | Candidate state is sometimes read as implemented or validated | Retain as future design only. No estimator or production governor is added. |
| Authority/audit contract | Recommendations are distinct from enforcement; hard boundaries prevail; JCS and atomic replay requirements | Harness uses sorted Python JSON and in-memory hash chaining; Scientist uses bounded research artifacts | Declare different dialects. Neither implementation satisfies the proposed observation/audit core contract. |
| PR #3 review corrections | Same-holdout comparators; A/B/C separation; cross-family transfer; Yellow controls; blinded inputs; sham controls and feature masks | No explicit Scientist lifecycle/ownership; no exact sample allocation, thresholds or uncertainty plan | Add architecture mapping and unfrozen status. Those exact scientific choices remain pre-freeze review blockers. |
| Assessment records | Independent evaluator identities and separate emergence/transfer labels | Residuals may contradict component means; missing invalid aggregates cannot be represented | Recompute residuals, reject nonfinite/bool statistics and preserve null invalid estimates/zero usable counts. JSON Schema alone is insufficient for arithmetic relations. |
| PR #4 selectors | Recompute rather than trust positive labels; two-family minimum | NaN passes comparisons; hashes can be mixed under one configuration ID | Finite range checks, residual consistency, A/B experiment/config/hash/family/comparator/endpoint matching, ambiguous hash and conflicting duplicate rejection. Diagnostics grant no authority. |
| Memory/audit | Trial scoping, hashes and recording interface | Nested references permit unlogged memory changes or audit rewriting | Defensive copies on ingress/egress, explicit trial scope, candidate-state commit after successful audit append. |
| Apparatus runner | Deterministic benign public fixtures, runtime holdout rejection | Arbitrary Python agent/evaluator interfaces are not a containment boundary; scripted development was labeled exploratory | Only reviewed fixture classes/tasks accepted; malformed partitions rejected before execution; all fixture runs labeled instrumentation, scientific_evidence=false. |
| CI | Existing Scientist matrix and archive checks | Old harness root package and workflow would create a separate uncoordinated surface | Separate harness package plus integration checks, both suites, offline smoke artifacts, no credentials/live providers. |

Main has the Scientist reasoning engine, bounded artifact IO, research ledgers and qualification instrumentation. It has no confirmatory experiment runner. The original root README and ROADMAP understate implemented infrastructure; that is repaired without elevating scientific claims.

Existing GitHub main CI run `35950748228` passed at the audited main. PR #2 has no runtime/workflow. PR #4 exact-head CI run `35541221659` passed, but its older suite lacks regressions for the outstanding review defects. Main's 57 tests run locally with four optional OpenAI-adapter tests skipped because its dependency is unavailable here; exact-head CI installs it and uses mocked SDK calls only.

## Concrete integration sequence

1. Preserve the mainline Scientist boundary and record exact snapshot identities.
2. Adopt #2 design contracts and inventory, distinguishing them from current Scientist and apparatus schemas. Keep the observation core, JCS selection and transactional replay deferred.
3. Reconcile #3 as an explicitly proposed, unexecuted, unfrozen research design. Add ownership/lifecycle mapping and arithmetic/missingness amendments; retain all earlier endpoint-independence and holdout protections.
4. Port only #4's development apparatus into a separate package. Repair diagnostics and recording integrity; restrict the runner to scripted public fixtures. Do not connect it to Scientist CLI, providers, tools, permission files or evidence ledgers.
5. Update status/navigation, add boundary/protocol integration checks, and exercise both suites plus scripted qualification and apparatus smoke checks in CI.
6. Submit one replacement PR for human review. Do not merge it or close the old PRs automatically.

## Decisions required from humans

- Approve the replacement design and disposition of PRs #2–#4; merge authority remains external.
- Select and preregister exact task families/generators, independent seeds, sample counts/allocation, randomization, retries, missingness/censoring, uncertainty/multiplicity and numeric survival/falsification/inconclusive rules. A list of freeze fields is not a completed preregistration or freeze.
- Review capability estimator/comparator specification, sham validity, observer anti-confounding, and the scientific interpretation of transporting A/B eligibility to C. A capability-completion discriminator alone does not establish viability warning or safe intervention.
- Qualify actual candidate scientific reasoning with human semantic review. Scripted qualification passes instrumentation checks only; seven quality dimensions remain unassessed.
- Build and independently review any future external sandbox/evaluator service: process separation, hard resource limits, authenticated identities, protected audit retention/checkpoints, holdout vault and permissions. No such capability is supplied here.
- Decide Cohervia licensing before distribution; no predecessor implementation code is copied by this reconciliation.
- Implement the minimal observation core separately, including pinned JCS conformance, atomic local storage, deterministic dispositions and replay; then review it against the preserved contract matrix.

No confirmatory holdout inputs, outcomes or reconstruction metadata were inspected. No model provider was called. Unit tests, public scripted qualification and apparatus self-tests are instrumentation, not new scientific evidence.

## Pre-merge technical review corrections

Three self-review findings were corrected on PR #8: archived IO/configuration is now bound to audit events and verified on output/re-read; memory resets are audited and trial-ID reuse is denied; available statistics are checked independently of positive/negative/invalid classification. Regressions cover archive mutation, missing events, permission/evidence relabeling, memory reset audit failure/rollback, reused IDs, valid negative estimates, inconsistent negative residuals and invalid-record missingness. Statistical plans and independent evaluator infrastructure remain deferred; no confirmatory execution is added.
