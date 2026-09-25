import tomllib
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from .credentials import resolve_api_key
from .errors import AppError


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class TargetAI(StrictModel):
    provider: str = ""
    model: str = ""

    @field_validator("provider", "model")
    @classmethod
    def clean_name(cls, value: str) -> str:
        if len(value) > 120 or any(ord(c) < 32 for c in value):
            raise ValueError("use um nome de até 120 caracteres, sem quebras de linha")
        return value.strip()


class UserConfig(StrictModel):
    api_key_env_var: str = Field(default="OPENAI_API_KEY", pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    target_interface: Literal["chat", "api_user", "api_system"] = "chat"
    output_language: str = Field(default="auto", min_length=1, max_length=80)
    max_clarification_rounds: int = Field(default=3, ge=0, le=10)
    max_revision_rounds: int = Field(default=2, ge=0, le=5)
    target_tools: list[Literal["web_browsing", "code_execution", "file_reading"]] | None = None
    target_ai: TargetAI = Field(default_factory=TargetAI)

    @field_validator("output_language")
    @classmethod
    def clean_language(cls, value: str) -> str:
        if not value.strip() or any(ord(c) < 32 for c in value):
            raise ValueError("informe auto ou um idioma, sem quebras de linha")
        return value.strip()


def load_config(root: Path) -> UserConfig:
    path = root / "user/configs.toml"
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise AppError("Falta user/configs.toml. Execute o bootstrap.") from exc
    except (tomllib.TOMLDecodeError, UnicodeError) as exc:
        # Never echo parser input: the user may accidentally paste a key here.
        raise AppError(
            "TOML inválido em user/configs.toml. Confira aspas, tabelas e tipos."
        ) from exc
    try:
        return UserConfig.model_validate(data)
    except ValidationError as exc:
        issues = [f"{'.'.join(map(str, e['loc']))}: {e['type']}" for e in exc.errors()]
        raise AppError("Configuração inválida: " + "; ".join(issues)) from exc


def read_api_key(config: UserConfig) -> str:
    return resolve_api_key(config.api_key_env_var)
