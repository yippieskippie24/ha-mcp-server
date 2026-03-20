from mcp.server.fastmcp import FastMCP

from ..client import HomeAssistantClient
from . import automations, history, scripts, states, system


def register_all(mcp: FastMCP, ha: HomeAssistantClient) -> None:
    """Register all tool groups with the MCP server."""
    automations.register(mcp, ha)
    scripts.register(mcp, ha)
    states.register(mcp, ha)
    history.register(mcp, ha)
    system.register(mcp, ha)
