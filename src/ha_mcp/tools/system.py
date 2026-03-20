from mcp.server.fastmcp import FastMCP

from ..client import HomeAssistantClient


def register(mcp: FastMCP, ha: HomeAssistantClient) -> None:

    @mcp.tool()
    async def get_system_info() -> dict:
        """Get Home Assistant system information: version, location name, timezone,
        unit system, country, language, and installed component count.
        """
        config: dict = await ha.get("/config")
        return {
            "version": config.get("version"),
            "location_name": config.get("location_name"),
            "timezone": config.get("time_zone"),
            "latitude": config.get("latitude"),
            "longitude": config.get("longitude"),
            "unit_system": config.get("unit_system"),
            "currency": config.get("currency"),
            "country": config.get("country"),
            "language": config.get("language"),
            "state": config.get("state"),
            "components_count": len(config.get("components", [])),
            "components": sorted(config.get("components", [])),
        }

    @mcp.tool()
    async def get_error_log(lines: int = 100) -> str:
        """Retrieve recent entries from the Home Assistant error log for debugging.

        Args:
            lines: Number of lines to return from the end of the log (default: 100).
                   Increase for more context, decrease to keep responses concise.
        """
        log = await ha.get_text("/error_log")
        log_lines = log.strip().splitlines()
        if len(log_lines) > lines:
            return "\n".join(log_lines[-lines:])
        return log
