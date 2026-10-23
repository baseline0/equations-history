"""The equations-history MCP server: three read-only tools that reply with the fleet read envelope."""

import asyncio

import pytest

from equations_history.mcp_server import (
    CONTRACT,
    VERSION,
    build_server,
    get_equation,
    list_equations,
    list_topics,
)

pytestmark = pytest.mark.unit

EXPECTED_TOOLS = {"list_topics", "list_equations", "get_equation"}


def test_every_reply_is_the_fleet_read_envelope():
    for reply in (list_topics(), list_equations("autoencoders"), get_equation("autoencoders", "deterministic_encoder")):
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


def test_the_server_offers_exactly_the_three_read_tools_and_all_are_read_only():
    listed = asyncio.run(build_server().list_tools())

    assert {tool.name for tool in listed} == EXPECTED_TOOLS
    assert all(tool.annotations and tool.annotations.read_only_hint for tool in listed)
