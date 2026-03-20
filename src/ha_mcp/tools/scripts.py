from typing import Any

from mcp.server.fastmcp import FastMCP

from ..client import HomeAssistantClient


def register(mcp: FastMCP, ha: HomeAssistantClient) -> None:

    @mcp.tool()
    async def list_scripts() -> list[dict]:
        """List all scripts with summary information.

        Returns id, alias, description, mode, sequence step count, and field names.
        Use get_script() to fetch the full sequence for a specific script.
        """
        configs: dict = await ha.get("/config/script/config")
        # The script config endpoint returns a dict keyed by script_id
        return [
            {
                "id": script_id,
                "alias": cfg.get("alias", script_id),
                "description": cfg.get("description", ""),
                "mode": cfg.get("mode", "single"),
                "sequence_steps": len(cfg.get("sequence", [])),
                "fields": list(cfg.get("fields", {}).keys()),
            }
            for script_id, cfg in configs.items()
        ]

    @mcp.tool()
    async def get_script(script_id: str) -> dict:
        """Get the full configuration for a specific script including its complete sequence.

        Args:
            script_id: The script's ID (from list_scripts)
        """
        return await ha.get(f"/config/script/config/{script_id}")

    @mcp.tool()
    async def create_or_update_script(
        script_id: str, config: dict[str, Any]
    ) -> dict:
        """Create a new script or update an existing one.

        Args:
            script_id: Unique ID for the script. Use an existing ID to update,
                       or a new descriptive slug to create.
            config: Script config. Required: alias, sequence. Optional: description,
                    mode (single/restart/queued/parallel), fields, icon.

        Example config:
            {
                "alias": "Good Morning Routine",
                "sequence": [
                    {"service": "light.turn_on", "target": {"area_id": "bedroom"}},
                    {"delay": {"minutes": 5}},
                    {"service": "cover.open_cover", "target": {"area_id": "bedroom"}}
                ]
            }
        """
        result = await ha.post(f"/config/script/config/{script_id}", config)
        return {"status": "ok", "result": result}

    @mcp.tool()
    async def delete_script(script_id: str) -> dict:
        """Permanently delete a script.

        Args:
            script_id: The script's ID (from list_scripts)
        """
        status = await ha.delete(f"/config/script/config/{script_id}")
        return {"status": "deleted", "script_id": script_id, "http_status": status}
