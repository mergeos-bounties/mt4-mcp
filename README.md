# mt4-mcp

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![Version](https://img.shields.io/badge/version-0.1.0-0E8A16.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-5319E7.svg)](https://modelcontextprotocol.io)

**mt4-mcp** is an [MCP](https://modelcontextprotocol.io) server so AI agents can inspect and trade against a **MetaTrader 4** terminal — account, symbols, quotes, orders/positions, history — with a full **offline mock** for CI and demos.

---

## Modes

| Mode | When | Behavior |
| --- | --- | --- |
| **mock** (default) | Windows / CI / no terminal | Seeded demo account, FX/CFD symbols, orders, history |
| **live** | Host has a bridge configured | Optional file/HTTP bridge (see env vars); fails closed if unavailable |

---

## Highlights

| Capability | Description |
| --- | --- |
| **Offline demo** | `mt4-mcp demo` exercises doctor, quotes, market order, history |
| **MCP stdio serve** | Plug into Cursor / Claude / Grok as an MCP server |
| **One-shot call** | `mt4-mcp call …` without a full MCP host |
| **Safety** | Mock never talks to a real broker; live needs explicit env |

---

## Quick start

```powershell
cd mt4-mcp
python -m venv .venv
.\.venv\Scripts\activate
pip install -e ".[dev]"

mt4-mcp version
mt4-mcp status
mt4-mcp demo
mt4-mcp tools list
pytest -q
```

Mock mode needs **no** MetaTrader install.

---

## CLI reference

| Command | Purpose |
| --- | --- |
| `mt4-mcp version` | Version + mode |
| `mt4-mcp status` | Mode, balance, equity, and open order count |
| `mt4-mcp demo` | Offline smoke of core backend APIs |
| `mt4-mcp doctor` | Backend health |
| `mt4-mcp serve` | MCP server over **stdio** |
| `mt4-mcp call …` | One-shot tool call |
| `mt4-mcp tools list` | List MCP tools |

```powershell
mt4-mcp serve
```

---

## MCP tools

| Tool | Purpose |
| --- | --- |
| `mt4_mode` | Get/set mock\|live |
| `mt4_doctor` | Connectivity / account health |
| `mt4_seed_demo` | Reset mock account |
| `mt4_account` | Balance, equity, margin |
| `mt4_symbols` | Symbol list |
| `mt4_quote` | Bid/ask for a symbol |
| `mt4_ticks` | Recent quote ticks for a symbol |
| `mt4_orders` | Open orders |
| `mt4_order_send` | Market/pending OrderSend-style |
| `mt4_order_modify` | SL/TP/price modify |
| `mt4_order_close` | Close by ticket |
| `mt4_history` | Closed order history |

---

## Mock pending fills

In mock mode, pending orders are converted to market orders when quotes cross
their trigger price. The mock supports deterministic tests for `buy_limit`,
`sell_limit`, `buy_stop`, and `sell_stop` crossing behavior.

---

## MCP host config

```json
{
  "mcpServers": {
    "mt4-mcp": {
      "command": "python",
      "args": ["-m", "mt4_mcp"],
      "env": {
        "MT4_MCP_MODE": "mock"
      }
    }
  }
}
```

Also see `examples/cursor_mcp.json`.

---

## Live bridge (optional)

Set env (never commit secrets):

| Variable | Meaning |
| --- | --- |
| `MT4_MCP_MODE` | `mock` or `live` |
| `MT4_MCP_BRIDGE_URL` | Optional HTTP bridge base URL |
| `MT4_MCP_BRIDGE_FILE` | Optional request/response JSON file path |

Without a working bridge, **live** mode returns structured errors; demos stay on **mock**.


---

## Safety

| Rule | Detail |
| --- | --- |
| **Mock-only env** | Copy `examples/env.mock.example` → `.env` and keep `MT4_MCP_MODE=mock` |
| **No secrets in git** | Add `.env` to `.gitignore` — never commit live broker credentials |
| **Max volume** | Set `MT4_MCP_MAX_VOLUME` to cap any single order in live mode |
| **Symbol allowlist** | Restrict tradeable symbols via `MT4_MCP_SYMBOL_ALLOWLIST` (comma-sep) |

---

## Development

```powershell
pip install -e ".[dev]"
ruff check src tests
pytest -q
mt4-mcp demo
```

---

## License

[MIT](LICENSE)
