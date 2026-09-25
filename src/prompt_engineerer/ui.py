from contextlib import contextmanager
from threading import Event, Thread

from rich.console import Console

from .errors import AppError


class UI:
    def __init__(self):
        self.console = Console(markup=False, highlight=False)

    def say(self, message: str):
        self.console.print(message)

    @contextmanager
    def stage(self, name: str):
        self.say(f"[ETAPA] {name}")
        if self.console.is_terminal:
            with self.console.status(f"{name} — aguardando…", spinner="dots"):
                yield
        else:
            done = Event()

            def heartbeat():
                while not done.wait(15):
                    self.say(f"[ATIVIDADE] {name} — aguardando resposta…")

            thread = Thread(target=heartbeat, daemon=True)
            thread.start()
            try:
                yield
            finally:
                done.set()
                thread.join()
        self.say(f"[OK] {name}")

    def ask(self, question: str) -> str:
        self.say(question)
        try:
            return input("> ").strip()
        except EOFError as exc:
            raise AppError(
                "Entrada interativa indisponível. Configure max_clarification_rounds = 0 "
                "ou execute em um terminal interativo."
            ) from exc
