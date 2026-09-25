import argparse

from .config import load_config, read_api_key
from .errors import AppError
from .files import initialize_user, project_root, read_seed
from .pipeline import load_catalog, optimize
from .provider import OpenAIProvider
from .target import inspect_target
from .ui import UI


def preflight(root, ui) -> bool:
    ready = True
    config = None
    for name, check in (
        ("Catálogo de guidelines", load_catalog),
        ("Seed", lambda: read_seed(root)),
    ):
        try:
            check()
            ui.say(f"[OK] {name}")
        except AppError as exc:
            ui.say(f"[PENDENTE] {exc}")
            ready = False
    try:
        config = load_config(root)
        ui.say("[OK] configs.toml")
        _, warning = inspect_target(config.target_ai)
        if warning:
            ui.say(f"[AVISO] {warning} Será possível usar orientações gerais.")
    except AppError as exc:
        ui.say(f"[PENDENTE] {exc}")
        ready = False
    if config:
        try:
            read_api_key(config)
            ui.say("[OK] Credencial disponível (autenticação não testada; nenhuma chamada paga).")
        except AppError as exc:
            ui.say(f"[PENDENTE] {exc}")
            ready = False
    return ready


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Leia user/seed_prompt.md e gere um prompt revisado."
    )
    parser.add_argument("--check", action="store_true", help="Preflight local, sem chamadas à API.")
    parser.add_argument(
        "--init", action="store_true", help="Crie apenas os arquivos locais ausentes."
    )
    args = parser.parse_args(argv)
    ui = UI()
    provider = None
    try:
        root = project_root()
        if args.init:
            created = initialize_user(root)
            ui.say(
                "[OK] Arquivos criados: " + (", ".join(created) or "nenhum; existentes preservados")
            )
            if not args.check:
                return 0
        if args.check:
            return 0 if preflight(root, ui) else 2
        with ui.stage("Validar entrada e configuração"):
            config = load_config(root)
            read_seed(root)
            key = read_api_key(config)
        provider = OpenAIProvider(key, ui)
        optimize(root, config, provider, ui)
        ui.say(f"[CONCLUÍDO] {root / 'user/optimized_prompt.md'}")
        ui.say(
            f"Chamadas tentadas: {provider.calls}; tokens informados pela API: "
            f"entrada={provider.input_tokens}, saída={provider.output_tokens}."
        )
        return 0
    except AppError as exc:
        ui.say(f"[ERRO] {exc}")
        return 1
    except OSError:
        ui.say("[ERRO] Falha de acesso a arquivo. Verifique permissões e espaço em disco.")
        return 1
    except KeyboardInterrupt:
        ui.say("\n[CANCELADO] Execução interrompida.")
        return 130
    finally:
        if provider:
            provider.close()
