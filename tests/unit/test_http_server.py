"""The HTTP/MCP service keeps probes open and protects snapshots with fleet auth."""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient

from equations_history.http_server import check_authorization, create_app

pytestmark = pytest.mark.unit

AUTH_ENV = (
    "FLEET_API_KEY",
    "EQUATIONS_HISTORY_API_KEY",
    "FLEET_API_KEYS",
    "FLEET_API_KEYS_FILE",
    "FLEET_REQUIRE_AUTH",
)


def _clear_auth(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in AUTH_ENV:
        monkeypatch.delenv(name, raising=False)


def test_with_no_keys_local_access_is_allowed(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_auth(monkeypatch)

    assert check_authorization("") == (None, "")


def test_a_deployment_without_a_key_fails_closed_when_required(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_auth(monkeypatch)
    monkeypatch.setenv("FLEET_REQUIRE_AUTH", "1")

    code, detail = check_authorization("Bearer anything")

    assert code == 503
    assert "no authentication is configured" in detail


def test_the_master_key_and_the_service_key_are_both_accepted(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_auth(monkeypatch)
    monkeypatch.setenv("FLEET_API_KEY", "fleet-secret")

    assert check_authorization("Bearer fleet-secret") == (None, "")
    assert check_authorization("Bearer wrong")[0] == 401
    assert check_authorization("")[0] == 401

    monkeypatch.setenv("EQUATIONS_HISTORY_API_KEY", "service-secret")
    assert check_authorization("Bearer service-secret") == (None, "")


def test_a_lookup_token_is_limited_to_its_allowed_tools(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_auth(monkeypatch)
    monkeypatch.setenv(
        "FLEET_API_KEYS",
        json.dumps(
            {
                "reader-token": {"allowed_tools": ["equations-history", "tool-rag"], "read_only": True},
                "other-token": {"allowed_tools": ["tool-rag"], "read_only": True},
            }
        ),
    )

    assert check_authorization("Bearer reader-token") == (None, "")
    assert check_authorization("Bearer other-token")[0] == 403
    assert check_authorization("Bearer unknown")[0] == 401


def test_probes_are_open_but_mcp_and_api_are_protected(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_auth(monkeypatch)
    monkeypatch.setenv("FLEET_API_KEY", "fleet-secret")
    client = TestClient(create_app())

    for path in ("/health", "/healthz", "/ready", "/readyz"):
        assert client.get(path).status_code == 200

    assert client.get("/api/records/michaelis-menten").status_code == 401
    assert client.post("/mcp", json={}).status_code == 401
    assert (
        client.get("/api/records/michaelis-menten", headers={"Authorization": "Bearer fleet-secret"}).status_code == 200
    )


def test_the_app_exposes_the_standard_route_shape(monkeypatch: pytest.MonkeyPatch) -> None:
    _clear_auth(monkeypatch)
    app = create_app()
    paths = {getattr(route, "path", "") for route in app.routes}

    assert {"/healthz", "/readyz", "/mcp", "/api/records/{record_id}"} <= paths
    assert "/api/records/{record_id}/crosswalk" in paths
