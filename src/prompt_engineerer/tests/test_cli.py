import json

from prompt_engineerer import cli
from prompt_engineerer.files import RESOURCES
from prompt_engineerer.pipeline import load_catalog


def test_check_without_key_or_seed_aggregates_pending(root, monkeypatch, capsys):
    monkeypatch.setattr(cli, "project_root", lambda: root)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    (root / "user/seed_prompt.md").write_text("", encoding="utf-8")
    assert cli.main(["--check"]) == 2
    output = capsys.readouterr().out
    assert "vazio" in output and "OPENAI_API_KEY" in output


def test_check_never_calls_api(root, monkeypatch):
    monkeypatch.setattr(cli, "project_root", lambda: root)
    monkeypatch.setenv("OPENAI_API_KEY", "fake-test-key")

    def forbidden(*args, **kwargs):
        raise AssertionError("No API allowed")

    monkeypatch.setattr(cli, "OpenAIProvider", forbidden)
    assert cli.main(["--check"]) == 0


def test_preflight_from_other_directory(root, monkeypatch):
    from prompt_engineerer.files import project_root

    monkeypatch.chdir(root)
    actual = project_root()
    assert (actual / "pyproject.toml").is_file()
    assert actual != root


def test_catalog_sources_and_eval_fixtures():
    sources = (RESOURCES / "sources.md").read_text(encoding="utf-8")
    for rule in load_catalog():
        assert rule["source"] in sources
        assert rule["when"] and rule["exceptions"]
    cases = json.loads((RESOURCES / "evaluation-cases.json").read_text(encoding="utf-8"))
    assert len(cases) >= 5
