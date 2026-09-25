import subprocess

import pytest

from prompt_engineerer.bootstrap import BootstrapError, run, update_repository


def git_at(path, *args):
    return subprocess.run(
        ["git", *args], cwd=path, check=True, capture_output=True, text=True
    ).stdout.strip()


@pytest.fixture
def checkout(tmp_path):
    remote = tmp_path / "remote.git"
    source = tmp_path / "source"
    local = tmp_path / "local"
    git_at(tmp_path, "init", "--bare", str(remote))
    git_at(tmp_path, "init", "-b", "main", str(source))
    git_at(source, "config", "user.name", "Test")
    git_at(source, "config", "user.email", "test@example.invalid")
    (source / ".gitignore").write_text("/user/\n", encoding="utf-8")
    (source / "README.md").write_text("v1", encoding="utf-8")
    git_at(source, "add", ".")
    git_at(source, "commit", "-m", "initial")
    git_at(source, "remote", "add", "origin", str(remote))
    git_at(source, "push", "-u", "origin", "main")
    git_at(tmp_path, "clone", "--branch", "main", str(remote), str(local))
    (local / "user").mkdir()
    for name in ("seed_prompt.md", "optimized_prompt.md", "configs.toml"):
        (local / "user" / name).write_text("private-local-data", encoding="utf-8")
    (source / "README.md").write_text("v2", encoding="utf-8")
    git_at(source, "commit", "-am", "update")
    git_at(source, "push")
    return local


def test_fast_forward_preserves_user_files(checkout):
    update_repository(checkout)
    assert (checkout / "README.md").read_text() == "v2"
    for file in (checkout / "user").iterdir():
        assert file.read_text() == "private-local-data"


def test_dirty_worktree_not_overwritten(checkout):
    (checkout / "README.md").write_text("local-change", encoding="utf-8")
    before = git_at(checkout, "rev-parse", "HEAD")
    update_repository(checkout)
    assert git_at(checkout, "rev-parse", "HEAD") == before
    assert (checkout / "README.md").read_text() == "local-change"


def test_divergence_does_not_merge(checkout):
    git_at(checkout, "config", "user.name", "Test")
    git_at(checkout, "config", "user.email", "test@example.invalid")
    (checkout / "local.txt").write_text("local", encoding="utf-8")
    git_at(checkout, "add", "local.txt")
    git_at(checkout, "commit", "-m", "local")
    before = git_at(checkout, "rev-parse", "HEAD")
    update_repository(checkout)
    assert git_at(checkout, "rev-parse", "HEAD") == before
    assert (checkout / "README.md").read_text() == "v1"


def test_preflight_subprocess_failure_stops(tmp_path):
    import sys

    with pytest.raises(BootstrapError, match="código 7"):
        run([sys.executable, "-c", "raise SystemExit(7)"], tmp_path, "fixture")


def test_preflight_pending_code(tmp_path):
    import sys

    assert (
        run([sys.executable, "-c", "raise SystemExit(2)"], tmp_path, "fixture", accepted=(0, 2))
        == 2
    )
