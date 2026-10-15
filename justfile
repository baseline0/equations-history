# equations-history: Task automation

import 'just/repo-push.just'

import 'just/fleet-clean.just'

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

# Pyright ratchet: fails if any file has more errors than pyright-baseline.json records
@check-types:
    fleet ratchet --action check

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

@help:
    uv run learn --help

# Unit tests: the gate the pre-push hook runs (fleet hook standard, fleet_base.hook_standard R4)
test-unit:
    just test
