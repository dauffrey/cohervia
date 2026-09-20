# System-level capability discovery

## Status

This document defines a **research programme**, not validated evidence of Cohervia performance and not a claim that any specific frontier system possesses an undisclosed capability.

Cohervia uses the term **uncharacterized capability surface** for capabilities that may be latent in a model or emerge from the interaction of a model with tools, memory, verification, multiple agents, and an environment, but that have not yet been reliably elicited and measured.

A useful decomposition is:

```text
C_system = f(M, P, T, S, E, V, N)
```

where:

- `M` = model;
- `P` = prompting/decomposition;
- `T` = tools;
- `S` = persistent state or memory;
- `E` = environment and permissions;
- `V` = verifier/feedback system;
- `N` = number and organization of agents.

The research target is not raw model intelligence in isolation. It is the interaction term: behaviour that appears only when components are combined.

## Research question

> Can Cohervia detect and characterize the earliest trajectory changes associated with a reproducible system-level capability gain before that gain is visible only in the final outcome?

This creates two distinct measurements:

1. **Capability measurement** — what became possible?
2. **Governance measurement** — what changed in the trajectory when it became possible?

These measurements must remain independent. A capability improvement is not evidence that the trajectory was safe, and a governor warning is not evidence that the capability was harmful.

## Candidate capability classes

Initial low-risk research should prioritize:

- machine-verifiable algorithm discovery;
- mathematical construction and theorem search;
- representation discovery;
- tool-combination effects;
- persistent-memory effects;
- long-horizon planning in benign software or simulation tasks;
- multi-agent coordination in synthetic environments;
- closed-loop scientific reasoning in computational simulators.

High-consequence physical, biological, chemical, cyber, financial, or critical-infrastructure experimentation is outside the initial programme.

## Emergence residual

For an experimental configuration `x`, let `C(x)` be a preregistered capability metric. Let `C_hat(x)` be the capability predicted from lower-order component results without using the held-out result for `x`.

Define the candidate emergence residual:

```text
Delta_emergent(x) = C(x) - C_hat(x)
```

A positive residual is not, by itself, evidence of a qualitatively new capability. It is a trigger for causal investigation.

The claim "system-level emergence" requires:

- reproducibility across multiple independent runs;
- a frozen endpoint;
- causal ablation showing that one or more interaction terms are necessary;
- an independent verifier where possible;
- preserved negative/null trials;
- no post-outcome redefinition of the metric.

## Candidate trajectory events

Cohervia should record the following as first-class events when observable:

- `tool_call`
- `tool_result`
- `memory_read`
- `memory_write`
- `memory_compaction`
- `plan_revision`
- `subagent_spawn`
- `inter_agent_message`
- `shared_state_read`
- `shared_state_write`
- `permission_request`
- `verifier_submission`
- `verifier_result`
- `constraint_encounter`
- `strategy_shift`
- `abstention`
- `termination`

The event vocabulary is intentionally descriptive. A `strategy_shift` observation does not imply deception, intent, or misalignment.

## Memory as a privileged tool

Persistent state can influence future model contexts:

```text
output_t -> stored state -> input_t+1
```

For Cohervia research, persistent memory is therefore treated as a privileged state-changing tool. Memory writes should carry:

- actor identity;
- source context identifier;
- timestamp;
- previous-state hash;
- proposed content hash;
- resulting-state hash;
- persistence class;
- declared purpose;
- downstream consumer identity when known;
- applicability state;
- evidence quality.

A model-generated summary must not silently become trusted governor state.

## Experimental design

Capability discovery should use factorial or fractional-factorial designs where practical.

Candidate dimensions:

| Dimension | Example levels |
|---|---|
| Model | model family A, model family B |
| Prompting | direct, decomposition, critic |
| Tools | none, code, verifier, retrieval, combinations |
| Memory | none, context-only, structured persistent state |
| Agents | 1, 2, 8+ when justified |
| Feedback | none, deterministic verifier, independent critic |
| Horizon | short, medium, extended |
| Environment | stateless sandbox, persistent sandbox, synthetic shared world |

Every experimental cell must have an explicit identifier and frozen configuration hash.

## Causal characterization

A surprising successful trajectory is an anecdote until it survives ablation.

For any candidate capability gain, investigate:

1. Does the result reproduce?
2. Does it disappear when the suspected enabling component is removed?
3. Does it transfer to a second task family?
4. Does it reproduce with a second model family?
5. Does it survive an independently implemented verifier?
6. Can the first material trajectory divergence be located?
7. Did any unauthorized state transition contribute?

The intended evidence ladder is:

```text
anecdote
  < repeatable phenomenon
  < causally characterized phenomenon
  < independently replicated capability
```

## Safety boundary

Capability-discovery experiments begin in offline or synthetic environments.

The acting agent must not control:

- the governor;
- the experiment stop mechanism;
- the evaluator;
- holdout outcomes;
- permissions;
- network policy;
- audit records;
- provenance hashes.

Automatic pause conditions include unexpected boundary crossing, unapproved external communication, unexpected credential access, monitor modification attempts, evaluator modification, or persistent state outside the designated mechanism.

See [SAFETY_TIERS.md](SAFETY_TIERS.md).

## Relationship to Cohervia

This track extends Cohervia's existing question from:

> Can declining viability be detected before consequential failure?

to the related systems question:

> Can changes in the capability surface be observed as trajectory changes before the final outcome reveals them?

No new construct is treated as validated by this document.

## Source basis

This research direction is informed by current work on system-level and agentic capability evaluation, including:

- Google DeepMind, **AlphaEvolve: A Gemini-powered coding agent for designing advanced algorithms** — https://deepmind.google/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/
- METR, **Task-Completion Time Horizons of Frontier AI Models** — https://metr.org/time-horizons/
- OpenAI, **How we monitor internal coding agents for misalignment** — https://openai.com/index/how-we-monitor-internal-coding-agents-misalignment/
- OpenAI, **Our framework for reporting model misalignment** — https://openai.com/index/model-misalignment-reporting-framework/
- Anthropic, **Agentic misalignment: How LLMs could be insider threats** — https://www.anthropic.com/research/agentic-misalignment
- Romera-Paredes et al., **Mathematical discoveries from program search with large language models**, Nature 625 (2024), DOI 10.1038/s41586-023-06924-6.

These sources motivate hypotheses and methods. They are not Cohervia evidence.
