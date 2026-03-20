from mcp.server.fastmcp import FastMCP

from .client import HomeAssistantClient
from .tools import register_all


def create_server() -> FastMCP:
    # Disable DNS rebinding protection so requests proxied via Tailscale
    # (or any reverse proxy) are accepted regardless of Host header.
    try:
        from mcp.server.transport_security import TransportSecuritySettings
        transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)
    except ImportError:
        transport_security = None

    mcp = FastMCP(
        "Home Assistant MCP",
        **({"transport_security": transport_security} if transport_security else {}),
        instructions=(
            "MCP server for Home Assistant configuration management and data analysis.\n\n"
            "Available capabilities:\n"
            "- Automations: list, read, create, update, delete\n"
            "- Scripts: list, read, create, update, delete\n"
            "- Entities: list by domain, search, get full state\n"
            "- Devices & areas: browse device/area/entity registry\n"
            "- Integrations: list config entries and their status\n"
            "- History: state change history and pre-aggregated long-term statistics\n"
            "- Logbook: human-readable narrative event log\n"
            "- System: HA version, config info, error log\n\n"
            "Workflow tip: always use list_* or search_* tools first to discover IDs, "
            "then use get_* tools for full details on specific items."
        ),
    )
    ha = HomeAssistantClient()
    register_all(mcp, ha)
    return mcp


def main() -> None:
    import os
    import uvicorn
    mcp = create_server()
    host = os.environ.get("FASTMCP_HOST", "127.0.0.1")
    port = int(os.environ.get("FASTMCP_PORT", "8000"))
    uvicorn.run(mcp.streamable_http_app(), host=host, port=port)


if __name__ == "__main__":
    main()
