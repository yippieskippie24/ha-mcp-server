from typing import Any

from mcp.server.fastmcp import FastMCP

from ..client import HomeAssistantClient


def register(mcp: FastMCP, ha: HomeAssistantClient) -> None:

    @mcp.tool()
    async def list_automations() -> list[dict]:
        """List all automations with summary information.

        Returns id, alias, description, mode, and trigger/condition/action counts.
        Use get_automation() to fetch the full trigger/condition/action config for a specific one.
        """
        configs: list[dict] = await ha.get("/config/automation/config")
        return [
            {
                "id": a.get("id"),
                "alias": a.get("alias"),
                "description": a.get("description", ""),
                "mode": a.get("mode", "single"),
                "trigger_count": len(a.get("trigger", [])),
                "condition_count": len(a.get("condition", [])),
                "action_count": len(a.get("action", [])),
            }
            for a in configs
        ]

    @mcp.tool()
    async def get_automation(automation_id: str) -> dict:
        """Get the full configuration for a specific automation including all triggers,
        conditions, and actions.

        Args:
            automation_id: The automation's unique ID (from list_automations)
        """
        return await ha.get(f"/config/automation/config/{automation_id}")

    @mcp.tool()
    async def create_or_update_automation(
        automation_id: str, config: dict[str, Any]
    ) -> dict:
        """Create a new automation or update an existing one.

        Args:
            automation_id: Unique ID for the automation. Use an existing ID to update,
                           or a new descriptive slug / UUID to create.
            config: Full automation config. Required keys: alias, trigger, action.
                    Optional: description, condition, mode (single/restart/queued/parallel).

        Example config:
            {
                "alias": "Turn on porch light at sunset",
                "trigger": [{"platform": "sun", "event": "sunset"}],
                "action": [{"service": "light.turn_on",
                             "target": {"entity_id": "light.porch"}}]
            }
        """
        result = await ha.post(f"/config/automation/config/{automation_id}", config)
        return {"status": "ok", "result": result}

    @mcp.tool()
    async def delete_automation(automation_id: str) -> dict:
        """Permanently delete an automation.

        Args:
            automation_id: The automation's unique ID (from list_automations)
        """
        status = await ha.delete(f"/config/automation/config/{automation_id}")
        return {"status": "deleted", "automation_id": automation_id, "http_status": status}
