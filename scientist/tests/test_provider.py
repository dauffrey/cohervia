import importlib.util
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from cohervia_scientist.provider import OpenAIProvider, ProviderResponseError


HAS_OPENAI = importlib.util.find_spec("openai") is not None


@unittest.skipUnless(HAS_OPENAI, "optional OpenAI adapter dependency is not installed")
class OpenAIProviderContractTests(unittest.TestCase):
    def response(self, *, status="completed", output_text='{"ok": true}', output_type="message"):
        return SimpleNamespace(
            status=status,
            output_text=output_text,
            output=[SimpleNamespace(type=output_type)],
        )

    def test_completed_response_uses_bounded_no_tool_request(self):
        with patch("openai.OpenAI") as openai_cls:
            client = openai_cls.return_value
            client.responses.create.return_value = self.response()
            provider = OpenAIProvider(model="test-model", reasoning_effort="high")
            text = provider.complete(instructions="rules", prompt="question")

            self.assertEqual(text, '{"ok": true}')
            openai_cls.assert_called_once_with(
                api_key=None,
                base_url="https://api.openai.com/v1",
                timeout=60.0,
                max_retries=0,
            )
            kwargs = client.responses.create.call_args.kwargs
            self.assertEqual(kwargs["model"], "test-model")
            self.assertEqual(kwargs["tools"], [])
            self.assertFalse(kwargs["store"])
            self.assertEqual(kwargs["max_output_tokens"], 8000)
            self.assertEqual(kwargs["reasoning"], {"effort": "high"})

    def test_incomplete_response_preserves_bounded_partial_text(self):
        with patch("openai.OpenAI") as openai_cls:
            client = openai_cls.return_value
            client.responses.create.return_value = self.response(
                status="incomplete", output_text='{"partial":'
            )
            provider = OpenAIProvider(model="test-model")
            with self.assertRaises(ProviderResponseError) as raised:
                provider.complete(instructions="rules", prompt="question")
            self.assertEqual(raised.exception.output_text, '{"partial":')
            self.assertEqual(raised.exception.response_status, "incomplete")

    def test_completed_response_without_text_is_rejected(self):
        with patch("openai.OpenAI") as openai_cls:
            client = openai_cls.return_value
            client.responses.create.return_value = self.response(output_text=None)
            provider = OpenAIProvider(model="test-model")
            with self.assertRaises(ProviderResponseError) as raised:
                provider.complete(instructions="rules", prompt="question")
            self.assertIsNone(raised.exception.output_text)
            self.assertEqual(raised.exception.response_status, "missing_text")

    def test_unexpected_output_type_is_rejected(self):
        with patch("openai.OpenAI") as openai_cls:
            client = openai_cls.return_value
            client.responses.create.return_value = self.response(output_type="tool_call")
            provider = OpenAIProvider(model="test-model")
            with self.assertRaises(ProviderResponseError) as raised:
                provider.complete(instructions="rules", prompt="question")
            self.assertEqual(raised.exception.output_text, '{"ok": true}')
            self.assertEqual(raised.exception.response_status, "unexpected_tool_output")


if __name__ == "__main__":
    unittest.main()
