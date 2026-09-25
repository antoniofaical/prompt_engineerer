import os

import pytest

from prompt_engineerer.config import UserConfig, load_config, read_api_key
from prompt_engineerer.errors import AppError
from prompt_engineerer.files import atomic_output, initialize_user, read_seed, run_lock


@pytest.mark.parametrize(
    "content",
    [
        "max_revision_rounds = -1",
        "max_revision_rounds = true",
        "max_clarification_rounds = 11",
        'target_interface = "unknown"',
        'target_tools = ["magic"]',
        'api_key_env_var = "bad name"',
        'output_language = "   "',
        'unknown_field = "secret-value"',
        '[target_ai]\nprovider = "openai"\nmax_revision_rounds = 2',
    ],
)
def test_invalid_config_reports_field_without_value(root, content):
    (root / "user/configs.toml").write_text(content, encoding="utf-8")
    with pytest.raises(AppError) as error:
        load_config(root)
    assert "secret-value" not in str(error.value)


def test_invalid_toml_does_not_echo_secret(root):
    (root / "user/configs.toml").write_text('api_key_env_var = "secret-value', encoding="utf-8")
    with pytest.raises(AppError) as error:
        load_config(root)
    assert "secret-value" not in str(error.value)


def test_tools_unknown_vs_none(root):
    assert load_config(root).target_tools is None
    (root / "user/configs.toml").write_text("target_tools = []", encoding="utf-8")
    assert load_config(root).target_tools == []


def test_environment_variable_custom_name(monkeypatch):
    config = UserConfig(api_key_env_var="MY_PROMPT_KEY")
    monkeypatch.setenv("MY_PROMPT_KEY", "  test-secret  ")
    assert read_api_key(config) == "test-secret"
    monkeypatch.setenv("MY_PROMPT_KEY", " ")
    with pytest.raises(AppError, match="MY_PROMPT_KEY"):
        read_api_key(config)


def test_bootstrap_templates_preserve_existing(root):
    paths = list((root / "user").iterdir())
    before = {p.name: p.read_bytes() for p in paths}
    assert initialize_user(root) == []
    assert {p.name: p.read_bytes() for p in paths} == before
    (root / "user/configs.toml").unlink()
    assert initialize_user(root) == ["configs.toml"]
    assert (root / "user/seed_prompt.md").read_bytes() == before["seed_prompt.md"]


@pytest.mark.parametrize("raw", [b"", b" \n\t", b"\xef\xbb\xbf  ", b"\xff", b"x" * 120001])
def test_seed_rejections(root, raw):
    (root / "user/seed_prompt.md").write_bytes(raw)
    with pytest.raises(AppError):
        read_seed(root)


def test_missing_seed(root):
    (root / "user/seed_prompt.md").unlink()
    with pytest.raises(AppError, match="Falta"):
        read_seed(root)


def test_utf8_bom(root):
    (root / "user/seed_prompt.md").write_bytes(b"\xef\xbb\xbfHello\r\n")
    assert read_seed(root) == "Hello"


def test_atomic_failure_preserves_output(root, monkeypatch):
    def fail(*args):
        raise PermissionError("test")

    monkeypatch.setattr(os, "replace", fail)
    with pytest.raises(PermissionError):
        atomic_output(root, "new")
    assert (root / "user/optimized_prompt.md").read_text() == "resultado anterior"
    assert list((root / "user").glob("*.tmp")) == []


def test_lock_prevents_concurrent_runs_and_cleans_up(root):
    with pytest.raises(RuntimeError), run_lock(root):
        with pytest.raises(AppError, match="lock"):
            with run_lock(root):
                pass
        raise RuntimeError("failure")
    assert not (root / "user/.run.lock").exists()
