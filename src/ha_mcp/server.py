from mcp.server.fastmcp import FastMCP

from .client import HomeAssistantClient
from .config import settings
from .tools import register_all


def create_server() -> FastMCP:
    mcp = FastMCP(
        "Home Assistant MCP",
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
        host=settings.mcp_host,
        port=settings.mcp_port,
    )
    ha = HomeAssistantClient()
    register_all(mcp, ha)
    return mcp


def main() -> None:
    mcp = create_server()
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
