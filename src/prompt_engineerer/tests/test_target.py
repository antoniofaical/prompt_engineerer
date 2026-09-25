import pytest
from conftest import FakeUI

from prompt_engineerer.config import TargetAI
from prompt_engineerer.errors import AppError
from prompt_engineerer.target import inspect_target, resolve_target


@pytest.mark.parametrize(
    ("provider", "model", "expected"),
    [
        ("", "", ""),
        ("ChatGPT", "", "openai"),
        ("Claude", "", "anthropic"),
        ("", "gpt-5-mini", "openai"),
        ("", "claude-sonnet-4-5", "anthropic"),
        ("", "gemini-2.5-pro", "google"),
    ],
)
def test_resolution(provider, model, expected):
    result, warning = inspect_target(TargetAI(provider=provider, model=model))
    assert result.provider == expected
    assert warning is None


def test_contradiction():
    with pytest.raises(AppError, match="diferentes"):
        inspect_target(TargetAI(provider="openai", model="claude-sonnet-4-5"))


def test_unknown_model_can_continue_general():
    ui = FakeUI(["g"])
    assert resolve_target(TargetAI(model="new-model"), True, ui) == TargetAI()
    assert any("ambíguo" in m for m in ui.messages)


def test_unknown_no_questions(ui):
    assert resolve_target(TargetAI(model="new-model"), False, ui) == TargetAI()


def test_unknown_can_stop():
    with pytest.raises(AppError, match="Ajuste"):
        resolve_target(TargetAI(model="new-model"), True, FakeUI([""]))
