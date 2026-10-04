"""Explicit live run, unmistakable offline self-test, or network-free archive replay."""
import argparse
from pathlib import Path
import sys

from cohervia.canonical import parse_canonical
from .provider import OpenAITextProvider, ProviderUnavailable, ScriptedProvider
from .runner import replay_bundle, run


def self_test_provider():
    return ScriptedProvider([
        {"status": "completed", "text": '{"answer":[1,2,3]}', "response_id": None, "actual_model": None, "usage": None},
        {"status": "completed", "text": '{"answer":55}', "response_id": None, "actual_model": None, "usage": None},
        {"status": "timeout", "text": None, "response_id": None, "actual_model": None, "usage": None},
    ])


def main(argv=None):
    parser = argparse.ArgumentParser(description="Public development only; no tools or confirmatory holdouts")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("live", "self-test"):
        command = commands.add_parser(name)
        command.add_argument("--output", required=True, help="fresh owned run directory; never overwrite")
        command.add_argument("--run-id", required=True)
        if name == "live":
            command.add_argument("--model", required=True, help="explicit API model identifier; no implicit default")
    command = commands.add_parser("replay")
    command.add_argument("--directory", required=True, help="existing pilot run directory")
    command.add_argument("--expected-sha256", help="optional independently retained bundle checkpoint")
    args = parser.parse_args(argv)
    try:
        if args.command == "replay":
            bundle = parse_canonical((Path(args.directory) / "bundle.json").read_bytes())
            report = replay_bundle(bundle, expected_sha256=args.expected_sha256)
        else:
            provider = OpenAITextProvider(args.model) if args.command == "live" else self_test_provider()
            _, report = run(provider, args.output, args.run_id)
        print(report, end="")
        return 0
    except ProviderUnavailable as exc:
        print("Live pilot blocked: " + str(exc), file=sys.stderr)
        return 2
    except (ValueError, OSError, TypeError, KeyError, RecursionError):
        print("Pilot validation/storage failed; no verified report. Existing raw receipts are retained.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
