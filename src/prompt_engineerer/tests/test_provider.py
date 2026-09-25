import json

import httpx
import openai
import pytest

from prompt_engineerer.errors import AppError
from prompt_engineerer.provider import OpenAIProvider
from prompt_engineerer.schemas import Draft


def response_body():
    return {
        "id": "resp_test",
        "object": "response",
        "created_at": 1,
        "status": "completed",
        "error": None,
        "incomplete_details": None,
        "instructions": None,
        "model": "gpt-5-mini",
        "parallel_tool_calls": False,
        "output": [
            {
                "type": "message",
                "id": "msg_test",
                "status": "completed",
                "role": "assistant",
                "content": [
                    {
                        "type": "output_text",
                        "annotations": [],
                        "text": json.dumps({"markdown": "# Prompt\nTeste"}),
                    }
                ],
            }
        ],
        "tools": [],
        "tool_choice": "auto",
        "metadata": {},
        "temperature": 1,
        "top_p": 1,
        "usage": {
            "input_tokens": 20,
            "output_tokens": 10,
            "total_tokens": 30,
            "input_tokens_details": {"cached_tokens": 0},
            "output_tokens_details": {"reasoning_tokens": 0},
        },
    }


def make_provider(handler, ui):
    client = openai.OpenAI(
        api_key="fake-test-key",
        base_url="https://example.invalid/v1",
        max_retries=0,
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    return OpenAIProvider("fake-test-key", ui, client=client)


def test_real_sdk_serialization_and_parse(ui):
    seen = []

    def handler(request):
        seen.append(json.loads(request.content))
        assert request.url.path == "/v1/responses"
        return httpx.Response(200, json=response_body())

    provider = make_provider(handler, ui)
    try:
        result = provider.call("Gerar prompt", {"seed": "Teste"}, Draft)
        assert result.markdown.startswith("# Prompt")
        assert seen[0]["store"] is False
        assert seen[0]["text"]["format"]["type"] == "json_schema"
        assert "fake-test-key" not in json.dumps(seen)
        assert provider.input_tokens == 20
    finally:
        provider.close()


@pytest.mark.parametrize("status", [401, 403, 400, 404])
def test_permanent_error_no_retry_or_secret_echo(ui, status):
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(status, json={"error": {"message": "fake-test-key", "type": "test"}})

    provider = make_provider(handler, ui)
    try:
        with pytest.raises(AppError) as exc:
            provider.call("Gerar prompt", {}, Draft)
        assert "fake-test-key" not in str(exc.value)
        assert len(calls) == 1
    finally:
        provider.close()


def test_transient_retry_bounded(ui, monkeypatch):
    monkeypatch.setattr("prompt_engineerer.provider.time.sleep", lambda seconds: None)
    provider = make_provider(
        lambda r: httpx.Response(429, json={"error": {"message": "limit"}}), ui
    )
    try:
        with pytest.raises(AppError, match="persistente"):
            provider.call("Gerar prompt", {}, Draft)
        assert provider.calls == 3
    finally:
        provider.close()


def test_refusal_not_written(ui):
    body = response_body()
    body["output"][0]["content"] = [{"type": "refusal", "refusal": "Cannot comply"}]
    provider = make_provider(lambda r: httpx.Response(200, json=body), ui)
    try:
        with pytest.raises(AppError, match="recusada"):
            provider.call("Gerar prompt", {}, Draft)
    finally:
        provider.close()
