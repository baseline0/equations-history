"""The formula-record MCP views: ids, verbatim records and visible schema violations."""

import equations_history.mcp_server as server


def test_list_formula_records_excludes_sidecars():
    reply = server.list_formula_records()

    assert reply["view"] == "list_formula_records"
    assert "michaelis-menten" in reply["data"]["records"]
    assert "specificity" in reply["data"]["records"]
    assert "reviews" not in reply["data"]["records"]


def test_get_formula_record_returns_record_and_validation_errors():
    reply = server.get_formula_record("michaelis-menten")

    assert reply["view"] == "get_formula_record"
    assert reply["data"]["record"]["id"] == "michaelis-menten"
    assert "validation_errors" in reply["data"]


def test_full_records_carry_provenance_and_validate():
    from equations_history.formula_record import validate_record

    reply = server.get_formula_record("michaelis-menten")
    assert reply["data"]["provenance_complete"] is True
    assert reply["data"]["validation_errors"] == []
    code = reply["data"]["record"]["provenance"]["code"]
    assert code["file"].startswith("templates/")
    assert code["source_line"] > 0
    assert validate_record(reply["data"]["record"]) == []


def test_get_formula_record_refuses_bad_and_unknown_ids():
    assert "error" in server.get_formula_record("../secrets")
    assert "error" in server.get_formula_record("does-not-exist")
