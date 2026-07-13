"""
MCP resource: mt4://account snapshot.

Registers a resource URI `mt4://account` that returns the current
mock MetaTrader 4 account state — balance, equity, margin, open
positions, and orders — as a JSON payload consumable by MCP hosts.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List

from mt4_mcp.mock.account import MockAccount, MockPosition, MockOrder


def _position_to_dict(pos: MockPosition) -> Dict[str, Any]:
    """Convierte una posición a un diccionario JSON serializable."""
    return {
        "ticket": pos.ticket,
        "symbol": pos.symbol,
        "type": pos.order_type,
        "volume": pos.volume,
        "open_price": pos.open_price,
        "current_price": pos.current_price,
        "sl": pos.sl,
        "tp": pos.tp,
        "swap": pos.swap,
        "profit": pos.profit,
        "comment": pos.comment,
        "open_time": pos.open_time.isoformat() if pos.open_time else None,
    }


def _order_to_dict(order: MockOrder) -> Dict[str, Any]:
    """Convierte una orden pendiente a un diccionario JSON serializable."""
    return {
        "ticket": order.ticket,
        "symbol": order.symbol,
        "type": order.order_type,
        "volume": order.volume,
        "price": order.price,
        "sl": order.sl,
        "tp": order.tp,
        "expiration": order.expiration.isoformat() if order.expiration else None,
        "comment": order.comment,
    }


def account_snapshot(account: MockAccount) -> Dict[str, Any]:
    """
    Genera una instantánea JSON del estado de la cuenta MT4.
    """
    floating = sum(p.profit for p in account.positions)
    return {
        "login": account.login,
        "server": account.server,
        "currency": account.currency,
        "leverage": account.leverage,
        "balance": round(account.balance, 2),
        "equity": round(account.balance + floating, 2),
        "margin": round(account.used_margin, 2),
        "free_margin": round(account.balance + floating - account.used_margin, 2),
        "margin_level": round((account.balance + floating) / account.used_margin * 100, 2) if account.used_margin > 0 else 0.0,
        "floating_profit": round(floating, 2),
        "positions": [_position_to_dict(p) for p in account.positions],
        "pending_orders": [_order_to_dict(o) for o in account.pending_orders],
        "position_count": len(account.positions),
        "order_count": len(account.pending_orders),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@mcp.resource("mt4://account")
def get_account_snapshot() -> str:
    """
    Recurso MCP que devuelve una instantánea de la cuenta MT4.
    """
    from mt4_mcp.mock.account import get_default_account
    account = get_default_account()
    snapshot = account_snapshot(account)
    return json.dumps(snapshot, indent=2)