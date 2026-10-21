"""Citation graph ingest: contract validation, edge direction, and neighbourhoods. Offline."""

import json
from pathlib import Path

import pytest

from equations_history.citations import GraphError, load_graph

pytestmark = pytest.mark.unit

A, B, C = "2401.00001v1", "2402.00002v1", "2403.00003v1"


def _write(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "graph.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_an_edge_is_read_as_citing_then_cited(tmp_path: Path) -> None:
    graph = load_graph(
        _write(
            tmp_path,
            {
                "nodes": [A, B],
                "edges": [[A, B]],
                "sources": {"openalex": 1, "text_arxiv_ids": 0, "bibliography_titles": 0},
            },
        )
    )

    assert graph.cites(A) == (B,)
    assert graph.cited_by(B) == (A,)
    assert graph.cites(B) == ()


def test_a_paper_outside_the_graph_has_no_neighbours(tmp_path: Path) -> None:
    graph = load_graph(
        _write(
            tmp_path,
            {"nodes": [A], "edges": [], "sources": {"openalex": 0, "text_arxiv_ids": 0, "bibliography_titles": 0}},
        )
    )

    assert graph.cites(C) == () and graph.cited_by(C) == ()


def test_a_file_missing_a_required_source_count_is_refused(tmp_path: Path) -> None:
    with pytest.raises(GraphError, match="does not match the contract"):
        load_graph(_write(tmp_path, {"nodes": [A], "edges": [], "sources": {"openalex": 0}}))


def test_a_malformed_arxiv_id_is_refused(tmp_path: Path) -> None:
    with pytest.raises(GraphError, match="does not match the contract"):
        load_graph(
            _write(
                tmp_path,
                {
                    "nodes": ["not-an-id"],
                    "edges": [],
                    "sources": {"openalex": 0, "text_arxiv_ids": 0, "bibliography_titles": 0},
                },
            )
        )


def test_an_edge_naming_a_non_node_is_refused(tmp_path: Path) -> None:
    with pytest.raises(GraphError, match="not nodes"):
        load_graph(
            _write(
                tmp_path,
                {
                    "nodes": [A],
                    "edges": [[A, B]],
                    "sources": {"openalex": 1, "text_arxiv_ids": 0, "bibliography_titles": 0},
                },
            )
        )
