"""The equations-history MCP server: read-only tools and resources that reply with the fleet read envelope."""

import asyncio
import json
from typing import Any, cast

import pytest

from equations_history.mcp_server import (
    CONTRACT,
    VERSION,
    build_server,
    get_equation,
    get_narrative_chunk,
    get_record_bundle,
    get_record_crosswalk,
    list_equations,
    list_topics,
)

pytestmark = pytest.mark.unit

EXPECTED_TOOLS = {
    "list_topics",
    "list_equations",
    "get_equation",
    "list_formula_records",
    "get_formula_record",
    "get_record_bundle",
    "get_record_crosswalk",
    "get_narrative_chunk",
    "get_catalog_manifest",
}
EXPECTED_RESOURCES = {"equations://topics", "records://index", "records://reviews"}
EXPECTED_TEMPLATES = {
    "equations://equation/{topic}/{name}",
    "records://formula/{record_id}/bundle",
    "records://formula/{record_id}/crosswalk",
    "records://formula/{record_id}/narrative",
    "records://manifest/{catalog}",
}


def test_every_reply_is_the_fleet_read_envelope():
    for reply in (
        list_topics(),
        list_equations("autoencoders"),
        get_equation("autoencoders", "deterministic_encoder"),
        get_record_bundle("michaelis-menten"),
        get_record_crosswalk("michaelis-menten"),
        get_narrative_chunk("michaelis-menten"),
    ):
        assert reply["contract"] == CONTRACT
        assert reply["version"] == VERSION
        assert reply["source"] == "equations-history"
        assert ("data" in reply) != ("error" in reply)


def test_list_topics_names_the_registered_topics():
    topics = list_topics()["data"]["topics"]

    assert "autoencoders" in topics
    assert len(topics) == len(set(topics)) and len(topics) > 1


def test_list_equations_gives_names_and_descriptions():
    data = list_equations("autoencoders")["data"]

    assert data["topic"] == "autoencoders"
    assert data["equations"]
    assert {"name", "title", "description"} <= set(data["equations"][0])


def test_get_equation_gives_the_full_record():
    data = get_equation("autoencoders", "deterministic_encoder")["data"]

    assert {"latex", "description", "history", "citations", "concepts"} <= set(data)
    assert isinstance(data["citations"], list)


def test_unknown_topic_and_equation_are_envelope_errors_not_tracebacks():
    unknown_topic = list_equations("no-such-topic")
    unknown_equation = get_equation("autoencoders", "no-such-equation")

    assert "error" in unknown_topic and "data" not in unknown_topic
    assert "error" in unknown_equation and "data" not in unknown_equation


def test_the_server_offers_read_only_tools_and_resources():
    server = build_server()
    listed = asyncio.run(server.list_tools())
    resources = asyncio.run(server.list_resources())
    templates = asyncio.run(server.list_resource_templates())

    assert {tool.name for tool in listed} == EXPECTED_TOOLS
    assert all(tool.annotations and tool.annotations.read_only_hint for tool in listed)
    assert {str(resource.uri) for resource in resources} == EXPECTED_RESOURCES
    assert {template.uri_template for template in templates} == EXPECTED_TEMPLATES


def test_a_resource_returns_the_same_envelope_as_its_tool():
    server = build_server()
    contents = cast(list[Any], asyncio.run(server.read_resource("equations://topics")))
    payload = json.loads(contents[0].content)

    assert payload == list_topics()
    assert contents[0].mime_type == "application/json"


def test_a_narrative_resource_is_plain_text_with_a_stable_identity():
    server = build_server()
    contents = cast(list[Any], asyncio.run(server.read_resource("records://formula/michaelis-menten/narrative")))
    bundle = get_record_bundle("michaelis-menten")["data"]

    assert contents[0].mime_type == "text/plain"
    assert contents[0].content.startswith(f"[formula {bundle['identity']['rag_record_key']}]")
    assert "Equation: " in contents[0].content
