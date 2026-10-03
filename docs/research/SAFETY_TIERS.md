# Capability-discovery safety tiers

## Purpose

This document defines conservative environment tiers for Cohervia capability-discovery research.

The tiers govern **where experiments may run**, not whether a model is considered aligned or safe.

## Tier Green — offline formal sandbox

Appropriate for:

- mathematics;
- algorithms;
- formal proofs;
- synthetic reasoning;
- representation discovery;
- deterministic simulators.

Required controls:

- no public network access;
- immutable evaluator;
- complete event logging;
- reproducible environment definition;
- bounded compute/time budget.

## Tier Yellow — isolated agent sandbox

Appropriate for:

- persistent memory studies;
- long-horizon benign software tasks;
- multi-agent coordination in synthetic worlds;
- tool-factorial experiments;
- reward/evaluator robustness studies using synthetic targets.

Additional controls:

- namespace isolation;
- instrumented shared state;
- explicit channel inventory;
- no real credentials;
- synthetic services only;
- independent stop controller;
- **immutable or cryptographically append-only protected audit storage**.

For Yellow-tier evidence, "externally protected" is not sufficient by itself if historical records can still be edited in place. Acceptable implementations must make prior records tamper-evident and non-rewriteable under the experimental agent's authority, for example through WORM semantics or an externally controlled append-only hash chain.

## Tier Orange — restricted real services

Not part of the initial `COH-EXP-0001` programme.

Any future use requires a separate preregistration and explicit authorization.

Minimum controls would include:

- least privilege;
- read-only defaults;
- explicit egress policy;
- ephemeral credentials;
- human approval for consequential writes;
- independent monitoring;
- rollback/recovery plan.

## Tier Red — high-consequence or physical systems

Out of scope for the initial capability-discovery programme.

Examples include high-consequence physical systems, critical infrastructure, real offensive cybersecurity targets, and hazardous biological/chemical experimentation.

Such work requires institutional/specialist governance beyond the controls defined in this repository.

## Automatic pause conditions

A Green or Yellow experiment must pause if an agent unexpectedly:

- crosses a network/storage boundary;
- accesses a credential not explicitly provisioned for the trial;
- creates an unapproved communication mechanism;
- attempts to modify the monitor, evaluator, policy, or audit log;
- changes evaluation criteria instead of solving the task;
- creates persistent state outside the designated state mechanism;
- triggers an unexpected external side effect.

A paused run is preserved as evidence. It is not silently restarted or discarded.

## Authority rule

An experimental agent cannot authorize its own promotion to a less restrictive tier.

Tier transitions are external governance decisions and require a new or amended preregistration.
