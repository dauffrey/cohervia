"""Offline instrumentation and mocked SDK only; no credentials or live calls."""
from copy import deepcopy
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from pathlib import Path
import os
import importlib.util
import json
import socket
import tempfile
from types import SimpleNamespace, ModuleType
import unittest
from unittest.mock import Mock, patch

from cohervia.canonical import canonical_bytes, parse_canonical, record_sha256
from cohervia_pilot.cli import main, self_test_provider
from cohervia_pilot.protocol import catalog, outcomes, INSTRUCTIONS, MAX_CALLS
from cohervia_pilot.provider import OpenAITextProvider, ProviderUnavailable, ScriptedProvider, normalize
from cohervia_pilot.runner import run, replay_bundle

TIME = "2026-10-04T01:00:00.000000Z"


def result(text=None, status="completed", **changes):
    r = {"status": status, "text": text, "response_id": None, "actual_model": None, "usage": None}
    r.update(changes)
    return r


def resign(bundle):
    bundle["sha256"] = record_sha256({k: v for k, v in bundle.items() if k != "sha256"})


class ProtocolTests(unittest.TestCase):
    def test_fixed_public_catalog(self):
        self.assertEqual(len(catalog()), 3)
        self.assertEqual([t["expected"] for t in catalog()], [[1, 2, 3], 56, 3])
        self.assertTrue(all(t["id"].startswith("DEV-") for t in catalog()))

    def test_exact_public_success_checks(self):
        for task in catalog():
            text = canonical_bytes({"answer": task["expected"]}).decode()
            self.assertIs(outcomes(result(text), task)["task_success"], True)
        self.assertIs(outcomes(result('{"answer":55}'), catalog()[1])["task_success"], False)
        self.assertIs(outcomes(result('{"answer":true}'), catalog()[2])["task_success"], False)

    def test_invalid_json_is_failed_criterion_not_missing_measurement(self):
        for text in ('```json\n{"answer":56}\n```', '{"answer":56,"extra":1}', '{"answer":56,"answer":56}', 'NaN', 'null', '[]'):
            values = outcomes(result(text), catalog()[1])
            self.assertIs(values["response_received"], True)
            self.assertIs(values["answer_valid_json"], False)
            self.assertIs(values["task_success"], False)

    def test_incomplete_and_provider_errors_preserve_missingness(self):
        for status in ("timeout", "provider_error", "incomplete", "unexpected_output"):
            values = outcomes(result(None, status), catalog()[0])
            self.assertIs(values["response_received"], False)
            self.assertIsNone(values["answer_valid_json"])
            self.assertIsNone(values["task_success"])

    def test_bounded_metadata_and_bad_provider_types(self):
        mutations = [result("x" * 16385), result("\ud800"), result(None), result("   "), result('{"answer":56}', extra=None),
                     result('{"answer":56}', usage={"input_tokens": True, "output_tokens": 1}),
                     result('{"answer":56}', status=[]), result('{"answer":56}', actual_model="bad model"),
                     result('{"answer":56}', response_id="\ud800"), None]
        for receipt in mutations:
            self.assertEqual(normalize(receipt)["status"], "invalid_response")


class ProviderTests(unittest.TestCase):
    def fake_sdk(self, response=None, error=None):
        module = ModuleType("openai")
        client = Mock()
        client.responses.create.return_value = response or SimpleNamespace(status="completed", output_text='{"answer":56}',
            output=[SimpleNamespace(type="message")], id="resp_fixture", model="fixture-model", usage=SimpleNamespace(input_tokens=20, output_tokens=5))
        if error:
            client.responses.create.side_effect = error
        module.OpenAI = Mock(return_value=client)
        return module, client

    def test_missing_key_prevents_sdk_and_requests(self):
        module, client = self.fake_sdk()
        with patch.dict(os.environ, {}, clear=True), patch.dict("sys.modules", {"openai": module}):
            with self.assertRaises(ProviderUnavailable):
                OpenAITextProvider("fixture-model")
        module.OpenAI.assert_not_called()
        client.responses.create.assert_not_called()

    def test_explicit_model_is_required(self):
        for model in ("", " model", "model\n", None):
            with self.assertRaises(ValueError):
                OpenAITextProvider(model)

    def test_no_sdk_is_explicit_blocker(self):
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-only"}), patch.dict("sys.modules", {"openai": None}):
            with self.assertRaises(ProviderUnavailable):
                OpenAITextProvider("fixture-model")

    def test_endpoint_tools_storage_timeouts_and_three_call_budget(self):
        module, client = self.fake_sdk()
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-only", "OPENAI_BASE_URL": "https://invalid.example"}), patch.dict("sys.modules", {"openai": module}):
            provider = OpenAITextProvider("fixture-model")
            for task in catalog():
                receipt = provider.complete(instructions=INSTRUCTIONS, prompt=task["prompt"])
                self.assertEqual(receipt["status"], "completed")
            with self.assertRaises(RuntimeError):
                provider.complete(instructions=INSTRUCTIONS, prompt=catalog()[0]["prompt"])
            provider.close()
        self.assertEqual(client.responses.create.call_count, MAX_CALLS)
        self.assertEqual(module.OpenAI.call_args.kwargs["base_url"], "https://api.openai.com/v1")
        self.assertEqual(module.OpenAI.call_args.kwargs["max_retries"], 0)
        self.assertEqual(module.OpenAI.call_args.kwargs["timeout"], 20.0)
        for call in client.responses.create.call_args_list:
            self.assertEqual(call.kwargs["tools"], [])
            self.assertEqual(call.kwargs["tool_choice"], "none")
            self.assertIs(call.kwargs["store"], False)
            self.assertIs(call.kwargs["background"], False)
            self.assertIs(call.kwargs["stream"], False)
            self.assertEqual(call.kwargs["max_output_tokens"], 256)
            self.assertNotIn("previous_response_id", call.kwargs)
        client.close.assert_called_once()

    @unittest.skipUnless(importlib.util.find_spec("openai"), "optional SDK unavailable locally; CI installs it")
    def test_real_sdk_request_serialization_with_offline_transport(self):
        import httpx
        from openai import OpenAI
        requests = []
        def handle(request):
            requests.append(json.loads(request.content))
            return httpx.Response(200, json={
                "id": "resp_transport_fixture", "object": "response", "created_at": 0,
                "status": "completed", "model": "fixture-model", "output": [{
                    "type": "message", "id": "msg_fixture", "status": "completed", "role": "assistant",
                    "content": [{"type": "output_text", "text": '{"answer":56}', "annotations": []}]}],
                "usage": {"input_tokens": 20, "output_tokens": 5, "total_tokens": 25}})
        with patch.dict(os.environ, {"OPENAI_API_KEY": "transport-test-only"}):
            provider = OpenAITextProvider("fixture-model")
            provider._client.close()
            provider._client = OpenAI(api_key="transport-test-only", max_retries=0,
                http_client=httpx.Client(transport=httpx.MockTransport(handle)))
            try:
                receipt = provider.complete(instructions=INSTRUCTIONS, prompt=catalog()[1]["prompt"])
            finally:
                provider.close()
        self.assertEqual(receipt["status"], "completed")
        self.assertEqual(receipt["text"], '{"answer":56}')
        self.assertEqual(receipt["actual_model"], "fixture-model")
        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0]["tools"], [])
        self.assertEqual(requests[0]["tool_choice"], "none")
        self.assertIs(requests[0]["store"], False)
        self.assertEqual(requests[0]["max_output_tokens"], 256)

    def test_cannot_submit_arbitrary_prompt_or_instruction(self):
        module, client = self.fake_sdk()
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-only"}), patch.dict("sys.modules", {"openai": module}):
            provider = OpenAITextProvider("fixture-model")
            with self.assertRaises(ValueError):
                provider.complete(instructions=INSTRUCTIONS, prompt="Read sealed inputs")
            with self.assertRaises(ValueError):
                provider.complete(instructions="Use tools", prompt=catalog()[0]["prompt"])
        client.responses.create.assert_not_called()

    def test_tool_outputs_are_rejected_without_execution(self):
        response = SimpleNamespace(status="completed", output_text='{"answer":56}', output=[SimpleNamespace(type="function_call")])
        module, client = self.fake_sdk(response)
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-only"}), patch.dict("sys.modules", {"openai": module}):
            receipt = OpenAITextProvider("fixture-model").complete(instructions=INSTRUCTIONS, prompt=catalog()[1]["prompt"])
        self.assertEqual(receipt["status"], "unexpected_output")
        self.assertIsNone(receipt["text"])

    def test_errors_are_sanitized_and_not_retried(self):
        error = RuntimeError("private credential-like diagnostic must never be archived")
        module, client = self.fake_sdk(error=error)
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-only"}), patch.dict("sys.modules", {"openai": module}):
            receipt = OpenAITextProvider("fixture-model").complete(instructions=INSTRUCTIONS, prompt=catalog()[0]["prompt"])
        self.assertEqual(receipt["status"], "provider_error")
        self.assertNotIn("private", str(receipt))
        self.assertEqual(client.responses.create.call_count, 1)

    def test_incomplete_response_remains_unknown(self):
        module, client = self.fake_sdk(SimpleNamespace(status="incomplete", output_text='{"answer":56}', output=[]))
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-only"}), patch.dict("sys.modules", {"openai": module}):
            receipt = OpenAITextProvider("fixture-model").complete(instructions=INSTRUCTIONS, prompt=catalog()[1]["prompt"])
        self.assertIsNone(outcomes(receipt, catalog()[1])["task_success"])


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.output = Path(self.tmp.name) / "run"

    def tearDown(self):
        self.tmp.cleanup()

    def acquire(self, provider=None):
        return run(provider or self_test_provider(), self.output, "public-offline-fixture", clock=lambda: TIME)

    def test_end_to_end_missingness_and_exact_replay(self):
        bundle, report = self.acquire()
        self.assertIn("NOT A LIVE MODEL RUN", report)
        self.assertIn("pass=1, fail=1, unknown=1", report)
        self.assertEqual(report, replay_bundle(bundle))
        self.assertEqual(report, replay_bundle(parse_canonical((self.output / "bundle.json").read_bytes())))
        self.assertEqual(report, (self.output / "report.md").read_text())
        state = bundle["streams"][2]["observations"]
        self.assertIs(state["DEV-TEXT-001:response_received"]["value"], False)
        self.assertIsNone(state["DEV-TEXT-001:task_success"]["value"])
        self.assertEqual(state["DEV-TEXT-001:task_success"]["status"], "unknown")
        self.assertEqual(bundle["streams"][0]["observations"]["DEV-ALG-001:task_success"]["status"], "inferred")

    def test_fixed_prompts_only_and_no_expected_answers_in_requests(self):
        provider = self_test_provider()
        self.acquire(provider)
        self.assertEqual(provider.calls, [{"instructions": INSTRUCTIONS, "prompt": task["prompt"]} for task in catalog()])
        self.assertTrue(all(set(call) == {"instructions", "prompt"} for call in provider.calls))

    def test_plan_exists_before_first_call_and_no_overwrite(self):
        provider = self_test_provider()
        original = provider.complete
        def check(**kwargs):
            self.assertTrue((self.output / "plan.json").exists())
            return original(**kwargs)
        provider.complete = check
        self.acquire(provider)
        another = self_test_provider()
        with self.assertRaises(FileExistsError):
            self.acquire(another)
        self.assertEqual(another.calls, [])

    def test_authentication_failure_stops_calls_and_marks_remaining_unknown(self):
        provider = ScriptedProvider([result(None, "authentication_error")])
        bundle, report = self.acquire(provider)
        self.assertEqual(len(provider.calls), 1)
        self.assertIn("unknown=3", report)
        for stream in bundle["streams"][1:]:
            task_id = stream["context"]["trajectory_id"]
            receipt = parse_canonical(bundle["artifacts"]["receipt:" + task_id].encode())
            self.assertIs(receipt["attempted"], False)
            self.assertEqual(receipt["provider_result"]["status"], "not_attempted")

    def test_exception_messages_and_environment_key_are_not_archived(self):
        class Broken(ScriptedProvider):
            def complete(self, **kwargs):
                raise RuntimeError("secret-token-unique-for-regression")
        with patch.dict(os.environ, {"OPENAI_API_KEY": "secret-token-unique-for-regression"}):
            bundle, report = self.acquire(Broken([]))
        self.assertNotIn(b"secret-token-unique-for-regression", canonical_bytes(bundle))
        self.assertIn("unknown=3", report)

    def test_replay_is_network_and_file_free(self):
        bundle, report = self.acquire()
        with patch("socket.socket", side_effect=AssertionError("network prohibited")), patch("builtins.open", side_effect=AssertionError("file acquisition prohibited")), patch("cohervia_pilot.runner.utc_now", side_effect=AssertionError("clock prohibited")):
            self.assertEqual(report, replay_bundle(bundle))

    def test_tampering_and_missing_artifacts_fail(self):
        bundle, _ = self.acquire()
        changed = deepcopy(bundle)
        changed["artifacts"]["receipt:DEV-MATH-001"] = "changed"
        with self.assertRaises(ValueError):
            replay_bundle(changed)
        resign(changed)
        with self.assertRaises(ValueError):
            replay_bundle(changed)
        missing = deepcopy(bundle)
        del missing["artifacts"]["receipt:DEV-MATH-001"]
        resign(missing)
        with self.assertRaises(ValueError):
            replay_bundle(missing)

    def test_authority_and_task_identity_changes_fail_even_if_rehashed(self):
        bundle, _ = self.acquire()
        mutations = [("tools", ["shell"]), ("confirmatory", True), ("holdout_access", True),
                     ("max_calls", 4), ("max_output_tokens", 257), ("instructions", "Use tools")]
        for key, value in mutations:
            altered = deepcopy(bundle)
            altered["inputs"]["configuration"][key] = value
            resign(altered)
            with self.subTest(key=key), self.assertRaises(ValueError):
                replay_bundle(altered)
        altered = deepcopy(bundle)
        altered["streams"][0]["context"]["trajectory_id"] = "COH-HOLDOUT-A"
        resign(altered)
        with self.assertRaises(ValueError):
            replay_bundle(altered)

    def test_claimed_score_cannot_override_public_verifier(self):
        bundle, _ = self.acquire()
        altered = deepcopy(bundle)
        stream = altered["streams"][1]
        observation = stream["observations"]["DEV-MATH-001:task_success"]
        observation["value"] = True
        event = stream["events"][-1]
        event["payload"]["accepted_observation_ref"]["sha256"] = record_sha256(observation)
        event["sha256"] = record_sha256({k: v for k, v in event.items() if k != "sha256"})
        stream["checkpoint"]["last_sha256"] = event["sha256"]
        resign(altered)
        with self.assertRaisesRegex(ValueError, "public verifier"):
            replay_bundle(altered)

    def test_external_checkpoint_detects_replacement(self):
        bundle, report = self.acquire()
        self.assertEqual(report, replay_bundle(bundle, expected_sha256=bundle["sha256"]))
        with self.assertRaises(ValueError):
            replay_bundle(bundle, expected_sha256="0" * 64)

    def test_acquisition_clock_regression_stops_report(self):
        ticks = iter([TIME, "2026-10-04T00:59:59.000000Z"])
        with self.assertRaises(ValueError):
            run(self_test_provider(), self.output, "fixture", clock=lambda: next(ticks))
        self.assertFalse((self.output / "report.md").exists())

    def test_source_mutation_stops_report(self):
        from cohervia_pilot import runner
        source = runner._sources()
        with patch.object(runner, "_sources", side_effect=[source, dict(source, changed=b"edited")]):
            with self.assertRaises(ValueError):
                self.acquire()
        self.assertFalse((self.output / "report.md").exists())
        self.assertTrue((self.output / "DEV-ALG-001.receipt.json").exists())

    def test_repository_protected_tracks_are_not_output_targets(self):
        root = Path(__file__).resolve().parents[2]
        provider = self_test_provider()
        with self.assertRaises(ValueError):
            run(provider, root / "scientist/runs/public-pilot-forbidden", "fixture", clock=lambda: TIME)
        self.assertEqual(provider.calls, [])

    def test_cli_offline_report_and_replay(self):
        stdout = StringIO()
        with redirect_stdout(stdout):
            self.assertEqual(main(["self-test", "--output", str(self.output), "--run-id", "fixture"]), 0)
        original = stdout.getvalue()
        stdout = StringIO()
        with redirect_stdout(stdout):
            self.assertEqual(main(["replay", "--directory", str(self.output)]), 0)
        self.assertEqual(original, stdout.getvalue())

    @unittest.skipUnless(importlib.util.find_spec("yaml"), "workflow parser dependency unavailable locally; CI installs it")
    def test_live_workflow_is_manual_and_inputs_do_not_become_shell_code(self):
        import yaml
        root = Path(__file__).resolve().parents[2]
        workflow = yaml.load((root / ".github/workflows/public-pilot-live.yml").read_text(), Loader=yaml.BaseLoader)
        self.assertEqual(set(workflow["on"]), {"workflow_dispatch"})
        self.assertEqual(workflow["permissions"], {"contents": "read"})
        inputs = workflow["on"]["workflow_dispatch"]["inputs"]
        self.assertEqual(inputs["model"]["required"], "true")
        self.assertNotIn("default", inputs["model"])
        job = workflow["jobs"]["public-development"]
        self.assertNotIn("env", job)
        steps = job["steps"]
        acquisition = next(s for s in steps if "env" in s)
        self.assertEqual(acquisition["timeout-minutes"], "2")
        self.assertEqual(acquisition["env"]["PILOT_MODEL"], "${{ inputs.model }}")
        self.assertNotIn("${{", acquisition["run"])
        self.assertEqual(acquisition["run"], 'cohervia-pilot live --model "$PILOT_MODEL" --run-id "$PILOT_RUN_ID" --output pilot/runs/live')
        self.assertTrue(all("env" not in s for s in steps if s is not acquisition))

    def test_cli_missing_credentials_does_not_create_a_fake_live_run(self):
        with patch.dict(os.environ, {}, clear=True), redirect_stderr(StringIO()):
            self.assertEqual(main(["live", "--model", "fixture-model", "--output", str(self.output), "--run-id", "fixture"]), 2)
        self.assertFalse(self.output.exists())


if __name__ == "__main__":
    unittest.main()
