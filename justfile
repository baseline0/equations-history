# equations-history: Task automation

import 'just/repo-push.just'

import 'just/fleet-clean.just'
import 'just/fleet-checks.just'
import 'just/fleet-commit.just'
import 'just/fleet-test.just'

set shell := ["bash", "-c"]

@default:
    just --list

@sync:
    uv sync --frozen

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

# Refresh a formula catalog snapshot from math-trace, and pin the manifest to the math-trace commit. src is the catalog
# path inside math-trace; empty means the template layout, templates/<name>/equations.json. Refuses while that file has
# uncommitted changes, so the snapshot always matches a commit.
sync-catalog name src="" mt="../math-trace":
    #!/usr/bin/env bash
    set -euo pipefail
    src="{{src}}"
    if [ -z "$src" ]; then src="templates/{{name}}/equations.json"; fi
    if ! git -C "{{mt}}" diff --quiet HEAD -- "$src"; then
        echo "refusing: {{mt}} has uncommitted changes in $src" >&2
        exit 1
    fi
    dst="src/equations_history/catalogs/{{name}}.json"
    cp "{{mt}}/$src" "$dst"
    commit=$(git -C "{{mt}}" rev-parse --short HEAD)
    sha=$(sha256sum "$dst" | cut -d' ' -f1)
    printf '{\n  "source": "math-trace %s",\n  "source_commit": "%s",\n  "sha256": "%s"\n}\n' \
        "$src" "$commit" "$sha" > "src/equations_history/catalogs/{{name}}.manifest.json"
    echo "synced {{name}} from math-trace $src at $commit"

# Write the public view of the pilot formula records to dist/public-records (gitignored), for the tool-publish preview.
# Only records grounded in math-trace belong here, so the Navier-Stokes example is left out.
records-public:
    mkdir -p dist/public-records
    uv run learn record public --path tests/fixtures/formula_record/michaelis-menten.json --paper-store tests/fixtures/paper_store --out dist/public-records/michaelis-menten.json
