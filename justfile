# equations-history: Task automation

set shell := ["bash", "-c"]

@default:
    just --list

@sync:
    uv sync

@test:
    uv run pytest tests/ -xvs

@fmt:
    uv run ruff format src/ tests/
    uv run ruff check src/ tests/ --fix

@check:
    uv run mypy src/ --strict
    uv run ruff check src/ tests/

@serve:
    uv run uvicorn equations_history.api:app --reload --host 0.0.0.0 --port 8000

@cli *ARGS:
    uv run learn {{ARGS}}

# Commit staged changes. MESSAGE="..." just commit uses that message; without it, commitmate drafts one if
# available, and otherwise you are asked. Nothing is committed when nothing is staged.
@commit:
    #!/usr/bin/env bash
    set -euo pipefail
    if [ -z "$(git diff --cached --name-only)" ]; then
        echo "[!] No staged changes. Stage files first: git add <files>"
        exit 1
    fi
    msg="${MESSAGE:-}"
    if [ -z "$msg" ] && command -v commitmate &> /dev/null && command -v ollama &> /dev/null; then
        msg=$(timeout 30 commitmate --format || echo "")
    fi
    if [ -z "$msg" ]; then
        read -r -p "Commit message: " msg
    fi
    if [ -z "$msg" ]; then
        echo "[!] Empty message; nothing committed."
        exit 1
    fi
    git commit -m "$msg"

@clean:
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
    rm -rf .ruff_cache/

@help:
    uv run learn --help
