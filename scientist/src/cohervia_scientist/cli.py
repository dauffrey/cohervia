from __future__ import annotations

import argparse
import json
from pathlib import Path

from .ledger import AppendOnlyLedger
from .models import Anomaly, EpistemicState, FailureClass, FailurePostmortem, Prediction
from .theory import TheoryGraph


def root_from_args(args: argparse.Namespace) -> Path:
    return Path(args.root).resolve()


def cmd_status(args: argparse.Namespace) -> int:
    root = root_from_args(args)
    theory = TheoryGraph.load(root / "state" / "theory_graph.json")
    payload = {
        "theory": theory.summary(),
        "predictions": len(AppendOnlyLedger(root / "state" / "predictions.jsonl").read_all()),
        "anomalies": len(AppendOnlyLedger(root / "state" / "anomalies.jsonl").read_all()),
        "failures": len(AppendOnlyLedger(root / "state" / "failures.jsonl").read_all()),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


def cmd_prediction(args: argparse.Namespace) -> int:
    root = root_from_args(args)
    record = Prediction(
        claim=args.claim,
        theory_version=args.theory_version,
        confidence=args.confidence,
        falsifies=args.falsifies or [],
        experiment_id=args.experiment_id,
    )
    AppendOnlyLedger(root / "state" / "predictions.jsonl").append(record.to_dict())
    print(record.id)
    return 0


def cmd_anomaly(args: argparse.Namespace) -> int:
    root = root_from_args(args)
    record = Anomaly(
        observed=args.observed,
        expected=args.expected,
        theory_version=args.theory_version,
        explanation_state=EpistemicState(args.explanation_state),
        competing_hypotheses=args.competing_hypotheses or [],
        priority=args.priority,
    )
    AppendOnlyLedger(root / "state" / "anomalies.jsonl").append(record.to_dict())
    print(record.id)
    return 0


def cmd_failure(args: argparse.Namespace) -> int:
    root = root_from_args(args)
    record = FailurePostmortem(
        hypothesis=args.hypothesis,
        observed=args.observed,
        failure_class=FailureClass(args.failure_class),
        lesson=args.lesson,
        theory_version=args.theory_version,
        cause=args.cause,
        affected_constructs=args.affected_constructs or [],
        theory_change=args.theory_change,
        unresolved=args.unresolved or [],
        follow_up=args.follow_up or [],
    )
    AppendOnlyLedger(root / "state" / "failures.jsonl").append(record.to_dict())
    print(record.id)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cohervia-scientist")
    parser.add_argument(
        "--root",
        default=str(Path(__file__).resolve().parents[2]),
        help="scientist project root containing state/",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status")
    status.set_defaults(func=cmd_status)

    prediction = sub.add_parser("record-prediction")
    prediction.add_argument("--claim", required=True)
    prediction.add_argument("--theory-version", required=True)
    prediction.add_argument("--confidence", type=float)
    prediction.add_argument("--falsifies", action="append")
    prediction.add_argument("--experiment-id")
    prediction.set_defaults(func=cmd_prediction)

    anomaly = sub.add_parser("record-anomaly")
    anomaly.add_argument("--observed", required=True)
    anomaly.add_argument("--expected", required=True)
    anomaly.add_argument("--theory-version", required=True)
    anomaly.add_argument(
        "--explanation-state",
        choices=[state.value for state in EpistemicState],
        default=EpistemicState.UNKNOWN.value,
    )
    anomaly.add_argument("--competing-hypotheses", action="append")
    anomaly.add_argument("--priority", default="medium")
    anomaly.set_defaults(func=cmd_anomaly)

    failure = sub.add_parser("record-failure")
    failure.add_argument("--hypothesis", required=True)
    failure.add_argument("--observed", required=True)
    failure.add_argument(
        "--failure-class",
        choices=[item.value for item in FailureClass],
        required=True,
    )
    failure.add_argument("--lesson", required=True)
    failure.add_argument("--theory-version", required=True)
    failure.add_argument("--cause")
    failure.add_argument("--affected-constructs", action="append")
    failure.add_argument("--theory-change")
    failure.add_argument("--unresolved", action="append")
    failure.add_argument("--follow-up", action="append")
    failure.set_defaults(func=cmd_failure)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
