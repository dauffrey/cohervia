# Deterministic qualification run

Mode: **scripted instrumentation only**. No live model was called.

- Cases: 7, in fixed Q01–Q07 order.
- Provider calls: 42 canned responses.
- Pipeline errors: 0.
- Structural check failures: 0.
- Human scientific-quality ratings: **all unknown/unassessed**.
- Qualification decision: **pending human review**.
- Execution authorization: **false**.
- Artifact verification: 92 preceding artifacts verified, plus the summary.

The compressed [archive](scripted-instrumentation.json.xz) preserves the exact requests, raw scripted responses, packets, errors, evaluations, protocol snapshots, and implementation/source provenance from this run. It is a xz-compressed JSON object with `format`, `summary`, and a `files` map of filenames to exact UTF-8 JSON text. No generated experiment code is run or supplied.

Archive SHA-256: `648ae05a5529a4ea61c382efff09ce37eee0e087448755d6c7363d56c1838393`.

The module hashes inside the start record identify the implementation bytes. The declared development baseline is `b62a9d4d93d98f39be938970d2ed1493d5043253`; actual Git commit identity is explicitly unknown. This artifact demonstrates instrumentation and preservation, not the quality of a model's science.
