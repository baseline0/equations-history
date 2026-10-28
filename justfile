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

# Assemble the grounded biochemistry records from the math-trace snapshot, then write their public views straight into
# formula-records/, the reviewed set. A changed record voids its review, so a deployable build refuses until someone
# reviews it again (just pages-approve). Only records grounded in math-trace belong here, so the Navier-Stokes example is
# left out. Each formula is listed as key:id.
records-public:
    #!/usr/bin/env bash
    set -euo pipefail
    mkdir -p dist/records formula-records
    for pair in michaelis_menten:michaelis-menten specificity:specificity; do
        formula="${pair%%:*}"
        id="${pair##*:}"
        uv run learn record assemble --catalog src/equations_history/catalogs/biochemistry.json \
            --narrative src/equations_history/narratives/biochemistry.json --formula "$formula" --id "$id" \
            --source-file templates/biochemistry/src/model.py --paper-store tests/fixtures/paper_store \
            --out "dist/records/$id.json"
        uv run learn record public --path "dist/records/$id.json" --paper-store tests/fixtures/paper_store \
            --out "formula-records/$id.json"
    done

# Check pages/ is ready to publish before you push: a deployable build, every record has its page, and nothing is left
# uncommitted. Read only. It does not push, deploy, or change Pages settings.
publish-check:
    #!/usr/bin/env bash
    set -euo pipefail
    test -f pages/BUILD.json || { echo "FAIL pages/BUILD.json is missing; run just pages-build"; exit 1; }
    python3 - <<'PY'
    import json, sys
    from pathlib import Path
    build = json.loads(Path("pages/BUILD.json").read_text(encoding="utf-8"))
    if build["preview"] is not False:
        sys.exit("FAIL pages/ is a preview build, not deployable")
    missing = [r for r in build["records"] if not Path("pages", r, "index.html").is_file()]
    if missing:
        sys.exit(f"FAIL no page for {missing}")
    print(f"OK deployable build with {len(build['records'])} record(s): {', '.join(build['records'])}")
    PY
    if [ -n "$(git status --porcelain -- pages)" ]; then
        echo "FAIL pages/ has uncommitted changes; commit them before pushing"; exit 1
    fi
    echo "OK pages/ is committed. Next: push, set Pages source to GitHub Actions, then start the workflow."

# Build the formula pages from the reviewed records in formula-records/. Deployable (the default) only when every record
# has a current review; a preview is marked and must never be published. Writes pages/ by default.
[group("pages")]
pages-build mode="deployable" out="pages":
    uv run python scripts/formula_pages_cli.py build --mode "{{mode}}" --out "{{out}}"

# Record that a person reviewed one record. The review is pinned to the record's bytes, so an edit voids it.
[group("pages")]
pages-approve id reviewer:
    uv run python scripts/formula_pages_cli.py approve --id "{{id}}" --reviewer "{{reviewer}}"

# Approve every record in formula-records/. Read the change first (git diff -- formula-records): this is a review, not a stamp.
[group("pages")]
pages-approve-all reviewer:
    git diff --stat -- formula-records
    uv run python scripts/formula_pages_cli.py approve-all --reviewer "{{reviewer}}"
