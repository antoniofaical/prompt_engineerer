import pytest
from conftest import FakeProvider, FakeUI

from prompt_engineerer.config import TargetAI, UserConfig
from prompt_engineerer.errors import AppError
from prompt_engineerer.pipeline import optimize

SELECT = {"guideline_ids": ["clear_deliverable"], "rationale": "Entrega explícita."}
PASS = {"passed": True, "issues": []}
FAIL = {"passed": False, "issues": [{"severity": "blocking", "description": "Falta restrição"}]}


def test_success_writes_only_markdown_preserves_inputs(root, analysis, ui):
    seed = (root / "user/seed_prompt.md").read_bytes()
    config = (root / "user/configs.toml").read_bytes()
    provider = FakeProvider([analysis, SELECT, {"markdown": "# Pedido\nResuma o artigo."}, PASS])
    optimize(root, UserConfig(), provider, ui)
    assert (root / "user/optimized_prompt.md").read_text() == "# Pedido\nResuma o artigo.\n"
    assert (root / "user/seed_prompt.md").read_bytes() == seed
    assert (root / "user/configs.toml").read_bytes() == config
    assert "api_key_env_var" not in str(provider.calls)
    rules = provider.calls[2][1]["guidelines"]
    assert any(r["id"] == "preserve_intent" for r in rules)


def test_revision_cycle(root, analysis, ui):
    provider = FakeProvider(
        [analysis, SELECT, {"markdown": "bad"}, FAIL, {"markdown": "corrected"}, PASS]
    )
    optimize(root, UserConfig(max_revision_rounds=1), provider, ui)
    assert (root / "user/optimized_prompt.md").read_text() == "corrected\n"
    assert provider.calls[4][0] == "Corrigir prompt"


@pytest.mark.parametrize("review", [FAIL, {"passed": True, "issues": FAIL["issues"]}])
def test_review_limit_preserves_previous(root, analysis, ui, review):
    provider = FakeProvider([analysis, SELECT, {"markdown": "bad"}, review])
    with pytest.raises(AppError, match="Limite"):
        optimize(root, UserConfig(max_revision_rounds=0), provider, ui)
    assert (root / "user/optimized_prompt.md").read_text() == "resultado anterior"
    assert len(provider.calls) == 4


def test_api_failure_preserves_output_and_removes_lock(root, analysis, ui):
    provider = FakeProvider([analysis, AppError("offline")])
    with pytest.raises(AppError, match="offline"):
        optimize(root, UserConfig(), provider, ui)
    assert (root / "user/optimized_prompt.md").read_text() == "resultado anterior"
    assert not (root / "user/.run.lock").exists()


def test_clarification_then_reanalysis(root, analysis):
    pending = {
        **analysis,
        "questions": [{"text": "Público?", "reason": "Ajustar nível", "blocking": False}],
    }
    provider = FakeProvider([pending, analysis, SELECT, {"markdown": "Para estudantes"}, PASS])
    optimize(root, UserConfig(max_clarification_rounds=1), provider, FakeUI(["Estudantes"]))
    assert provider.calls[1][1]["answers"][0]["answer"] == "Estudantes"


@pytest.mark.parametrize("answer", ["", "/fim"])
def test_stop_optional_questions(root, analysis, answer):
    pending = {
        **analysis,
        "questions": [{"text": "Público?", "reason": "Nível", "blocking": False}],
    }
    provider = FakeProvider([pending, SELECT, {"markdown": "Peça o público se necessário"}, PASS])
    optimize(root, UserConfig(), provider, FakeUI([answer]))
    assert len(provider.calls) == 4


def test_disabled_questions_still_blocks_contradictions(root, analysis, ui):
    analysis["blocking_conflicts"] = ["Sem ferramentas, mas exige navegação"]
    provider = FakeProvider([analysis])
    with pytest.raises(AppError, match="contradições"):
        optimize(root, UserConfig(max_clarification_rounds=0), provider, ui)


def test_unknown_guideline_is_rejected(root, analysis, ui):
    provider = FakeProvider([analysis, {"guideline_ids": ["invented"], "rationale": "test"}])
    with pytest.raises(AppError, match="IDs"):
        optimize(root, UserConfig(), provider, ui)


def test_provider_specific_guidelines_filtered(root, analysis, ui):
    provider = FakeProvider([analysis, SELECT, {"markdown": "pedido"}, PASS])
    optimize(root, UserConfig(target_ai=TargetAI(provider="anthropic")), provider, ui)
    ids = {r["id"] for r in provider.calls[1][1]["catalog"]}
    assert "claude_delimiters" in ids
    assert "openai_role" not in ids
