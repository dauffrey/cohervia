"""One text-only Responses call; no model tools, retries, history or custom endpoint."""
import os

from .protocol import MAX_CALLS, MAX_OUTPUT_TOKENS, MAX_TEXT_BYTES, TIMEOUT_SECONDS, INSTRUCTIONS, catalog, model_id


class ProviderUnavailable(RuntimeError):
    pass


def _receipt(status, text=None, response_id=None, actual_model=None, usage=None):
    return {"status": status, "text": text, "response_id": response_id,
            "actual_model": actual_model, "usage": usage}


def normalize(receipt):
    """Bounded allowlisted acquisition fields. Unexpected provider data stays unknown."""
    fields = {"status", "text", "response_id", "actual_model", "usage"}
    statuses = {"completed", "incomplete", "provider_error", "timeout", "authentication_error",
                "rate_limit", "connection_error", "unexpected_output", "invalid_response"}
    try:
        if type(receipt) is not dict or set(receipt) != fields or receipt["status"] not in statuses:
            return _receipt("invalid_response")
        text = receipt["text"]
        if text is not None and (type(text) is not str or len(text.encode("utf-8")) > MAX_TEXT_BYTES):
            return _receipt("invalid_response")
        if receipt["status"] == "completed" and (not text or not text.strip()):
            return _receipt("invalid_response")
        for field in ("response_id", "actual_model"):
            if receipt[field] is not None and not model_id(receipt[field]):
                return _receipt("invalid_response")
        usage = receipt["usage"]
        if usage is not None and (type(usage) is not dict or set(usage) != {"input_tokens", "output_tokens"}
                                  or any(type(v) is not int or not 0 <= v <= 9007199254740991 for v in usage.values())):
            return _receipt("invalid_response")
        return dict(receipt)
    except (TypeError, UnicodeError):
        return _receipt("invalid_response")


class OpenAITextProvider:
    kind = "openai_responses"

    def __init__(self, model):
        if not model_id(model):
            raise ValueError("explicit valid API model identifier required")
        if not os.environ.get("OPENAI_API_KEY"):
            raise ProviderUnavailable("OPENAI_API_KEY is not configured; no calls made")
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ProviderUnavailable("install pilot[openai]; no calls made") from exc
        self.model = model
        # Explicit key/endpoint ignores custom endpoint environment configuration.
        self._client = OpenAI(api_key=os.environ["OPENAI_API_KEY"], base_url="https://api.openai.com/v1",
                              timeout=TIMEOUT_SECONDS, max_retries=0)
        self._calls = 0

    def complete(self, *, instructions, prompt):
        if instructions != INSTRUCTIONS or prompt not in {task["prompt"] for task in catalog()}:
            raise ValueError("only the fixed public prompts and instruction are allowed")
        if self._calls >= MAX_CALLS:
            raise RuntimeError("pilot call budget exhausted")
        self._calls += 1
        try:
            response = self._client.responses.create(model=self.model, instructions=instructions,
                input=prompt, tools=[], tool_choice="none", store=False, background=False,
                stream=False, max_output_tokens=MAX_OUTPUT_TOKENS)
            if any(getattr(item, "type", "") not in {"message", "reasoning"} for item in getattr(response, "output", [])):
                return _receipt("unexpected_output")
            status = "completed" if getattr(response, "status", None) == "completed" else "incomplete"
            usage = getattr(response, "usage", None)
            usage = ({"input_tokens": getattr(usage, "input_tokens", None),
                      "output_tokens": getattr(usage, "output_tokens", None)} if usage is not None else None)
            return normalize(_receipt(status, getattr(response, "output_text", None),
                                      getattr(response, "id", None), getattr(response, "model", None), usage))
        except Exception as exc:
            # Do not archive exception messages/URLs/headers: they may contain secrets.
            code = {"APITimeoutError": "timeout", "AuthenticationError": "authentication_error",
                    "RateLimitError": "rate_limit", "APIConnectionError": "connection_error"}.get(type(exc).__name__, "provider_error")
            return _receipt(code)

    def close(self):
        self._client.close()


class ScriptedProvider:
    kind = "scripted_instrumentation"
    model = "scripted-fixture"

    def __init__(self, receipts):
        self.receipts = iter(receipts)
        self.calls = []

    def complete(self, *, instructions, prompt):
        if len(self.calls) >= MAX_CALLS:
            raise RuntimeError("pilot call budget exhausted")
        self.calls.append({"instructions": instructions, "prompt": prompt})
        return normalize(next(self.receipts))

    def close(self):
        pass
