# ha-mcp-server

An MCP (Model Context Protocol) server that gives Claude structured, token-efficient access to your Home Assistant instance — focused on **configuration management and data analysis**, not device control.

## Why

The typical approach to AI-assisted HA work (pasting YAML files, copying state dumps) is token-heavy and brittle. This server exposes purpose-built tools that:

- Return compact summaries for browsing, full configs only on demand
- Enable direct creation and editing of automations and scripts via the HA API
- Provide efficient access to historical sensor data and long-term statistics
- Work from any device (laptop, tablet, phone) via local network or Tailscale

## Architecture

```
Claude (laptop / iPad / phone)
        |
        | HTTP — local LAN or Tailscale
        ↓
[Docker Host]  ha-mcp-server  :8080
        |
        | HTTP + WebSocket
        ↓
[Home Assistant]  :8123
```

## Prerequisites

- Docker + Docker Compose on your Docker host
- Tailscale on your Docker host (for remote access)
- Home Assistant with the REST API enabled (on by default)
- A Home Assistant long-lived access token

## Setup

### 1. Clone and configure

```bash
git clone https://github.com/yippieskippie24/ha-mcp-server.git
cd ha-mcp-server
cp .env.example .env
```

Edit `.env` with your values:

```env
HA_URL=http://172.17.217.241:8123   # your HA local IP
HA_TOKEN=your_long_lived_token_here
```

**Getting a token:** Home Assistant → Profile (bottom-left avatar) → Security tab → Long-Lived Access Tokens → Create Token.

### 2. Start the server

```bash
docker-compose up -d
docker-compose logs -f   # verify it started cleanly
```

### 3. Connect Claude

The MCP server listens at `http://DOCKER_HOST_IP:8080/mcp`.

Use your Docker host's **local IP** when on LAN, or its **Tailscale IP** when remote.

**Claude Code (CLI) — add once per device:**

```bash
claude mcp add home-assistant --transport http http://DOCKER_HOST_IP:8080/mcp
```

**Claude Desktop** — edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "home-assistant": {
      "url": "http://DOCKER_HOST_IP:8080/mcp"
    }
  }
}
```

> On iOS/iPadOS, use the Tailscale IP of your Docker host in the URL.

## Available Tools

### Automations
| Tool | Description |
|------|-------------|
| `list_automations` | Summary list — id, alias, mode, trigger/action counts |
| `get_automation` | Full config (triggers, conditions, actions) for one automation |
| `create_or_update_automation` | Create or update an automation |
| `delete_automation` | Delete an automation |

### Scripts
| Tool | Description |
|------|-------------|
| `list_scripts` | Summary list — id, alias, mode, sequence step count |
| `get_script` | Full sequence config for one script |
| `create_or_update_script` | Create or update a script |
| `delete_script` | Delete a script |

### Entities, Devices & Areas
| Tool | Description |
|------|-------------|
| `list_entities` | All entities with current state; filterable by domain |
| `get_entity_state` | Full state + all attributes for one entity |
| `search_entities` | Substring search across entity_id and friendly names |
| `list_areas` | All areas/rooms defined in HA |
| `list_integrations` | Installed integrations and their load status |
| `get_entity_registry` | Full entity registry with device/area/platform metadata |
| `list_devices` | Device registry — manufacturer, model, area assignment |

### History & Analysis
| Tool | Description |
|------|-------------|
| `get_entity_history` | Raw state change history for one or more entities |
| `get_statistics` | Pre-aggregated stats (hourly/daily/weekly/monthly mean, min, max, sum) |
| `get_logbook` | Human-readable event narrative; filterable by entity |

### System
| Tool | Description |
|------|-------------|
| `get_system_info` | HA version, location, timezone, unit system, component list |
| `get_error_log` | Recent HA error log entries for debugging |

## Updating

```bash
git pull
docker-compose up -d --build
```

## Local Development (without Docker)

```bash
pip install -e .

export HA_URL=http://172.17.217.241:8123
export HA_TOKEN=your_token_here

python -m ha_mcp
```
