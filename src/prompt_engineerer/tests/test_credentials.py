import os
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from prompt_engineerer import cli, credentials
from prompt_engineerer.config import UserConfig, read_api_key
from prompt_engineerer.errors import AppError

NAME = "PROMPT_ENG_OPENAI_API_KEY"


@pytest.fixture
def registry(monkeypatch):
    values = {}
    calls = []

    def query(hive, name):
        calls.append((hive, name))
        value = values.get(hive, FileNotFoundError())
        if isinstance(value, Exception):
            raise value
        return value

    def open_key(hive, path, reserved, access):
        expected = {
            "user": "Environment",
            "machine": r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
        }
        assert path == expected[hive]
        assert reserved == 0 and access == 0x20019
        return nullcontext(hive)

    fake = SimpleNamespace(
        HKEY_CURRENT_USER="user",
        HKEY_LOCAL_MACHINE="machine",
        KEY_READ=0x20019,
        REG_SZ=1,
        REG_EXPAND_SZ=2,
        OpenKey=open_key,
        QueryValueEx=query,
        ExpandEnvironmentStrings=lambda value: value.replace("%TOKEN%", "expanded-test-key"),
    )
    monkeypatch.delenv(NAME, raising=False)
    monkeypatch.setattr(credentials, "WINDOWS", True)
    importer = Mock(return_value=fake)
    monkeypatch.setattr(credentials, "import_module", importer)
    return values, calls, importer


def test_process_value_has_precedence(registry, monkeypatch):
    values, calls, importer = registry
    values["user"] = ("user-test-key", 1)
    monkeypatch.setenv(NAME, " process-test-key ")
    assert read_api_key(UserConfig(api_key_env_var=NAME)) == "process-test-key"
    importer.assert_not_called()
    assert calls == []


def test_finds_new_user_variable_without_terminal_restart(registry):
    values, calls, importer = registry
    values["user"] = (" user-test-key ", 1)
    values["machine"] = ("machine-test-key", 1)
    assert credentials.resolve_api_key(NAME) == "user-test-key"
    assert calls == [("user", NAME)]
    importer.assert_called_once_with("winreg")
    assert NAME not in os.environ  # No mutation of the process or persistent environment.


@pytest.mark.parametrize("user_value", [FileNotFoundError(), ("  ", 1), (42, 4)])
def test_falls_back_to_machine(registry, user_value):
    values, calls, _ = registry
    values["user"] = user_value
    values["machine"] = ("machine-test-key", 1)
    assert credentials.resolve_api_key(NAME) == "machine-test-key"
    assert calls == [("user", NAME), ("machine", NAME)]


def test_blank_process_value_uses_persistent_value(registry, monkeypatch):
    values, _, _ = registry
    monkeypatch.setenv(NAME, " ")
    values["user"] = ("user-test-key", 1)
    assert credentials.resolve_api_key(NAME) == "user-test-key"


def test_expandable_registry_string(registry):
    values, _, _ = registry
    values["user"] = ("%TOKEN%", 2)
    assert credentials.resolve_api_key(NAME) == "expanded-test-key"


def test_denied_user_scope_still_checks_machine(registry):
    values, _, _ = registry
    values["user"] = PermissionError("sensitive-detail")
    values["machine"] = ("machine-test-key", 1)
    assert credentials.resolve_api_key(NAME) == "machine-test-key"


def test_registry_error_does_not_echo_exception(registry):
    values, _, _ = registry
    values["user"] = PermissionError("sensitive-detail")
    with pytest.raises(AppError, match="permissões") as error:
        credentials.resolve_api_key(NAME)
    assert "sensitive-detail" not in str(error.value)


def test_absent_everywhere_explains_where_to_register(registry):
    with pytest.raises(AppError, match="Cadastre-a"):
        credentials.resolve_api_key(NAME)


def test_non_windows_does_not_read_registry(monkeypatch):
    monkeypatch.delenv(NAME, raising=False)
    importer = Mock(side_effect=AssertionError("Registry must not be imported"))
    monkeypatch.setattr(credentials, "import_module", importer)
    with pytest.raises(AppError, match="Exporte-a"):
        credentials.resolve_api_key(NAME)
    importer.assert_not_called()


def test_check_and_normal_execution_resolve_same_saved_key(root, registry, monkeypatch, capsys):
    values, _, _ = registry
    values["user"] = ("user-test-key", 1)
    (root / "user/configs.toml").write_text(f'api_key_env_var = "{NAME}"\n', encoding="utf-8")
    monkeypatch.setattr(cli, "project_root", lambda: root)
    client = Mock(calls=0, input_tokens=0, output_tokens=0)
    factory = Mock(return_value=client)
    monkeypatch.setattr(cli, "OpenAIProvider", factory)
    monkeypatch.setattr(cli, "optimize", Mock())
    assert cli.main(["--check"]) == 0
    factory.assert_not_called()
    assert cli.main([]) == 0
    assert factory.call_args.args[0] == "user-test-key"
    assert "user-test-key" not in capsys.readouterr().out
