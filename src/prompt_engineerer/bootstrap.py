"""Preflight multiplataforma; somente stdlib, executável antes de instalar o pacote."""

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path


class BootstrapError(Exception):
    pass


def say(text):
    print(text, flush=True)


def run(command, root, label, timeout=600, accepted=(0,)):
    say(f"[ETAPA] {label}")
    started = time.monotonic()
    process = subprocess.Popen(command, cwd=root)
    try:
        while True:
            try:
                code = process.wait(timeout=10)
                break
            except subprocess.TimeoutExpired:
                elapsed = int(time.monotonic() - started)
                say(f"[ATIVIDADE] {label}: {elapsed}s decorridos...")
                if elapsed >= timeout:
                    raise BootstrapError(f"Tempo limite em: {label}.") from None
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
    if code not in accepted:
        raise BootstrapError(f"{label} falhou (código {code}). Veja a saída acima.")
    say(f"[{'OK' if code == 0 else 'PENDENTE'}] {label}")
    return code


def git(root, *args):
    try:
        result = subprocess.run(
            ["git", *args], cwd=root, text=True, capture_output=True, timeout=20, check=False
        )
    except subprocess.TimeoutExpired as exc:
        raise BootstrapError("Git não respondeu em 20s.") from exc
    if result.returncode:
        raise BootstrapError("Não foi possível consultar o estado do Git.")
    return result.stdout.strip()


def update_repository(root):
    if not shutil.which("git"):
        raise BootstrapError("Instale Git antes de executar o bootstrap.")
    if not (root / ".git").exists():
        say("[AVISO] Sem checkout Git: atualização indisponível; preparando os arquivos locais.")
        return
    say("[ETAPA] Verificar atualização segura do repositório")
    if git(root, "status", "--porcelain"):
        say("[AVISO] Alterações locais detectadas. Atualização pulada; nenhum arquivo descartado.")
        return
    branch = git(root, "branch", "--show-current")
    if not branch:
        say("[AVISO] HEAD destacado. Atualização pulada.")
        return
    try:
        remote = git(root, "config", f"branch.{branch}.remote")
        remote_ref = git(root, "config", f"branch.{branch}.merge")
    except BootstrapError:
        say("[AVISO] Branch sem upstream. Atualização pulada; configure o tracking no Git.")
        return
    if remote == "." or not remote_ref.startswith("refs/heads/"):
        say("[AVISO] Upstream não remoto/padrão. Atualização pulada.")
        return
    try:
        run(["git", "fetch", remote, remote_ref], root, "Buscar atualizações", timeout=120)
    except BootstrapError:
        say("[AVISO] Fetch falhou. Continuando com a versão local; confira rede/autenticação.")
        return
    ahead, behind = map(
        int, git(root, "rev-list", "--left-right", "--count", "HEAD...FETCH_HEAD").split()
    )
    if ahead:
        say("[AVISO] Commits locais presentes. Atualização pulada; resolva o Git manualmente.")
    elif behind:
        run(["git", "merge", "--ff-only", "FETCH_HEAD"], root, "Aplicar avanço direto", timeout=60)
    else:
        say("[OK] Repositório atualizado.")


def prepare_environment(root):
    venv_dir = root / ".venv"
    python = venv_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    if not venv_dir.exists():
        run([sys.executable, "-m", "venv", str(venv_dir)], root, "Criar ambiente virtual")
    if not python.is_file():
        raise BootstrapError(".venv incompleto. Renomeie esse diretório e execute novamente.")
    run(
        [
            str(python),
            "-c",
            "import sys; assert sys.version_info >= (3,11); "
            "assert sys.prefix != sys.base_prefix; import pip",
        ],
        root,
        "Verificar Python e pip do venv",
    )
    run(
        [str(python), "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"],
        root,
        "Atualizar ferramentas de instalação",
    )
    run(
        [str(python), "-m", "pip", "install", "--upgrade", "-e", ".[dev]"],
        root,
        "Instalar/atualizar dependências compatíveis",
    )
    run([str(python), "-m", "pip", "check"], root, "Verificar dependências")
    run([str(python), "-m", "ruff", "check", "src"], root, "Ruff: análise estática")
    run([str(python), "-m", "ruff", "format", "--check", "src"], root, "Ruff: formatação")
    run([str(python), "-m", "pytest"], root, "Testes automatizados")
    code = run(
        [str(python), "-m", "prompt_engineerer", "--init", "--check"],
        root,
        "Arquivos locais e configuração",
        accepted=(0, 2),
    )
    say("[CONCLUÍDO] Ambiente virtual instalado e verificações de código aprovadas.")
    if code == 2:
        say("[PENDENTE] Complete o seed/configuração/credencial indicados acima antes de gerar.")
    if os.name == "nt":
        say(f"Ative no PowerShell: & '{venv_dir / 'Scripts/Activate.ps1'}'")
    else:
        import shlex

        say(f"Ative no shell: source {shlex.quote(str(venv_dir / 'bin/activate'))}")
    say("Depois execute: prompt-engineerer")
    return code


def main(argv=None):
    parser = argparse.ArgumentParser(description="Preflight sem chamadas pagas à API.")
    parser.add_argument(
        "--skip-update", action="store_true", help="Use o checkout local sem fetch."
    )
    parser.add_argument("--after-update", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[2]
    try:
        if sys.version_info < (3, 11):  # noqa: UP036 - runs before package installation
            raise BootstrapError("Python 3.11+ é necessário.")
        if not args.after_update:
            if args.skip_update:
                say("[AVISO] Atualização Git desativada explicitamente (--skip-update).")
            else:
                update_repository(root)
            # Start the current on-disk version after a possible Git update.
            return subprocess.call(
                [sys.executable, str(Path(__file__).resolve()), "--after-update"], cwd=root
            )
        return prepare_environment(root)
    except (BootstrapError, OSError) as exc:
        say(f"[ERRO] {exc}")
        return 1
    except KeyboardInterrupt:
        say("\n[CANCELADO] Bootstrap interrompido.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
