from contextlib import contextmanager
from threading import Event, Thread

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .errors import AppError


class UI:
    def __init__(self):
        self.console = Console(markup=False, highlight=False)

    def say(self, message: str):
        text = Text(message)
        if message.startswith("[") and "]" in message:
            label = message[: message.index("]") + 1]
            style = {
                "[ETAPA]": "bold blue",
                "[OK]": "green",
                "[ATIVIDADE]": "dim",
                "[PERGUNTAS]": "bold cyan",
            }.get(label, "bold")
            text.stylize(style, 0, len(label))
        self.console.print(text)

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

    def ask(self, question: str, *, reason: str = "", title: str = "Pergunta") -> str:
        body = Text(question, style="bold")
        if reason:
            body.append("\n\nMotivo: " + reason, style="not bold dim")
        self.console.print()
        self.console.print(
            Panel(body, title=Text(title), title_align="left", border_style="cyan", padding=(1, 2))
        )
        self.console.print(Text("Sua resposta: ", style="bold green"), end="")
        try:
            return input().strip()
        except EOFError as exc:
            raise AppError(
                "Entrada interativa indisponível. Configure max_clarification_rounds = 0 "
                "ou execute em um terminal interativo."
            ) from exc
        finally:
            self.console.print()
