# Construct status

This table is intentionally conservative. Every status entry should be traceable to a predecessor record or formal design constraint and should not be elevated by mere selection into Cohervia.

| Construct or result | Status | Traceability and note |
| --- | --- | --- |
| external governor isolation | architectural constraint | Required separation of acting agent and governor; a design constraint rather than an empirical result. |
| deterministic authorization precedence | architectural constraint | Deterministic enforcement is a governing design requirement. It outranks probabilistic governor signals. |
| graduated authority control | architectural constraint | Structured authority progression is a design concept in the predecessor architecture and remains an architectural constraint until validated. |
| EFGM `MetricObservation` applicability and provenance semantics | evidence/provenance infrastructure | A core measurement and provenance principle, not a direct production safety claim. |
| EFGM DQ, CRC, GI, AE, and CUE | candidate hypothesis | Candidate sensors rather than generally validated predictors; they must remain subject to preregistered evaluation and holdout discipline. |
| disturbance load, operational reserve, recovery, and viability margin | supported within a controlled synthetic environment | These constructs have the strongest controlled synthetic evidence in the predecessor homeostasis lineage. |
| the coupled-margin mechanism | supported within controlled synthetic environments, with a known bounded failure region | AH-EXP-0004 through AH-EXP-0007 found the mechanism broadly advantageous in the tested synthetic conditions. AH-EXP-0007 found a bounded adversarial schedule where the uncoupled controller outperformed it. That result limits the mechanism's applicability but does not falsify the mechanism wholesale. |
| uniform-superiority claim | weakened or partially falsified | AH-EXP-0007 partially falsified the claim that the coupled-margin controller is uniformly superior. The failure was excessive protective regulation that prevented task completion on a bounded schedule. |
| AH-EXP-0008 prolonged-mode over-regulation detector | falsified | The prolonged `CAUTION`/`RECOVERY` detector reduced completion and total utility. Persistence in a protective mode was not sufficient evidence that regulation had become maladaptive. |
| AH-EXP-0009 trajectory/counterfactual relaxation detector | falsified on its final independent holdout | Aggregate completion, viability, and utility improved. The preregistered intervention-level governance criterion failed because harmful intervention schedules, `62`, exceeded beneficial intervention schedules, `57`. Preserve the distinction between aggregate performance and intervention-level governance quality. |
| AH-EXP-0010 uncertainty-aware counterfactual abstention | survived a specific preregistered test | AH-EXP-0010 survived its frozen, one-shot synthetic holdout. This is evidence for the tested abstention mechanism under the frozen conditions only, not a general real-agent result. |
| AH-EXP-0011 boundary and escape measurement | survived a specific preregistered measurement test | AH-EXP-0011 established reproducible `STABLE`, `RECOVERED`, and `FAILED` regions plus finite `tau_escape` within the frozen synthetic queue/service environment. The adaptive relaxation mechanism executed zero interventions during the AH-EXP-0011 sweep. AH-EXP-0011 therefore supports boundary and escape-time measurement, but not an effect of the AH-EXP-0010 adaptive override on those boundaries. |
| `STABLE`, `RECOVERED`, `FAILED`, and `tau_escape` measurement | survived a specific preregistered test | These outcomes are supported by the relevant predecessor preregistration and recorded result in the synthetic environment. |
| `AH-EXP-0012` pre-escape warning hypothesis | preregistered but unexecuted | Confirmatory outcomes remain unobserved. |
| CGS `H_t`, `M_t`, `dM_t/dt`, and `U_t` | candidate hypothesis | These are coherent candidate constructs for a compact governing state but are not yet a validated production governor representation. |
| real-agent generalization | not established | The predecessor evidence is synthetic, and no valid generalization to real autonomous agents is established. |
| production safety | not established | No production governor claim is established in this foundation review. |

## Status category definitions

- architectural constraint: a design requirement or separation principle.
- evidence/provenance infrastructure: a methodological construct required for disciplined measurement and evidence retention.
- supported within a controlled synthetic environment: a construct has evidence in a bounded synthetic setting.
- survived a specific preregistered test: the construct or result survived a named preregistered evaluation.
- weakened or partially falsified: evidence indicates reduced confidence or bounded applicability without wholesale rejection.
- falsified: evidence indicates the construct is not reliable under the tested conditions.
- preregistered but unexecuted: a hypothesis exists with a preregistration but no confirmatory evidence yet.
- candidate hypothesis: a proposed construct requiring independent evidence.
- not established: no valid evidence or inference currently supports it for the intended general claim.

The status labels above are intentionally conservative and should be treated as evidence-limited commitments rather than platform-wide endorsements.
