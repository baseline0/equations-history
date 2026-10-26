"""Every registered topic is reachable over HTTP, and the routes agree with the registry."""

import pytest
from fastapi.testclient import TestClient

from equations_history import registry
from equations_history.api import API_ROUTES, app

client = TestClient(app)


def test_every_registered_topic_has_a_route() -> None:
    assert set(API_ROUTES) == set(registry.topics())


@pytest.mark.parametrize("topic", sorted(API_ROUTES))
def test_list_route_returns_exactly_the_registry_equations(topic: str) -> None:
    route = API_ROUTES[topic]

    response = client.get(f"/api/equations/{route.segment}")

    assert response.status_code == 200
    assert list(response.json()) == registry.names(topic)


@pytest.mark.parametrize("topic", sorted(API_ROUTES))
def test_single_equation_route_returns_the_named_equation(topic: str) -> None:
    route = API_ROUTES[topic]
    name = registry.names(topic)[0]

    response = client.get(f"/api/equations/{route.segment}/{name}")

    assert response.status_code == 200
    assert response.json()["name"] == registry.get(topic, name).name


def test_an_unknown_equation_is_a_404() -> None:
    response = client.get("/api/equations/quantum/no_such_equation")

    assert response.status_code == 404


def test_a_catalog_equation_reports_its_math_trace_source() -> None:
    body = client.get("/api/equations/biochemistry/michaelis_menten").json()

    assert body["source"] == "templates/biochemistry/src/model.py:32"


def test_the_response_carries_the_year_placeholder() -> None:
    body = client.get("/api/equations/biochemistry/michaelis_menten").json()

    assert "year" in body
    assert body["year"] is None
