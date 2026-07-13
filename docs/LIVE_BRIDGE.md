# Live Bridge — HTTP Contract (MT4)

## Overview

When `MT4_MCP_MODE=live` and `MT4_MCP_BRIDGE_URL` is set, mt4-mcp delegates
account/quote queries to an external bridge server.

## Endpoints

### GET {bridge}/account

Returns account summary.

**Response (200):**
```json
{
  "ok": true,
  "login": 5005001,
  "server": "MockMT4-Demo",
  "balance": 25000.0,
  "equity": 25000.0,
  "margin": 0,
  "margin_free": 25000.0,
  "currency": "USD",
  "leverage": 200
}
```

### GET {bridge}/quote?symbol=EURUSD

Returns current quote.

**Response (200):**
```json
{
  "ok": true,
  "symbol": "EURUSD",
  "bid": 1.0850,
  "ask": 1.0853,
  "spread": 3,
  "timestamp": "2026-07-13T07:00:00Z"
}
```

### Error response

```json
{
  "ok": false,
  "error": "Bridge unavailable"
}
```

## Offline behavior

- Connection errors return `{"ok": false, "error": "live bridge unavailable"}`
- CI/demo always uses mock
