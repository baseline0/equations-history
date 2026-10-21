# equations-history: Task automation

import 'just/repo-push.just'

import 'just/fleet-clean.just'
import 'just/fleet-checks.just'
import 'just/fleet-commit.just'

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
    uv run --extra dev mypy src/ --strict
    uv run ruff check src/ tests/

# Pyright ratchet: fails if any file has more errors than pyright-baseline.json records
@check-types:
    fleet ratchet --action check

@serve:
    uv run uvicorn equations_history.api:app --reload --host 0.0.0.0 --port 8000

@cli *ARGS:
    uv run learn {{ARGS}}

@help:
    uv run learn --help

# Unit tests: the gate the pre-push hook runs (fleet hook standard, fleet_base.hook_standard R4)
test-unit:
    just test
