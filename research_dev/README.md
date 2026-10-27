# Capability self-assessment — offline development contract

This directory implements a **pure-Python, development-only** three-stage record validator. It does not connect to an AI provider, run experiments, access holdouts, authenticate records, or authorize actions.

Run from the repository root with Python 3.11+:

```sh
python -m unittest discover -s research_dev -p 'test_*.py' -v
```

The record requires a pre-task prediction, a separately linked attempt, and a verdict. SHA-256 digests detect inconsistent stage contents, not coordinated rewriting or malicious tampering. The verifier identity is a string, **not** proof of independence. The helper `make_record` is intended only for fabricated test data; it does not calculate ground truth. No answer key is transmitted to a model by this module, because there is no model interface.

A completed response must have a Boolean verdict; an incomplete/error response must have an unknown verdict. The Brier score is computed only for observed outcomes. Every returned result explicitly says `scientific_evidence=false` and `execution_authorized=false`.

Next: independent code review, integration with the existing pilot's replayable evidence bundle, and a separately authorized live development smoke test. No COH-EXP-0001 execution or baseline changes are implied.
