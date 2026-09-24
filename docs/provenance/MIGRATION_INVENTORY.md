# Migration inventory

Status: proposed Phase 1 decisions, pending review. No source code is migrated.
Each source link pins the exact snapshot in [LINEAGE.md](LINEAGE.md).
ADOPT retains conceptual semantics, not permission to copy code. ADAPT explicitly changes
a source idea. DEFER reserves a later study; EXCLUDE omits from default runtime while
preserving history. None upgrades a construct's scientific status.

## Source-grounded decisions

Contract targets refer to [observations](../contracts/OBSERVATION_CONTRACT.md),
[trajectory state](../contracts/TRAJECTORY_STATE_CONTRACT.md), and
[authority/audit](../contracts/AUTHORITY_AUDIT_CONTRACT.md).
Inventory IDs are stable within this specification.

| ID | Construct | Exact source/symbol or section | Source meaning and evidence status | Decision | Destination | Dependencies / rationale / limitations | License key |
| --- | --- | --- | --- | --- | --- | --- | --- |
| INV-01 | Observation states/value semantics | [src/efgm/schemas_v2.py — MetricObservation](https://github.com/dauffrey/efgm/blob/37b2ff2d2b577c9f383dd0d7c3083597627150ea/src/efgm/schemas_v2.py) | Normalized metric with explicit missingness; infrastructure, not predictor evidence | ADAPT | O1–O2 | Add identity/type/unit fields; do not inherit confidence=0.50 or [0,1] for all metrics | E |
| INV-02 | Scorer/evidence provenance | [src/efgm/scoring_v2.py — research_provenance_issues](https://github.com/dauffrey/efgm/blob/37b2ff2d2b577c9f383dd0d7c3083597627150ea/src/efgm/scoring_v2.py) | Checks research provenance; infrastructure | ADAPT | O3 | Local artifact resolution; schema validation cannot authenticate sources | E |
| INV-03 | Identity and temporal continuity | [src/efgm/temporal_v0_3.py — EFGMAgentState; temporal_identity_issues](https://github.com/dauffrey/efgm/blob/37b2ff2d2b577c9f383dd0d7c3083597627150ea/src/efgm/temporal_v0_3.py) | Sequence/subject checks; infrastructure | ADAPT | O1, O4 | Add availability time and deterministic ingestion; no cross-subject merging | E |
| INV-04 | Input/config hashes | [src/efgm/scoring_v2.py — canonical_sha256](https://github.com/dauffrey/efgm/blob/37b2ff2d2b577c9f383dd0d7c3083597627150ea/src/efgm/scoring_v2.py); [src/efgm/schemas_v2.py — EFGMDecisionResult](https://github.com/dauffrey/efgm/blob/37b2ff2d2b577c9f383dd0d7c3083597627150ea/src/efgm/schemas_v2.py) | Input and config byte identities; infrastructure | ADAPT | A4 | New JCS convention; predecessor digests remain unchanged and not interchangeable | E |
| INV-05 | DQ/CRC and composites | [src/efgm/scoring_v2.py — score_decision_efgm; geometric_mean](https://github.com/dauffrey/efgm/blob/37b2ff2d2b577c9f383dd0d7c3083597627150ea/src/efgm/scoring_v2.py) | Derived normalized research scores; not generally validated failure probabilities | DEFER | Future sensor adapter | Needs meaningful domain mapping, calibration and dependence treatment; no Phase 2 scoring | E |
| INV-06 | GI/AE/CUE | [src/efgm/scoring_v3.py — score_agent_governance](https://github.com/dauffrey/efgm/blob/37b2ff2d2b577c9f383dd0d7c3083597627150ea/src/efgm/scoring_v3.py) | Research governance scores; candidate predictors | DEFER | Future sensor adapter | Applicability cannot be fabricated; no wholesale adoption of composites | E |
| INV-07 | Disturbance/reserve/recovery and coupled margin | [src/ahomeostasis/core.py — Regulator.margin; recover](https://github.com/dauffrey/EFGM-artificial-homeostasis/blob/7d67c01647a2a5305d5bf651ff2eacc8c2834d40/src/ahomeostasis/core.py); [src/ahomeostasis/queue_replication.py — QueueTelemetry](https://github.com/dauffrey/EFGM-artificial-homeostasis/blob/7d67c01647a2a5305d5bf651ff2eacc8c2834d40/src/ahomeostasis/queue_replication.py); [experiments/AH-EXP-0007/RESULTS.md — Interpretation](https://github.com/dauffrey/EFGM-artificial-homeostasis/blob/7d67c01647a2a5305d5bf651ff2eacc8c2834d40/experiments/AH-EXP-0007/RESULTS.md) | Bounded synthetic support; known over-regulation failure region | DEFER | Future viability adapter | Synthetic resource is not LLM reserve; uniform superiority partially falsified, mechanism not wholly falsified | A |
| INV-08 | Counterfactual abstention | [src/ahomeostasis/robust_counterfactual_abstention.py — should_relax_robust](https://github.com/dauffrey/EFGM-artificial-homeostasis/blob/7d67c01647a2a5305d5bf651ff2eacc8c2834d40/src/ahomeostasis/robust_counterfactual_abstention.py); [experiments/AH-EXP-0010/FINAL_RESULT.md — Classification](https://github.com/dauffrey/EFGM-artificial-homeostasis/blob/7d67c01647a2a5305d5bf651ff2eacc8c2834d40/experiments/AH-EXP-0010/FINAL_RESULT.md) | Survived specific frozen synthetic holdout | DEFER | Future intervention study | Bounded uncertainty assumptions; does not license deployment thresholds | A |
| INV-09 | Boundary classes and escape | [src/ahomeostasis/trajectory_boundary.py — TrajectoryClass; TrajectoryResult](https://github.com/dauffrey/EFGM-artificial-homeostasis/blob/7d67c01647a2a5305d5bf651ff2eacc8c2834d40/src/ahomeostasis/trajectory_boundary.py); [experiments/AH-EXP-0011/FINAL_RESULT.md — Interpretation](https://github.com/dauffrey/EFGM-artificial-homeostasis/blob/7d67c01647a2a5305d5bf651ff2eacc8c2834d40/experiments/AH-EXP-0011/FINAL_RESULT.md) | Survived measurement hypothesis, not predictive test; zero adaptive override interventions | DEFER | T5 offline outcomes | tau_escape/final classes are labels, not online inputs | A |
| INV-10 | H_t and presentation index | [src/cgs/core.py — likelihood_hazard; score_hazard; coherence_index](https://github.com/dauffrey/CGS/blob/96c15ce00221879ae613ec907e69206a5037d915/src/cgs/core.py) | Reference mathematics; empirical predictive value unestablished | DEFER | T1–T3 | Preserve estimator mode; normalized hazard index is not extra evidence | C |
| INV-11 | State/action margins and velocity | [src/cgs/core.py — state_margin; action_margin; margin_velocity](https://github.com/dauffrey/CGS/blob/96c15ce00221879ae613ec907e69206a5037d915/src/cgs/core.py) | Research definitions, not selected Cohervia estimators | DEFER | T1, T4; A1 | Frozen reference policy differs from action-dependent policy; units and histories must agree | C |
| INV-12 | Isolation and deterministic precedence | [docs/specs/CG-0.2.md — 2. Independent runtime-assurance architecture; 3. Immutable task contract](https://github.com/dauffrey/CGS/blob/96c15ce00221879ae613ec907e69206a5037d915/docs/specs/CG-0.2.md) | Architecture constraint, not empirical safety proof | ADOPT | A1–A2 | External authority remains separate; adaptation only in future record vocabulary | C |
| INV-13 | Graduated governance | [docs/specs/CG-0.2.md — 14. Governor decision inputs](https://github.com/dauffrey/CGS/blob/96c15ce00221879ae613ec907e69206a5037d915/docs/specs/CG-0.2.md) | Candidate control architecture | ADAPT | A1–A2 | Recommendation/enforcement/audit separated; outcomes not scalar; implementation deferred | C |
| INV-14 | Uncertainty mismatch | [src/cgs/core.py — SensorVector](https://github.com/dauffrey/CGS/blob/96c15ce00221879ae613ec907e69206a5037d915/src/cgs/core.py) | Observable mismatch sensor; candidate signal | DEFER | T1 | Not Cohervia U_t evidence-quality metadata; explicit adapter naming required | C |
| INV-15 | Fixed false-alarm baselines and shadow trajectories | [experiments/CG-EXP-0001.md — 7. False-alarm budget; 8. Compared systems](https://github.com/dauffrey/CGS/blob/96c15ce00221879ae613ec907e69206a5037d915/experiments/CG-EXP-0001.md) | Preregistered design; evidentiary experiment unexecuted | ADOPT | Future evaluation policy, T5 | Strong trajectory/sequential baselines; calibration separated from test; no Phase 2 harness | C |
| INV-16 | Synthetic harness | [experiments/CG-EXP-0001-HARNESS.md — Interpretation gate](https://github.com/dauffrey/CGS/blob/96c15ce00221879ae613ec907e69206a5037d915/experiments/CG-EXP-0001-HARNESS.md) | Instrumentation-only, deliberately embedded precursor | DEFER | Future instrumentation | Not real-agent evidence; no execution or copying here | C |
| INV-17 | Prolonged-mode detector | [experiments/AH-EXP-0008/RESULTS.md — Status; Interpretation](https://github.com/dauffrey/EFGM-artificial-homeostasis/blob/7d67c01647a2a5305d5bf651ff2eacc8c2834d40/experiments/AH-EXP-0008/RESULTS.md) | Falsified: completion and utility declined | EXCLUDE | Historical negative evidence | Exclude from default runtime; retain original identity/results | A |
| INV-18 | Trajectory/counterfactual detector | [experiments/AH-EXP-0009/FINAL_RESULT.md — Scientific interpretation](https://github.com/dauffrey/EFGM-artificial-homeostasis/blob/7d67c01647a2a5305d5bf651ff2eacc8c2834d40/experiments/AH-EXP-0009/FINAL_RESULT.md) | Falsified despite aggregate gains: harmful 62 vs beneficial 57 | EXCLUDE | Historical negative evidence | Aggregate gains do not prove intervention quality | A |
| INV-19 | Holdout separation | [experiments/AH-EXP-0012/PREREGISTRATION.md — Status; Scientific separation from AH-EXP-0011](https://github.com/dauffrey/EFGM-artificial-homeostasis/blob/7d67c01647a2a5305d5bf651ff2eacc8c2834d40/experiments/AH-EXP-0012/PREREGISTRATION.md) | Preregistered, confirmatory outcomes unobserved at pin | ADOPT | Evidence policy; T5 | Known AH-EXP-0011 outcomes development-only; do not execute holdout | A |

## Licensing and attribution

These are observations about the inspected snapshots, not a decision about Cohervia's license.

- E: [LICENSE](https://github.com/dauffrey/efgm/blob/37b2ff2d2b577c9f383dd0d7c3083597627150ea/LICENSE) declares Apache-2.0. Future code copying requires applicable
  attribution, license and notice handling and compatibility review.
- C: [LICENSE](https://github.com/dauffrey/CGS/blob/96c15ce00221879ae613ec907e69206a5037d915/LICENSE) declares MIT, copyright CGS contributors. Future copying
  requires retaining its applicable copyright and permission notice.
- A: no root LICENSE/COPYING file or project license declaration was found in the pinned
  snapshot; [pyproject.toml](https://github.com/dauffrey/EFGM-artificial-homeostasis/blob/7d67c01647a2a5305d5bf651ff2eacc8c2834d40/pyproject.toml) does not declare a license. Public visibility does
  not establish code-reuse permission. Obtain explicit licensing before copying code.
- Cohervia has no chosen software license. This PR adds none. Phase 2 can be freshly
  implemented from these proposed contracts; distribution/licensing still needs owner decision.

## Definition incompatibilities

1. EFGM metric values are normalized scores, not automatically calibrated probabilities.
   Cohervia metric definitions declare domains and units rather than forcing every input into [0,1].
2. Artificial Homeostasis models reserve and recovery through synthetic operational resources.
   An LLM agent has no automatically equivalent scalar reserve measurement.
3. An AH reserve-minus-disturbance margin and CGS probability-based state margin differ in
   units, reference conditions and interpretation. No identity mapping is justified.
4. State viability is separate from action authorization. A high margin grants no permission.
5. CGS coherence_index is a transform of hazard, not an independent sensor.
6. Correlated sensors require dependence treatment before aggregation; adding names adds no evidence.
7. Cohervia U_t is proposed evidence-quality information; CGS uses uncertainty mismatch.
   No predecessor validation transfers between these meanings.
8. Current record IDs, timestamps, JCS hashes and audit interfaces are proposed Cohervia design.
   They are not falsely attributed to EFGM or CGS implementations.

## Evidence boundaries and outstanding choices

AH-EXP-0007 limits uniform superiority; it does not erase bounded support for coupling.
AH-EXP-0008 and AH-EXP-0009 stay falsified. AH-EXP-0010 survived only its specific holdout.
AH-EXP-0011 measured boundaries and escape with zero adaptive relaxation interventions;
it did not validate an override effect or precursor prediction.
AH-EXP-0012 remains unexecuted at the pin, regardless of later predecessor development.
CGS's harness supplies instrumentation evidence only.

Outstanding implementation decisions are the pinned canonicalizer and Cohervia licensing.
Domain-specific metric definitions, estimators, authenticated acquisition and production
retention/checkpoints remain deferred; they do not prevent fictional local core tests.
No existing result is renamed as COH-EXP evidence. See the
[bounded Phase 2 plan](../implementation/PHASE_2_PLAN.md).
