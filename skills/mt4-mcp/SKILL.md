---
name: mt4-mcp
description: >
  MetaTrader 4 account/quotes/orders (mock + live bridge). CLI `mt4-mcp` + MCP stdio serve. Use when the user mentions
  mt4-mcp, /mt4-mcp, or related domain work. One-command Grok install from GitHub.
metadata:
  short-description: "MetaTrader 4 account/quotes/orders (mock + live bridge)."
---

# mt4-mcp

## One-command install (Grok)

```bash
pip install "git+https://github.com/mergeos-bounties/mt4-mcp.git" && grok plugin install mergeos-bounties/mt4-mcp --trust
```

Or plugin first, then package:

```bash
grok plugin install mergeos-bounties/mt4-mcp --trust
pip install "git+https://github.com/mergeos-bounties/mt4-mcp.git"
```

Verify:

```bash
mt4-mcp version
mt4-mcp doctor
mt4-mcp demo
mt4-mcp serve   # MCP stdio for hosts
```

## Modes

| Env | Values |
| --- | --- |
| `MT4_MCP_MODE` | `mock` (default) · `live` |

## MCP

```bash
mt4-mcp serve
```

Config ships in plugin `.mcp.json`. Manual: see repo `examples/`.
