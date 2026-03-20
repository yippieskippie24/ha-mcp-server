from mcp.server.fastmcp import FastMCP

from ..client import HomeAssistantClient


def register(mcp: FastMCP, ha: HomeAssistantClient) -> None:

    @mcp.tool()
    async def list_entities(domain: str | None = None) -> list[dict]:
        """List entities with their current state and key attributes.

        Args:
            domain: Optional domain filter (e.g. 'light', 'sensor', 'switch', 'climate',
                    'binary_sensor', 'media_player', 'automation', 'cover').
                    Strongly recommended for large installations to reduce response size.
        """
        states: list[dict] = await ha.get("/states")
        result = []
        for s in states:
            entity_id = s["entity_id"]
            if domain and not entity_id.startswith(f"{domain}."):
                continue
            attrs = s.get("attributes", {})
            result.append({
                "entity_id": entity_id,
                "state": s["state"],
                "friendly_name": attrs.get("friendly_name"),
                "unit": attrs.get("unit_of_measurement"),
                "device_class": attrs.get("device_class"),
                "last_changed": s.get("last_changed"),
            })
        return result

    @mcp.tool()
    async def get_entity_state(entity_id: str) -> dict:
        """Get the full current state and all attributes for a specific entity.

        Args:
            entity_id: The entity ID (e.g. 'sensor.living_room_temperature')
        """
        return await ha.get(f"/states/{entity_id}")

    @mcp.tool()
    async def search_entities(query: str) -> list[dict]:
        """Search for entities by entity_id or friendly_name (case-insensitive substring match).

        Args:
            query: Search string matched against entity_id and friendly_name.
                   Examples: 'living room', 'temperature', 'garage'
        """
        states: list[dict] = await ha.get("/states")
        q = query.lower()
        results = []
        for s in states:
            entity_id = s["entity_id"]
            friendly_name = s.get("attributes", {}).get("friendly_name", "")
            if q in entity_id.lower() or q in str(friendly_name).lower():
                results.append({
                    "entity_id": entity_id,
                    "state": s["state"],
                    "friendly_name": friendly_name,
                    "unit": s.get("attributes", {}).get("unit_of_measurement"),
                    "last_changed": s.get("last_changed"),
                })
        return results

    @mcp.tool()
    async def list_areas() -> list[dict]:
        """List all areas (rooms/zones) defined in Home Assistant."""
        result = await ha.ws_command({"type": "config/area_registry/list"})
        return [
            {
                "area_id": a["area_id"],
                "name": a["name"],
                "aliases": a.get("aliases", []),
            }
            for a in (result or [])
        ]

    @mcp.tool()
    async def list_integrations() -> list[dict]:
        """List all configured integrations (config entries) with their current status.

        Returns domain, title, state (loaded/setup_error/not_loaded/etc.), and disabled status.
        Useful for auditing what's installed and identifying broken integrations.
        """
        entries: list[dict] = await ha.get("/config/config_entries/entry")
        return [
            {
                "entry_id": e["entry_id"],
                "domain": e["domain"],
                "title": e["title"],
                "state": e["state"],
                "disabled_by": e.get("disabled_by"),
                "reason": e.get("reason"),
            }
            for e in entries
        ]

    @mcp.tool()
    async def get_entity_registry() -> list[dict]:
        """Get the full entity registry: all entities with device, area, and platform metadata.

        More detailed than list_entities — includes device_id, area_id, platform assignment,
        and whether each entity is disabled or hidden. Use this to understand
        entity-device-area relationships across your entire HA instance.
        """
        result = await ha.ws_command({"type": "config/entity_registry/list"})
        return [
            {
                "entity_id": e["entity_id"],
                "unique_id": e.get("unique_id"),
                "platform": e.get("platform"),
                "device_id": e.get("device_id"),
                "area_id": e.get("area_id"),
                "name": e.get("name"),
                "original_name": e.get("original_name"),
                "disabled_by": e.get("disabled_by"),
                "hidden_by": e.get("hidden_by"),
            }
            for e in (result or [])
        ]

    @mcp.tool()
    async def list_devices() -> list[dict]:
        """List all devices in the device registry with area, manufacturer, and model info.

        Useful for understanding the physical device inventory and device-area relationships.
        """
        result = await ha.ws_command({"type": "config/device_registry/list"})
        return [
            {
                "id": d["id"],
                "name": d.get("name"),
                "name_by_user": d.get("name_by_user"),
                "manufacturer": d.get("manufacturer"),
                "model": d.get("model"),
                "sw_version": d.get("sw_version"),
                "area_id": d.get("area_id"),
                "disabled_by": d.get("disabled_by"),
                "entry_type": d.get("entry_type"),
            }
            for d in (result or [])
        ]
