"""The formula-pages publish workflow is started by hand, waits for production approval, and refuses a preview build.

Read as text, so the test needs no YAML parser that this repo does not depend on."""

from equations_history.constants import REPO_ROOT

WORKFLOW = REPO_ROOT / ".github" / "workflows" / "pages-formulas.yml"


def _text() -> str:
    return WORKFLOW.read_text(encoding="utf-8")


def test_the_publish_is_started_by_hand_only() -> None:
    text = _text()
    assert "workflow_dispatch:" in text
    assert "push:" not in text and "pull_request:" not in text and "schedule:" not in text


def test_the_publish_job_waits_for_the_production_environment() -> None:
    assert "environment:\n      name: production" in _text()


def test_the_workflow_refuses_a_preview_build() -> None:
    text = _text()
    assert "pages/BUILD.json" in text
    assert "['preview'] is False" in text
