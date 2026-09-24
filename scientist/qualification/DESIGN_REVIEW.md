# Qualification design critique

This review is part of the implementation session, not an independent scientific assessment.

| Risk identified | Design response | Remaining limitation |
| --- | --- | --- |
| Circular grading by the same LLM | No LLM judge or automatic quality scores; anchored human rubric | Human agreement and rubric validity are not established |
| Canned success presented as model performance | Explicit scripted/injected/live modes; quality remains unknown | No live model evaluation was performed |
| Presence checks mistaken for scientific merit | Separate structural checks; tests deliberately show overclaiming can evade them | Semantic scientific review is essential |
| Synthetic failure fixtures mistaken for actual negative findings | Every record is labeled as an illustrative instrumentation stimulus | Does not assess retrieval from a large real history |
| Model ignores mistakes but repeats their IDs | ID citation is only a diagnostic; human rubric demands a concrete change | Lesson uptake is not mechanically proven |
| Safe abstention penalized for missing design | Unassessed experiment fields instead of zero | A human must decide if abstention was scientifically justified |
| Failed samples omitted | Fixed order, all seven case results, explicit error counts | Interrupted/disk-failed runs can remain incomplete |
| Malformed or partial output disappears | Save request before call and output before parsing; partial provider text carried into archive | Outputs above 1 MB are hash/length recorded but not fully preserved |
| Transport messages leak credentials | Record error types without exception messages | Provider text itself must still be handled as potentially sensitive |
| Archive summaries can diverge from packets or misstate run identity | Bind summary mode/suite/rubric identity to the archived start/protocol; verify fixed protocol hashes, artifact hashes, trace bindings, case coverage, and recompute checks/counts | Hashes are not signatures; coordinated rewriting is not detectable without external custody |
| Grading expectations leak into generation | Review focus/rubric excluded from role prompts | Public development suite can be learned or manually overfit |
| One run or score unlocks execution | No aggregate grade, auto-qualification, or new authority | Further capability work requires a separate review |
| Generalization overstated | Seven bounded topical probes with explicit scope | Neither broad research competence nor Cohervia effectiveness is established |

Deterministic adversarial tests cover lost memory citations, collapsed mechanism/prediction diversity, ignored critic vetoes, holdout flags, empty baselines/falsifiers, corrupted artifacts, manipulated summary counts, provider failures, partial responses, and all-rejected packets. These tests validate harness behavior, not model scientific judgment.
