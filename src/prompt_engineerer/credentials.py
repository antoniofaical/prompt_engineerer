"""Resolve a named credential without logging or persisting its value."""

import os
import sys
from importlib import import_module

from .errors import AppError

WINDOWS = sys.platform == "win32"


def _windows_persistent_value(name: str) -> str | None:
    registry = import_module("winreg")
    scopes = (
        (registry.HKEY_CURRENT_USER, "Environment"),
        (
            registry.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
        ),
    )
    unreadable = False
    for hive, path in scopes:
        try:
            with registry.OpenKey(hive, path, 0, registry.KEY_READ) as key:
                value, kind = registry.QueryValueEx(key, name)
            if kind not in (registry.REG_SZ, registry.REG_EXPAND_SZ) or not isinstance(value, str):
                continue
            if kind == registry.REG_EXPAND_SZ:
                value = registry.ExpandEnvironmentStrings(value)
            if value.strip():
                return value.strip()
        except FileNotFoundError:
            continue
        except OSError:
            unreadable = True
    if unreadable:
        raise AppError(
            f"Não foi possível ler todos os locais de {name} no Windows. "
            "Verifique as permissões de leitura das variáveis de usuário/sistema."
        )
    return None


def resolve_api_key(name: str) -> str:
    """Process > Windows User > Windows Machine; never modify the environment."""
    value = os.environ.get(name, "").strip()
    if value:
        return value
    if WINDOWS:
        value = _windows_persistent_value(name)
        if value:
            return value
        raise AppError(
            f"Variável {name} ausente ou vazia no processo e nas variáveis de usuário/sistema "
            "do Windows. Cadastre-a com esse nome ou ajuste api_key_env_var em user/configs.toml."
        )
    raise AppError(
        f"Variável {name} ausente ou vazia no ambiente do processo. "
        "Exporte-a no shell ou configure o ambiente do serviço que executa o programa."
    )
