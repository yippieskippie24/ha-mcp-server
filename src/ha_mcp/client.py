import json
from typing import Any

import httpx
import websockets

from .config import settings


class HomeAssistantClient:
    """Async client for the Home Assistant REST and WebSocket APIs."""

    def __init__(self) -> None:
        self.base_url = settings.ha_url.rstrip("/")
        self._headers = {
            "Authorization": f"Bearer {settings.ha_token}",
            "Content-Type": "application/json",
        }

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.base_url}/api{path}",
                headers=self._headers,
                params=params,
                timeout=30.0,
            )
            r.raise_for_status()
            return r.json()

    async def get_text(self, path: str) -> str:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.base_url}/api{path}",
                headers=self._headers,
                timeout=30.0,
            )
            r.raise_for_status()
            return r.text

    async def post(self, path: str, data: dict | None = None) -> Any:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.base_url}/api{path}",
                headers=self._headers,
                json=data,
                timeout=30.0,
            )
            r.raise_for_status()
            return r.json()

    async def delete(self, path: str) -> int:
        async with httpx.AsyncClient() as client:
            r = await client.delete(
                f"{self.base_url}/api{path}",
                headers=self._headers,
                timeout=30.0,
            )
            r.raise_for_status()
            return r.status_code

    async def ws_command(self, command: dict) -> Any:
        """Open a WebSocket connection, authenticate, run one command, and return its result."""
        ws_url = (
            self.base_url
            .replace("http://", "ws://")
            .replace("https://", "wss://")
        )
        async with websockets.connect(f"{ws_url}/api/websocket") as ws:
            msg = json.loads(await ws.recv())
            if msg["type"] != "auth_required":
                raise RuntimeError(f"Expected auth_required, got: {msg}")

            await ws.send(json.dumps({
                "type": "auth",
                "access_token": settings.ha_token,
            }))
            msg = json.loads(await ws.recv())
            if msg["type"] != "auth_ok":
                raise RuntimeError(f"HA WebSocket auth failed: {msg}")

            await ws.send(json.dumps({"id": 1, **command}))
            while True:
                msg = json.loads(await ws.recv())
                if msg.get("id") == 1:
                    if not msg.get("success", True):
                        raise RuntimeError(
                            f"WebSocket command failed: {msg.get('error', msg)}"
                        )
                    return msg.get("result")
