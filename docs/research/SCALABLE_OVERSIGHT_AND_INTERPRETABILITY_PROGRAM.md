# Independent AI understanding and oversight — prospective research track

**Status:** research design and bounded read-only intake infrastructure. Not a validated governor, proof of mechanistic understanding, safe intervention or production deployment. Created October 12, 2026.

## Ultimate scientific objective and limitation

The desired end state is independently verifiable prediction of consequential behavior, causally grounded explanations in explicitly scoped model families, and externally enforced permission boundaries under uncertainty, model change, unreliable monitors and stronger-than-monitor agents.

A general `100% solved` claim is **not supportable** by this repository or any finite benchmark. Exhaustive guarantees, where feasible at all, require a stated finite/abstracted system, formal properties, trusted enforcement assumptions and independently reviewed verification. A monitor cannot prove its own reliability by self-reporting confidence.

Cohervia cannot directly inspect the hidden internal processes of a remotely served model from its text responses. EFGM metrics and natural-language explanations may be informative but are not evidence of faithful mechanisms without causal experiments. Absent access is explicit `unknown`, not zero or success.

## Research division of labor

- **EFGM:** candidate entropy, decision integrity, causal-explanation measurement and falsification protocols. EFGM v2 and Agent Governance v0.3 metrics remain experimental; no threshold from them automatically authorizes Cohervia actions.
- **Cohervia observation/audit core:** exact evidence bytes, provenance, frozen configuration, explicit missingness, JCS identity and deterministic replay. Existing acceptance proves record integrity only, not truth of a model's internal explanation.
- **Cohervia Scientist:** propose hypotheses, critically examine alternative mechanisms and draft bounded exploratory plans; never execute confirmatory studies, unlock a holdout or change permissions.
- **External evaluator / holdout custodian (future):** independently execute preregistered mechanism probes and separate governance trials with evidence custody, anti-contamination and all negative results.
- **Independent governor and deterministic enforcer (future):** compare shadow-mode warnings at matched false-alarm budgets; enforce permissions separately from monitor judgments. If a monitor is missing, late, inconsistent or compromised, a trusted enforcement layer cannot silently default to `ALLOW`.

## Evidence and trust boundaries

A cross-repository claim packet, even with valid hashes and a claimed independent evaluator, remains **untrusted input** until source artifacts and custodial identities are independently verified. Hash strings alone do not establish provenance, and two different dataset hashes do not prove disjoint or blinded data. A reported `observed` state is not independent confirmation.

`cohervia.shadow_evidence.assess_shadow_evidence` implements an intentionally small, standalone **read-only research intake**:

- requires exact `efgm-evidence-summary/0.1` shape, identity and SHA-256 fields, valid reason codes and explicit evidence statuses;
- retains EFGM `INVALID`/`INSUFFICIENT_EVIDENCE` dispositions; unobserved/unknown provenance or independent evidence blocks review candidacy;
- returns at most `UNVERIFIED_REVIEW_CANDIDATE` for a complete *self-reported* packet;
- never authenticates the input, attests evaluator independence, stores data, ingests Scientist records, accesses holdouts, estimates trajectories, grants permissions, or controls a governor.

A reviewed future adapter must bind raw evidence bytes and asserted claims into distinct typed records in the existing core, with independently trusted checkpoints and externally verified custody. Do not interpret this read-only function as that adapter or as Phase 3 completion.

## Prospective experimental gates

1. Select allowed public/open-weight models and narrowly defined causal interventions. Record which internal quantities actually can be observed. Remote black-box models permit behavioral, not hidden-mechanism, claims.
2. Preregister a concrete independent causal study: frozen model/config, estimand, placebo controls, disjoint blinded evaluation, uncertainty, confidence/calibration, failure criteria, minimal baselines, and how to adjudicate conflicting explanations.
3. Only after independent evaluator/holdout infrastructure and approval: run confirmatory evaluation with negative-result retention. The Scientist may analyze released reports but must not inspect unopened heldouts.
4. Preregister **shadow-only** Cohervia monitoring against action-only and simple checklist baselines under fixed alert budgets. Measure false alarms, missed events, predictive lead time, uncertainty, distribution shift and monitoring costs. A coherent or high-viability agent can still perform an unauthorized act.
5. Only after independent sandbox, custody, human review and a separate safety case: research deterministic enforcement/fallback under model and monitor failure. Authority must always stay external to acting AI and probabilistic monitors.

**Explicit stop conditions:** absent provenance, unavailable hidden-state access for causal claims, compromised independent evaluator, holdout leakage, protocol changes after exposure, unexpected tool access or failed containment. None of these may be relabeled a successful run.

## Related authoritative internal records

- [Architectural overview](../architecture/OVERVIEW.md)
- [Observation contract](../contracts/OBSERVATION_CONTRACT.md)
- [Authority/audit contract](../contracts/AUTHORITY_AUDIT_CONTRACT.md)
- [Scientist capability/permission boundary](SCIENTIST_CAPABILITY_BOUNDARY.md)
- [Research roadmap](../../ROADMAP.md)
- [EFGM upstream research program](https://github.com/dauffrey/efgm/blob/research/causal-explanation-evidence-gate-20261012/research/INTERPRETABILITY_AND_GOVERNABILITY_PROGRAM.md)

## External research context

- Guan et al., *Monitoring Monitorability* (2026): https://proceedings.mlr.press/v306/guan26h.html
- Asiaee, *Certified Interventional Fidelity* (2026): https://proceedings.mlr.press/v337/asiaee26d.html
- NIST CAISI, *Challenges to the monitoring of deployed AI systems* (2026): https://www.nist.gov/publications/challenges-monitoring-deployed-ai-systems-center-ai-standards-and-innovation

These references motivate testing standards; no external result is imported as Cohervia evidence.
