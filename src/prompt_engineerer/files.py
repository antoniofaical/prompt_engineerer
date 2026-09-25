import os
import tempfile
from contextlib import contextmanager
from pathlib import Path

from .errors import AppError
from .technical import MAX_SEED_BYTES

RESOURCES = Path(__file__).resolve().parent / "resources"


def project_root() -> Path:
    root = Path(__file__).resolve().parents[2]
    if not (root / "pyproject.toml").is_file() or not (root / "bootstrap.sh").is_file():
        raise AppError("Use a instalação editável no clone do projeto: execute o bootstrap.")
    return root


def initialize_user(root: Path) -> list[str]:
    folder = root / "user"
    folder.mkdir(exist_ok=True)
    created = []
    for name in ("seed_prompt.md", "optimized_prompt.md", "configs.toml"):
        try:
            with (folder / name).open("x", encoding="utf-8", newline="\n") as file:
                file.write((RESOURCES / "templates" / name).read_text(encoding="utf-8"))
            created.append(name)
        except FileExistsError:
            pass
    return created


def read_seed(root: Path) -> str:
    path = root / "user/seed_prompt.md"
    try:
        with path.open("rb") as file:
            raw = file.read(MAX_SEED_BYTES + 1)
    except FileNotFoundError as exc:
        raise AppError(
            "Falta user/seed_prompt.md. Execute o bootstrap e escreva sua demanda."
        ) from exc
    if len(raw) > MAX_SEED_BYTES:
        raise AppError(f"Seed excede {MAX_SEED_BYTES} bytes. Reduza o contexto relevante.")
    try:
        seed = raw.decode("utf-8-sig").strip()
    except UnicodeError as exc:
        raise AppError("Salve user/seed_prompt.md com codificação UTF-8.") from exc
    if not seed:
        raise AppError("user/seed_prompt.md está vazio. Escreva sua demanda antes de executar.")
    return seed


@contextmanager
def run_lock(root: Path):
    path = root / "user/.run.lock"
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise AppError(
            "Já existe user/.run.lock. Aguarde a outra execução. Se ela foi encerrada "
            "à força, remova o lock somente após confirmar que não há execução ativa."
        ) from exc
    try:
        os.close(fd)
        yield
    finally:
        path.unlink(missing_ok=True)


def atomic_output(root: Path, markdown: str) -> None:
    if not markdown.strip():
        raise AppError("A geração retornou conteúdo vazio; o arquivo anterior foi preservado.")
    folder = root / "user"
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=folder, suffix=".tmp", delete=False
        ) as file:
            temp_path = Path(file.name)
            file.write(markdown.strip() + "\n")
            file.flush()
            os.fsync(file.fileno())
        os.replace(temp_path, folder / "optimized_prompt.md")
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)
