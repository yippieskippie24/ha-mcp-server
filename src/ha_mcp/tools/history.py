from mcp.server.fastmcp import FastMCP

from ..client import HomeAssistantClient


def register(mcp: FastMCP, ha: HomeAssistantClient) -> None:

    @mcp.tool()
    async def get_entity_history(
        entity_ids: list[str],
        start_time: str,
        end_time: str | None = None,
        minimal_response: bool = True,
    ) -> dict[str, list]:
        """Get state change history for one or more entities over a time range.

        Args:
            entity_ids: List of entity IDs to query.
                        Example: ['sensor.living_room_temp', 'sensor.outdoor_humidity']
            start_time: ISO 8601 start time. Example: '2024-01-15T00:00:00+00:00'
            end_time: ISO 8601 end time. Defaults to now.
            minimal_response: If True (default), returns only state + last_changed per entry,
                              which is much more token-efficient. Set to False to include
                              full attributes for each state change.

        Returns a dict keyed by entity_id, each containing a list of state change records.
        """
        params: dict = {
            "filter_entity_id": ",".join(entity_ids),
            "minimal_response": "true" if minimal_response else "false",
            "no_attributes": "true" if minimal_response else "false",
        }
        if end_time:
            params["end_time"] = end_time

        data: list[list[dict]] = await ha.get(
            f"/history/period/{start_time}", params=params
        )
        result: dict[str, list] = {}
        for entity_history in data:
            if entity_history:
                eid = entity_history[0].get("entity_id", "unknown")
                result[eid] = entity_history
        return result

    @mcp.tool()
    async def get_statistics(
        statistic_ids: list[str],
        start_time: str,
        end_time: str,
        period: str = "day",
        types: list[str] | None = None,
    ) -> dict:
        """Get long-term statistics for sensors (pre-aggregated by hour/day/week/month).

        Best for analyzing energy usage, temperature trends, and other continuous measurements
        over longer time ranges. Uses pre-computed statistics — much more efficient than
        raw history for spans of weeks or months.

        Args:
            statistic_ids: List of entity IDs with statistics enabled.
                           Typically sensor.* entities with a numeric state class.
            start_time: ISO 8601 start time. Example: '2024-01-01T00:00:00+00:00'
            end_time: ISO 8601 end time.
            period: Aggregation period — 'hour', 'day', 'week', or 'month'.
            types: Stat types to include — any of 'mean', 'min', 'max', 'sum', 'state',
                   'change'. Defaults to ['mean', 'min', 'max', 'sum'].

        Returns a dict keyed by statistic_id with a list of aggregated data points.
        """
        return await ha.ws_command({
            "type": "recorder/statistics_during_period",
            "start_time": start_time,
            "end_time": end_time,
            "statistic_ids": statistic_ids,
            "period": period,
            "types": types or ["mean", "min", "max", "sum"],
        })

    @mcp.tool()
    async def get_logbook(
        start_time: str,
        end_time: str | None = None,
        entity_id: str | None = None,
    ) -> list[dict]:
        """Get logbook entries — a human-readable narrative of significant state changes and
        automation/script events.

        More readable than raw history. Good for understanding what happened and when,
        and for debugging automation behavior.

        Args:
            start_time: ISO 8601 start time. Example: '2024-01-15T00:00:00+00:00'
            end_time: ISO 8601 end time. Defaults to now.
            entity_id: Filter to a specific entity. Omit to return all entries
                       (can be large — use entity_id filter for targeted debugging).
        """
        params: dict = {}
        if end_time:
            params["end_time"] = end_time
        if entity_id:
            params["entity_id"] = entity_id

        return await ha.get(f"/logbook/{start_time}", params=params)
