# Predecessor lineage and provenance

Cohervia is a canonical successor project and is intentionally documented as a foundation-only research effort. It does not copy predecessor implementations, and it does not inherit validation claims simply because a predecessor construct was chosen for study.

## Authoritative predecessor snapshots

This lineage record is anchored to the public repository snapshots specified for the foundation PR:

- EFGM: `https://github.com/dauffrey/efgm` at commit `37b2ff2d2b577c9f383dd0d7c3083597627150ea`
- EFGM Artificial Homeostasis: `https://github.com/dauffrey/EFGM-artificial-homeostasis` at commit `7d67c01647a2a5305d5bf651ff2eacc8c2834d40`
- Coherence Governor System: `https://github.com/dauffrey/CGS` at commit `96c15ce00221879ae613ec907e69206a5037d915`

Where a predecessor README conflicts with a later experiment record, the experiment's preregistration, frozen implementation record, final result, and evidence record are authoritative.

## Predecessor records

| Predecessor | Repository URL | Pinned commit | Role | Constructs considered for migration | Evidence limitations | What will not automatically transfer |
| --- | --- | --- | --- | --- | --- | --- |
| EFGM | https://github.com/dauffrey/efgm | `37b2ff2d2b577c9f383dd0d7c3083597627150ea` | Evidence-backed observation and provenance lineage | `MetricObservation` semantics, applicability states, provenance discipline, falsification posture | The repository is a provenance and methodology lineage, not a validated production control system. It is evidence for measurement semantics and governance discipline, not proof of general predictive performance. | Direct operational assumptions, threshold choices, and general performance claims from predecessor implementation or documentation. |
| EFGM Artificial Homeostasis | https://github.com/dauffrey/EFGM-artificial-homeostasis | `7d67c01647a2a5305d5bf651ff2eacc8c2834d40` | Disturbance, reserve, recovery, and viability measurement lineage | disturbance load, operational reserve, recovery, viability margin, counterfactual regulation, abstention, `STABLE`, `RECOVERED`, `FAILED`, `tau_escape` | Strongest evidence remains synthetic and bounded to the controlled synthetic environment. `AH-EXP-0010` survived its preregistered holdout; `AH-EXP-0011` survived its primary measurement hypothesis; `AH-EXP-0012` is preregistered but unobserved. | Synthetic results do not automatically generalize to real autonomous agents, and no policy threshold is validated simply because it survived a synthetic benchmark. |
| Coherence Governor System | https://github.com/dauffrey/CGS | `96c15ce00221879ae613ec907e69206a5037d915` | Independent governor architecture lineage | independent governor separation, trajectory warning, state viability vs action authorization, graduated authority, matched false-alarm evaluation | The `CG-EXP-0001` synthetic harness is instrumentation evidence only. It is not evidence that the governor predicts real-agent failure. | Real-agent failure prediction, production safety claims, and policy interpretation do not transfer automatically from the synthetic harness. |

## Immutable experiment identifiers

Predecessor experiment identifiers remain immutable. They must be cited under their original IDs and never renamed as Cohervia experiments.

This includes:

- `AH-EXP-0010`
- `AH-EXP-0011`
- `AH-EXP-0012`
- `CG-EXP-0001`

Their outcomes, status, and evidence, if any, remain tied to their original lineage. Cohervia begins a new experimental lineage and reserves the `COH-EXP-NNNN` namespace. `AH-EXP-0012` remains a predecessor experiment and must not be duplicated, renamed, or contaminated.

## Migration posture

Cohervia will adopt constructs only under explicit research provenance and conservative status review. A predecessor construct may be considered for migration, but no construct is assumed valid merely because it was selected for the successor project.

This foundation PR records lineage, names the canonical project identity, and establishes the research posture required before implementation-level migration begins.
