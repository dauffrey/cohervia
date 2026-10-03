# Capability research within the Scientist architecture

Status: proposed design, not a scientific result or execution authorization. Applies to the reconciled COH-EXP-0001 documents and separate development apparatus.

## Ownership and information flow

| Component | May produce/read | Must not do |
| --- | --- | --- |
| Scientist reasoning and critic roles | Questions, hypotheses, rival predictions, critiques, exploratory designs and bounded claim drafts from approved public context and research memory | Invoke apparatus, execute arbitrary tools, open holdouts, validate its own claims as empirical evidence, change policies or promote theories automatically |
| Scientist qualification | Fixed public development questions, exact scripted/model responses and structural diagnostics; human rubric | Treat a structural pass or LLM judgment as scientific evidence or grant execution authority |
| Separate `harness/` package | Two public scripted task fixtures, synthetic events, apparatus diagnostics and template coverage checks | Execute the factorial study, use live models/arbitrary agents, read A/B/C inputs, write Scientist state, grant permissions or label its fixtures confirmatory |
| Future capability / transfer evaluators | Frozen A/B task/verifier records under independent authorization | Read observer outputs to define capability success, change endpoints or thresholds after exposure, self-authorize |
| Future governance evaluator | Frozen C trajectories and blinded observer outputs, matched sham comparisons | Select positive populations using C outcomes, tune on A/B/C or infer safety/intervention efficacy from task-success warnings |
| External authority and holdout custodian | Explicit reviewed execution scope, sealed artifact custody, hard containment and audit retention | Delegate permission self-modification to Scientist or the acting agent |
| Human result review | Exact independent result bundles, negative/null findings, uncertainty and protocol deviations | Promote a candidate solely because tests, schema validation or qualification passed |

This integration does not expand Scientist's approved read paths. The README, ROADMAP and experiment index summarize the track within existing public context; the detailed experiment files are not silently added to its allowlist. A separately reviewed context change would be required for direct automated retrieval. No harness import or tool is added to Scientist.

## Lifecycle mapping

`ResearchPhase` describes research records, not permissions. The present COH-EXP-0001 design is a candidate preregistration; the apparatus is independent development instrumentation. The current package supplies no command that advances this design to FROZEN or opens a holdout.

| Research stage | Required record / action | Authority and evidence |
| --- | --- | --- |
| question → hypothesis → critique | Retrieve relevant failures; propose independently falsifiable mechanisms and discriminating rivals | Scientist proposals are inferred/unknown and not empirical observations |
| exploration | Independently authorized bounded exploratory work, with exact artifacts and failures retained | Scripted apparatus fixtures here remain instrumentation; a DEVELOPMENT enum does not make them scientific evidence |
| preregistration | Human review and merged exact protocol, including all numeric decision rules | The imported draft and null manifest are insufficient |
| frozen → confirmatory_pending | Independently verified immutable implementation, evaluator, configuration, analysis and dataset identities plus explicit external authority | No runtime unlock flag exists in this integration |
| result_recorded | Independently generated immutable A/B/C bundles, followed by bounded evidence review | No automatic ingestion into Scientist ledgers; retain invalid, missing, null and negative outcomes |
| theory_revision → promotion_proposed | Reviewed postmortems, evidence references, prior negative results and uncertainty | Candidate revision only; external human merge/promotion gate |

## Record boundaries

The PR #2 `Observation`, `TrajectoryState`, `GovernorRecommendation` and `EnforcementDecision` contracts remain future interfaces. Scientist packets are reasoning artifacts; qualification packets are reasoning diagnostics; harness `Event` and `TrialResult` are apparatus records. None may be silently interpreted as another kind.

The apparatus hash dialect is `python-sorted-json-v1`: UTF-8, sorted keys, compact separators, finite JSON numbers. It is not RFC 8785 JCS. Its in-memory append-only API provides mutation isolation for callers, not process containment, durable storage, historical custody, signatures, tail completeness or an immutable external audit sink. The proposed observation core's atomic durable audit and replay contract remains unimplemented.

Prospective emergence/transfer assessments are independent external evaluator records. Synthetic records used to test selectors or schemas carry no scientific standing. The selectors are pure arithmetic/identity diagnostics and never authorize a stage, open a holdout, verify historical custody or certify an evaluator's independence. An external evaluator must additionally bind every recorded threshold/hash to the reviewed frozen protocol and exact evidence bundle.

Missing aggregate estimates remain null on invalid assessments; zero usable counts are allowed and are not fabricated zero effects. Affirmative/non-invalid records require numeric aggregates, positive usable counts and evidence references. Python validation adds finite statistics and residual recomputation to JSON Schema; the prospective draft fixes absolute serialization tolerance at 1e-12, with zero relative tolerance. This tolerance is an implementation consistency check, not an uncertainty estimator.

## COH-EXP-0001 limits

The 16-cell factor matrix, baseline/transfer estimators, real tool/memory composition, causal ablations, configuration-normalized observer and primary governance analysis are design requirements, not implemented by two scripted tasks. The fixture observer deliberately sees verifier events to test plumbing; it is disqualified as a confirmatory observer because of terminal/endpoint leakage. Its event count warning is not a viable scientific predictor.

Preserve Yellow-tier containment, independent evaluators, same-partition lower-order comparators, A→B→C task-instance separation, two-family replication of the same frozen configuration, topology-matched sham controls, pre-terminal feature masks, matched false-alarm budgets and fixed sample/stopping rules. Keep A/B/C inputs, outcomes and reconstructive metadata inaccessible in all development/testing. Known public fixtures never become holdouts.

Changes after any holdout exposure invalidate the sequence and require a new eligible preregistration/holdout set. Hashes and test passes do not override these requirements. No safety, production-governor, real-agent, capability-emergence or scientific-competence finding follows from this integration.

## Technical review corrections

Scripted apparatus archives now bind saved task/configuration/answer bytes through audited hashes and provide a complete-archive verifier. Memory initialization/reset is audited; previously used trial IDs are rejected. Numeric integrity checks cover affirmative, negative and invalid assessment labels while preserving null unavailable estimates. These corrections do not supply a statistical design, independent evaluator, execution authority or new scientific evidence.
