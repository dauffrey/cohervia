from __future__ import annotations

import argparse
import json
from pathlib import Path

from .ledger import AppendOnlyLedger
from .models import Anomaly, EpistemicState, FailureClass, FailurePostmortem, Prediction
from .provider import OpenAIProvider
from .reasoning import ScientificReasoner, write_packet
from .theory import TheoryGraph


def root_from_args(args: argparse.Namespace) -> Path:
    return Path(args.root).absolute()


def repo_root_from_scientist(scientist_root: Path) -> Path:
    return scientist_root.parent.absolute()


def cmd_status(args: argparse.Namespace) -> int:
    root = root_from_args(args)
    theory = TheoryGraph.load(root / "state" / "theory_graph.json")
    payload = {
        "version": "0.2.0",
        "theory": theory.summary(),
        "predictions": len(AppendOnlyLedger(root / "state" / "predictions.jsonl").read_all()),
        "anomalies": len(AppendOnlyLedger(root / "state" / "anomalies.jsonl").read_all()),
        "failures": len(AppendOnlyLedger(root / "state" / "failures.jsonl").read_all()),
        "reasoning_engine": "available",
        "experiment_execution": "disabled",
        "confirmatory_holdout_access": "disabled",
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


def cmd_reason(args: argparse.Namespace) -> int:
    scientist_root = root_from_args(args)
    repo_root = repo_root_from_scientist(scientist_root)

    if args.provider != "openai":
        raise ValueError("CLI currently supports provider=openai")

    provider = OpenAIProvider(
        model=args.model,
        reasoning_effort=args.reasoning_effort,
    )
    reasoner = ScientificReasoner(
        provider=provider,
        repo_root=repo_root,
        scientist_root=scientist_root,
        hypothesis_count=args.hypothesis_count,
        memory_limit=args.memory_limit,
    )
    packet = reasoner.run(question_override=args.question)

    output = write_packet(packet, Path(args.output) if args.output else None,
                          scientist_root=scientist_root)
    print(str(output))
    print(f"status={packet.status}")
    return 0 if packet.status == "candidate_reasoning" else 2


def bounded_integer(minimum: int, maximum: int):
    def parse(value: str) -> int:
        try:
            parsed = int(value)
        except ValueError as exc:
            raise argparse.ArgumentTypeError("expected an integer") from exc
        if not minimum <= parsed <= maximum:
            raise argparse.ArgumentTypeError(f"must be between {minimum} and {maximum}")
        return parsed
    return parse


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

    reason = sub.add_parser("reason")
    reason.add_argument("--provider", choices=["openai"], default="openai")
    reason.add_argument("--model", required=True, help="API model identifier available to your account")
    reason.add_argument(
        "--reasoning-effort",
        choices=["low", "medium", "high", "xhigh"],
        default="high",
    )
    reason.add_argument("--question")
    reason.add_argument("--hypothesis-count", type=bounded_integer(2, 8), default=4)
    reason.add_argument("--memory-limit", type=bounded_integer(1, 20), default=6)
    reason.add_argument("--output")
    reason.set_defaults(func=cmd_reason)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
