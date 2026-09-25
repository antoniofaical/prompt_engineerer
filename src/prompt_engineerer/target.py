import re

from .config import TargetAI
from .errors import AppError

ALIASES = {
    "openai": "openai",
    "open ai": "openai",
    "chatgpt": "openai",
    "anthropic": "anthropic",
    "claude": "anthropic",
    "google": "google",
    "gemini": "google",
    "meta": "meta",
    "mistral": "mistral",
    "xai": "xai",
    "x.ai": "xai",
}
MODEL_FAMILIES = {
    "openai": r"(?:gpt-\d[\w.-]*|o[134](?:-[\w.-]+)?)",
    "anthropic": r"claude(?:[- ][\w. -]+)?",
    "google": r"gemini(?:[- ][\w. -]+)?",
    "meta": r"llama(?:[- ][\w. -]+)?",
    "mistral": r"(?:mistral|codestral|magistral)(?:[- ][\w. -]+)?",
    "xai": r"grok(?:[- ][\w. -]+)?",
}


def inspect_target(target: TargetAI) -> tuple[TargetAI, str | None]:
    raw = target.provider.casefold()
    provider = ALIASES.get(raw, raw)
    model = target.model.strip()
    inferred = next(
        (
            name
            for name, pattern in MODEL_FAMILIES.items()
            if re.fullmatch(pattern, model.casefold())
        ),
        "",
    )
    if provider in MODEL_FAMILIES and inferred and provider != inferred:
        raise AppError(
            "target_ai.provider e target_ai.model indicam fornecedores diferentes. "
            "Corrija user/configs.toml."
        )
    if raw and raw not in ALIASES:
        return TargetAI(
            provider=provider, model=model
        ), "Provedor não reconhecido no catálogo local."
    if model and not inferred:
        return TargetAI(provider=provider, model=model), "Modelo ambíguo ou fora do catálogo local."
    return TargetAI(provider=provider or inferred, model=model), None


def resolve_target(target: TargetAI, allow_questions: bool, ui) -> TargetAI:
    resolved, warning = inspect_target(target)
    if warning:
        ui.say(f"[AVISO] {warning} Isso não significa que ele seja inválido.")
        if allow_questions:
            answer = ui.ask(
                "Digite g para continuar com orientações gerais, ou Enter para encerrar "
                "e ajustar target_ai em user/configs.toml."
            )
            if answer.casefold() != "g":
                raise AppError(
                    "Ajuste target_ai e execute novamente; resultado anterior preservado."
                )
        else:
            ui.say("Perguntas desativadas: serão usadas orientações gerais.")
        resolved = TargetAI()
    ui.say(
        f"[DESTINO] Provedor: {resolved.provider or 'não especificado'}; "
        f"modelo: {resolved.model or 'não especificado'}."
    )
    if not target.provider and resolved.provider:
        ui.say("Provedor inferido pela família do nome; isso não verifica acesso ao modelo.")
    return resolved
