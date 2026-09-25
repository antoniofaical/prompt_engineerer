from contextlib import contextmanager

import pytest

from prompt_engineerer.files import initialize_user


class FakeUI:
    def __init__(self, answers=()):
        self.answers = iter(answers)
        self.messages = []

    def say(self, text):
        self.messages.append(text)

    @contextmanager
    def stage(self, name):
        self.messages.append(name)
        yield

    def ask(self, question):
        self.messages.append(question)
        return next(self.answers)


class FakeProvider:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def call(self, stage, payload, schema):
        # Record a snapshot, not a reference later mutated by the orchestrator.
        import copy

        self.calls.append((stage, copy.deepcopy(payload), schema))
        response = next(self.responses)
        if isinstance(response, Exception):
            raise response
        return schema.model_validate(response)


@pytest.fixture
def root(tmp_path):
    initialize_user(tmp_path)
    (tmp_path / "user/seed_prompt.md").write_text(
        "Crie instruções para resumir um artigo, preservando limitações e fontes.", encoding="utf-8"
    )
    (tmp_path / "user/optimized_prompt.md").write_text("resultado anterior", encoding="utf-8")
    return tmp_path


@pytest.fixture
def ui():
    return FakeUI()


@pytest.fixture
def analysis():
    return {
        "objective": "Resumir artigo",
        "requirements": ["Preservar limitações"],
        "missing_information": [],
        "questions": [],
        "blocking_conflicts": [],
    }
