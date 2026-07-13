"""FastMCP server: MetaTrader 4 tools for AI agents."""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from mt4_mcp.backend import get_backend, switch_mode
from mt4_mcp.config import get_mode

mcp = FastMCP(
    "mt4-mcp",
    instructions=(
        "MetaTrader 4 MCP server. Prefer mock mode offline. "
        "Typical flow: mt4_doctor → mt4_account → mt4_quote → mt4_order_send → mt4_orders."
    ),
)


def _j(data: Any) -> str:
    return json.dumps(data, indent=2, default=str)


@mcp.tool()
def mt4_mode(mode: str | None = None) -> str:
    """Get or set MT4 backend mode (mock|live)."""
    if mode:
        return _j(switch_mode(mode))
    b = get_backend()
    return _j({"mode": get_mode(), "backend": b.name, "doctor": b.doctor()})


@mcp.tool()
def mt4_doctor() -> str:
    """Check mock/live connectivity and account health."""
    return _j(get_backend().doctor())


@mcp.tool()
def mt4_seed_demo() -> str:
    """Reset the mock MT4 demo account (mock only)."""
    return _j(get_backend().seed_demo())


@mcp.tool()
def mt4_account() -> str:
    """Account balance, equity, margin."""
    return _j(get_backend().account())


@mcp.tool()
def mt4_symbols() -> str:
    """List tradeable symbols."""
    return _j(get_backend().symbols())


@mcp.tool()
def mt4_quote(symbol: str) -> str:
    """Bid/ask quote for a symbol (e.g. EURUSD)."""
    return _j(get_backend().quote(symbol))


@mcp.tool()
def mt4_orders() -> str:
    """List open orders/tickets."""
    return _j(get_backend().orders())


@mcp.tool()
def mt4_order_send(
    symbol: str,
    side: str,
    volume: float,
    order_type: str = "market",
    price: float | None = None,
    sl: float | None = None,
    tp: float | None = None,
    comment: str = "",
) -> str:
    """Place market or pending order (OrderSend-style).

    Args:
        symbol: e.g. EURUSD
        side: buy or sell
        volume: lots
        order_type: market|buy_limit|sell_limit|buy_stop|sell_stop
        price: required for pending
        sl: stop loss
        tp: take profit
        comment: order comment
    """
    return _j(
        get_backend().order_send(symbol, side, volume, order_type, price, sl, tp, comment)
    )


@mcp.tool()
def mt4_order_modify(
    ticket: int,
    price: float | None = None,
    sl: float | None = None,
    tp: float | None = None,
) -> str:
    """Modify SL/TP/price on an open ticket."""
    return _j(get_backend().order_modify(ticket, price, sl, tp))


@mcp.tool()
def mt4_order_close(ticket: int, volume: float | None = None) -> str:
    """Close order by ticket (optional partial volume)."""
    return _j(get_backend().order_close(ticket, volume))


@mcp.tool()
def mt4_history(limit: int = 20) -> str:
    """Closed order history."""
    return _j(get_backend().history(limit=limit))


def run_stdio() -> None:
    mcp.run(transport="stdio")
