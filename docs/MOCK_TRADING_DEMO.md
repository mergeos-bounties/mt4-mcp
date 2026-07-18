# Mock trading demo without MT4

This walkthrough verifies `mt4-mcp` end to end in **mock mode**. It does not require MetaTrader 4, a broker account, a bridge process, or any live credentials.

Use it for local smoke tests, CI checks, and MCP host demos before switching any environment to live mode.

## Why mock mode is safe

Mock mode uses the in-process `MockMT4Backend` seeded with deterministic demo account data, symbols, quotes, orders, and history. It never connects to a real MT4 terminal and never sends orders to a broker.

Keep this environment variable set while following the demo:

```bash
export MT4_MCP_MODE=mock
```

PowerShell equivalent:

```powershell
$env:MT4_MCP_MODE = "mock"
```

## 1. Install locally

From a fresh clone:

```bash
git clone https://github.com/mergeos-bounties/mt4-mcp.git
cd mt4-mcp
python -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
```

On Windows PowerShell:

```powershell
git clone https://github.com/mergeos-bounties/mt4-mcp.git
cd mt4-mcp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## 2. Confirm mode and backend health

```bash
mt4-mcp version
mt4-mcp doctor
mt4-mcp status
```

Expected signals:

- `version` includes the package version and `mode: mock`
- `doctor` reports a mock backend instead of bridge connectivity errors
- `status` prints balance, equity, and open order count from the seeded mock account

## 3. Run the one-command smoke demo

```bash
mt4-mcp demo
```

The demo performs this offline flow:

1. Seeds the mock account.
2. Prints doctor information.
3. Reads account state.
4. Fetches an `EURUSD` quote.
5. Sends a tiny mock market order.
6. Lists open orders.
7. Modifies stop-loss/take-profit.
8. Closes the mock order.
9. Prints recent history.

A successful run ends with:

```text
mt4-mcp demo complete (mock).
```

## 4. Exercise individual tools without an MCP host

The `call` command lets you test MCP tool behavior directly from the CLI:

```bash
mt4-mcp call account
mt4-mcp call symbols
mt4-mcp call quote symbol=EURUSD
mt4-mcp call ticks symbol=EURUSD limit=3
mt4-mcp call history limit=5
```

To test a complete mock order lifecycle manually:

```bash
mt4-mcp call seed_demo
mt4-mcp call order_send symbol=EURUSD side=buy volume=0.1 order_type=market sl=1.0800 tp=1.0900 comment=mock-doc-demo
mt4-mcp call orders
mt4-mcp call order_modify ticket=1001 sl=1.0810 tp=1.0890
mt4-mcp call order_close ticket=1001
mt4-mcp call history limit=5
```

The default seeded mock order ticket starts at `1001`; if you have sent multiple mock orders in the same process, use the ticket returned by `order_send`.

## 5. Run tests that cover the mock path

```bash
pytest -q tests/test_cli_demo.py tests/test_mock_backend.py tests/test_server_tools.py
```

These tests cover the CLI demo, backend account/order behavior, and server tool dispatch without requiring MT4.

## 6. Connect an MCP host in mock mode

For any stdio MCP host, use:

```json
{
  "mcpServers": {
    "mt4-mcp": {
      "command": "mt4-mcp",
      "args": ["serve"],
      "env": {
        "MT4_MCP_MODE": "mock"
      }
    }
  }
}
```

After the host starts the server, ask it to call `mt4_doctor`, `mt4_account`, or `mt4_quote` to verify that the mock backend responds.

## Switching to live later

Only switch to live mode after the mock demo passes and you have intentionally configured a safe bridge:

```bash
export MT4_MCP_MODE=live
export MT4_MCP_BRIDGE_URL=http://127.0.0.1:8765
```

Live mode fails closed if the configured bridge is unavailable. Never commit `.env` files or broker credentials.
