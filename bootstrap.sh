#!/usr/bin/env bash
set -euo pipefail
TASK_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
for TASK_PYTHON in python3 python; do
    if command -v "$TASK_PYTHON" >/dev/null 2>&1 && "$TASK_PYTHON" -c 'import sys; sys.exit(sys.version_info < (3, 11))' 2>/dev/null; then
        exec "$TASK_PYTHON" "$TASK_ROOT/src/prompt_engineerer/bootstrap.py" "$@"
    fi
done
echo '[ERRO] Instale Python 3.11 ou superior (com venv/pip) e tente novamente.' >&2
exit 1
