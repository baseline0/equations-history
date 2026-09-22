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

@commit:
    git status
    #!/usr/bin/env bash
    set -e
    read -p "Commit message (or press Enter for auto-generate): " msg
    if [ -z "$msg" ]; then
        # Try commitmate for auto-generate, fall back to manual
        if command -v commitmate &> /dev/null && which ollama &> /dev/null; then
            msg=$(timeout 30 commitmate --format || echo "")
        fi
        if [ -z "$msg" ]; then
            read -p "Enter commit message: " msg
        fi
    fi
    git commit -m "$msg" || true

@clean:
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
    rm -rf .ruff_cache/

@help:
    uv run learn --help
