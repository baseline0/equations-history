"""HTTP/MCP service for equations-history.

Exposes the fleet Layer-2 shape: liveness/readiness probes, a bearer-protected Streamable HTTP
/mcp endpoint, and two small REST reads for record bundles and crosswalks. All data is snapshot-backed;
this process never fetches from the network.
"""

from __future__ import annotations

import contextlib
import hmac
import json
import os
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Annotated, Any, cast

import typer
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from mcp.server.transport_security import TransportSecuritySettings

from equations_history.formula_catalog import CatalogError
from equations_history.mcp_server import build_server
from equations_history.record_bundle import build_bundle

PROBE_PATHS: frozenset[str] = frozenset({"/health", "/healthz", "/ready", "/readyz"})
SERVICE_NAME = "equations-history"


def load_fleet_auth_table() -> dict[str, dict[str, Any]]:
    """The FLEET_API_KEYS table from the environment, or from FLEET_API_KEYS_FILE."""
    keys_json = os.environ.get("FLEET_API_KEYS")
    if keys_json:
        try:
            parsed = json.loads(keys_json)
            if isinstance(parsed, dict):
                return parsed
        except (TypeError, ValueError):
            pass
    keys_file = os.environ.get("FLEET_API_KEYS_FILE")
    if keys_file and Path(keys_file).is_file():
        try:
            parsed = json.loads(Path(keys_file).read_text(encoding="utf-8"))
            if isinstance(parsed, dict):
                return parsed
        except (OSError, TypeError, ValueError):
            pass
    return {}


def check_authorization(auth_header: str) -> tuple[int | None, str]:
    """Check a Bearer token against the fleet key table. Returns (None, "") when authorized."""
    fleet_key = os.environ.get("FLEET_API_KEY")
    service_key = os.environ.get("EQUATIONS_HISTORY_API_KEY")
    auth_table = load_fleet_auth_table()
    if not fleet_key and not service_key and not auth_table:
        if os.environ.get("FLEET_REQUIRE_AUTH") == "1":
            return status.HTTP_503_SERVICE_UNAVAILABLE, "Service unavailable: no authentication is configured"
        return None, ""
    if not auth_header.startswith("Bearer ") or not auth_header[7:].strip():
        return status.HTTP_401_UNAUTHORIZED, "Unauthorized: missing or malformed Bearer token"
    token = auth_header[7:].strip()
    if fleet_key and hmac.compare_digest(token, fleet_key):
        return None, ""
    if service_key and hmac.compare_digest(token, service_key):
        return None, ""
    for key, spec in auth_table.items():
        if hmac.compare_digest(token, key):
            allowed = spec.get("allowed_tools", ["*"])
            if "*" not in allowed and SERVICE_NAME not in allowed:
                return status.HTTP_403_FORBIDDEN, f"Forbidden: token not authorized for {SERVICE_NAME}"
            return None, ""
    return status.HTTP_401_UNAUTHORIZED, "Unauthorized: invalid Bearer token"


def create_app() -> FastAPI:
    """Build the FastAPI app with probes, protected MCP endpoint and record REST reads."""
    server = build_server()

    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        session_manager = cast(Any, server._lowlevel_server)._session_manager
        async with session_manager.run():
            yield

    app = FastAPI(
        title=SERVICE_NAME,
        description="Traceable equation narratives, formula records and provenance snapshots",
        version="0.1.0",
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def enforce_auth(request: Request, call_next: Any) -> Response:
        if request.url.path in PROBE_PATHS:
            return cast(Response, await call_next(request))
        error_code, detail = check_authorization(request.headers.get("authorization", ""))
        if error_code is not None:
            headers = {"WWW-Authenticate": 'Bearer error="invalid_token"'} if error_code == 401 else None
            return JSONResponse(status_code=error_code, content={"detail": detail}, headers=headers)
        return cast(Response, await call_next(request))

    @app.get("/health")
    @app.get("/healthz")
    def health() -> dict[str, str]:
        return {"status": "alive", "service": SERVICE_NAME}

    @app.get("/ready")
    @app.get("/readyz")
    def ready(response: Response) -> dict[str, Any]:
        try:
            build_bundle("michaelis-menten")
        except (CatalogError, OSError) as error:
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
            return {"status": "not_ready", "error": str(error)}
        return {"status": "ready", "service": SERVICE_NAME}

    @app.get("/api/records/{record_id}")
    def api_record(record_id: str) -> dict[str, Any]:
        try:
            return build_bundle(record_id)
        except CatalogError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error

    @app.get("/api/records/{record_id}/crosswalk")
    def api_crosswalk(record_id: str) -> dict[str, Any]:
        try:
            return cast(dict[str, Any], build_bundle(record_id)["identity"])
        except CatalogError as error:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error

    security = TransportSecuritySettings(enable_dns_rebinding_protection=False)
    streamable_app = server.streamable_http_app(
        streamable_http_path="/mcp",
        transport_security=security,
        host="0.0.0.0",
    )
    for route in streamable_app.routes:
        app.routes.append(route)
    return app


app = create_app()


def start_server(host: str = "0.0.0.0", port: int = 8080) -> None:
    """Start the Streamable HTTP MCP service on the fleet's standard port."""
    uvicorn.run(create_app(), host=host, port=port, log_level="info")


cli_app = typer.Typer(help="HTTP and MCP server for equations-history", add_completion=False)


@cli_app.command()
def serve(
    host: Annotated[
        str, typer.Option("--host", help="Host interface to bind to")
    ] = "0.0.0.0",  # typer-explicit: allow-optional: standard binding interface
    port: Annotated[
        int, typer.Option("--port", help="Port to listen on")
    ] = 8080,  # typer-explicit: allow-optional: default fleet port for tool services
) -> None:
    """Serve the HTTP and Streamable HTTP MCP server until terminated."""
    start_server(host=host, port=port)


def main() -> None:
    """Console script entry point."""
    cli_app()


if __name__ == "__main__":
    main()
