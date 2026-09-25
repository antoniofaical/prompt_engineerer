"""Exercise pytest's environment bookkeeping under the Windows size limit."""

import os
import subprocess
import sys
import textwrap

from prompt_engineerer.files import project_root


def test_large_seed_case_runs_under_windows_environment_limit():
    # Use a separate process so the guard cannot affect the parent test runner.
    # Running the real tests (rather than just checking IDs) covers setup/teardown.
    script = textwrap.dedent(
        """
        import os
        import pytest

        original = type(os.environ).__setitem__
        lengths = []

        def guarded(self, key, value):
            if key == "PYTEST_CURRENT_TEST":
                length = len(value.encode("utf-16-le")) // 2
                lengths.append(length)
                if length > 32767:
                    raise ValueError("the environment variable is longer than 32767 characters")
            return original(self, key, value)

        type(os.environ).__setitem__ = guarded
        try:
            code = pytest.main([
                "src/prompt_engineerer/tests/test_config_files.py::test_seed_rejections",
                "-q", "--tb=short", "-o", "addopts=",
            ])
        finally:
            type(os.environ).__setitem__ = original
        assert lengths, "The environment guard was not exercised"
        assert max(lengths) < 512, "Test IDs must stay concise, not contain payloads"
        raise SystemExit(code)
        """
    )
    environment = os.environ.copy()
    environment.pop("PYTEST_ADDOPTS", None)
    environment["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=project_root(),
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, (result.stdout + result.stderr)[-3000:]
    assert "5 passed" in result.stdout
