import json
import time
from typing import TypeVar

import openai
from pydantic import BaseModel, ValidationError

from .errors import AppError
from .files import RESOURCES
from .technical import (
    API_MAX_RETRIES,
    API_TIMEOUT_SECONDS,
    BASE_URL,
    MAX_OUTPUT_TOKENS,
    MODEL,
)

T = TypeVar("T", bound=BaseModel)


class OpenAIProvider:
    def __init__(self, api_key: str, ui, client=None):
        self.ui = ui
        self.client = client or openai.OpenAI(
            api_key=api_key,
            base_url=BASE_URL,
            timeout=API_TIMEOUT_SECONDS,
            max_retries=0,
        )
        self.instructions = (RESOURCES / "system.md").read_text(encoding="utf-8")
        self.calls = 0
        self.input_tokens = 0
        self.output_tokens = 0

    def call(self, stage: str, payload: dict, schema: type[T]) -> T:
        for attempt in range(API_MAX_RETRIES + 1):
            try:
                with self.ui.stage(stage):
                    self.calls += 1
                    response = self.client.responses.parse(
                        model=MODEL,
                        instructions=self.instructions,
                        input=json.dumps({"stage": stage, "data": payload}, ensure_ascii=False),
                        text_format=schema,
                        max_output_tokens=MAX_OUTPUT_TOKENS,
                        store=False,
                    )
                    if response.usage:
                        self.input_tokens += response.usage.input_tokens
                        self.output_tokens += response.usage.output_tokens
                    if response.status != "completed" or response.output_parsed is None:
                        raise AppError(
                            "Resposta recusada, incompleta ou sem dados estruturados. "
                            "O resultado anterior foi preservado."
                        )
                    return response.output_parsed
            except (openai.AuthenticationError, openai.PermissionDeniedError) as exc:
                raise AppError(
                    "API recusou a credencial ou o acesso ao modelo gerador. "
                    "Verifique a chave e as permissões da conta OpenAI."
                ) from exc
            except (openai.APIConnectionError, openai.RateLimitError) as exc:
                retry_error = exc
            except openai.APIStatusError as exc:
                if exc.status_code not in (408, 409) and exc.status_code < 500:
                    raise AppError(
                        f"API retornou HTTP {exc.status_code}. Confira o modelo técnico "
                        "e a compatibilidade do SDK; veja o README."
                    ) from exc
                retry_error = exc
            except ValidationError as exc:
                raise AppError("A API retornou dados fora do esquema esperado.") from exc
            except openai.OpenAIError as exc:
                raise AppError(
                    "Falha ao interpretar a resposta da API; resultado preservado."
                ) from exc
            if attempt == API_MAX_RETRIES:
                raise AppError(
                    "Falha transitória persistente: verifique conexão, quota e limites da API."
                ) from retry_error
            delay = min(2 ** (attempt + 1), 8)
            self.ui.say(f"[AVISO] Nova tentativa {attempt + 1}/{API_MAX_RETRIES} em {delay}s.")
            time.sleep(delay)
        raise AssertionError("unreachable")

    def close(self):
        self.client.close()
