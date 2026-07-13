"""Offline MetaTrader 4-style mock terminal."""

from __future__ import annotations

import time
from copy import deepcopy
from typing import Any


class MockBackend:
    name = "mock"

    def __init__(self) -> None:
        self._ticket = 100000
        self.seed_demo()

    def _next_ticket(self) -> int:
        self._ticket += 1
        return self._ticket

    def seed_demo(self) -> dict[str, Any]:
        self._balance = 10_000.0
        self._equity = 10_000.0
        self._margin = 0.0
        self._currency = "USD"
        self._leverage = 100
        self._login = 900001
        self._server = "MockBroker-Demo"
        self._symbols: dict[str, dict[str, Any]] = {
            "EURUSD": {
                "symbol": "EURUSD",
                "digits": 5,
                "point": 0.00001,
                "trade_contract_size": 100000,
                "bid": 1.08520,
                "ask": 1.08540,
                "spread": 20,
            },
            "GBPUSD": {
                "symbol": "GBPUSD",
                "digits": 5,
                "point": 0.00001,
                "trade_contract_size": 100000,
                "bid": 1.26510,
                "ask": 1.26535,
                "spread": 25,
            },
            "USDJPY": {
                "symbol": "USDJPY",
                "digits": 3,
                "point": 0.001,
                "trade_contract_size": 100000,
                "bid": 149.520,
                "ask": 149.545,
                "spread": 25,
            },
            "XAUUSD": {
                "symbol": "XAUUSD",
                "digits": 2,
                "point": 0.01,
                "trade_contract_size": 100,
                "bid": 2325.40,
                "ask": 2325.80,
                "spread": 40,
            },
        }
        self._orders: dict[int, dict[str, Any]] = {}
        self._ticks: dict[str, list[dict[str, Any]]] = {symbol: [] for symbol in self._symbols}
        self._history: list[dict[str, Any]] = [
            {
                "ticket": 100001,
                "symbol": "EURUSD",
                "side": "buy",
                "volume": 0.10,
                "open_price": 1.08000,
                "close_price": 1.08250,
                "profit": 25.0,
                "comment": "demo-history",
                "closed_at": time.time() - 86400,
            }
        ]
        self._recalc()
        return {
            "ok": True,
            "mode": "mock",
            "login": self._login,
            "symbols": list(self._symbols),
            "open_orders": 0,
        }

    def _recalc(self) -> None:
        floating = sum(float(o.get("profit", 0.0)) for o in self._orders.values())
        margin = sum(float(o.get("margin", 0.0)) for o in self._orders.values())
        self._margin = round(margin, 2)
        self._equity = round(self._balance + floating, 2)

    def doctor(self) -> dict[str, Any]:
        self._recalc()
        return {
            "ok": True,
            "mode": "mock",
            "terminal": "MetaTrader 4 (mock)",
            "connected": True,
            "login": self._login,
            "server": self._server,
            "balance": self._balance,
            "equity": self._equity,
            "open_orders": len(self._orders),
            "symbols": len(self._symbols),
            "message": "Mock MT4 terminal — no MetaTrader install required",
        }

    def account(self) -> dict[str, Any]:
        self._recalc()
        return {
            "ok": True,
            "login": self._login,
            "server": self._server,
            "currency": self._currency,
            "leverage": self._leverage,
            "balance": self._balance,
            "equity": self._equity,
            "margin": self._margin,
            "free_margin": round(self._equity - self._margin, 2),
            "open_orders": len(self._orders),
        }

    def symbols(self) -> list[dict[str, Any]]:
        return [deepcopy(v) for v in self._symbols.values()]

    def quote(self, symbol: str) -> dict[str, Any]:
        s = self._symbols.get(symbol.upper())
        if not s:
            return {"ok": False, "error": f"unknown symbol {symbol}"}
        # slight synthetic tick
        mid = (s["bid"] + s["ask"]) / 2
        s["bid"] = round(mid - s["point"] * 10, s["digits"])
        s["ask"] = round(mid + s["point"] * 10, s["digits"])
        self._fill_pending_on_cross(s["symbol"])
        tick = {"ok": True, **deepcopy(s), "time": time.time()}
        self._ticks.setdefault(s["symbol"], []).insert(0, tick)
        self._ticks[s["symbol"]] = self._ticks[s["symbol"]][:100]
        return tick

    def ticks(self, symbol: str, limit: int = 20) -> list[dict[str, Any]]:
        sym = symbol.upper()
        n = max(1, min(int(limit), 100))
        return [deepcopy(t) for t in self._ticks.get(sym, [])[:n]]

    def set_quote(self, symbol: str, bid: float, ask: float) -> dict[str, Any]:
        s = self._symbols.get(symbol.upper())
        if not s:
            return {"ok": False, "error": f"unknown symbol {symbol}"}
        s["bid"] = round(float(bid), s["digits"])
        s["ask"] = round(float(ask), s["digits"])
        self._fill_pending_on_cross(s["symbol"])
        return {"ok": True, **deepcopy(s), "time": time.time()}

    def _fill_pending_on_cross(self, symbol: str) -> None:
        q = self._symbols[symbol]
        now = time.time()
        for order in self._orders.values():
            if order["symbol"] != symbol or order["type"] == "market":
                continue
            pending_type = order["type"]
            price = float(order["open_price"])
            should_fill = (
                (pending_type == "buy_limit" and q["ask"] <= price)
                or (pending_type == "sell_limit" and q["bid"] >= price)
                or (pending_type == "buy_stop" and q["ask"] >= price)
                or (pending_type == "sell_stop" and q["bid"] <= price)
            )
            if should_fill:
                order["type"] = "market"
                order["filled_from"] = pending_type
                order["filled_at"] = now
                order["current_price"] = q["bid"] if order["side"] == "buy" else q["ask"]
        self._mark_to_market()

    def orders(self) -> list[dict[str, Any]]:
        self._mark_to_market()
        return [deepcopy(o) for o in self._orders.values()]

    def _mark_to_market(self) -> None:
        for o in self._orders.values():
            if o["type"] != "market":
                continue
            q = self._symbols[o["symbol"]]
            price = q["bid"] if o["side"] == "buy" else q["ask"]
            mult = 100000 if o["symbol"] != "XAUUSD" else 100
            if o["symbol"] == "USDJPY":
                # rough USD profit
                pip_value = o["volume"] * 1000 / price
            else:
                pip_value = o["volume"] * mult * (1 if o["symbol"] != "XAUUSD" else 0.01)
            direction = 1 if o["side"] == "buy" else -1
            o["profit"] = round(direction * (price - o["open_price"]) * pip_value, 2)
            o["current_price"] = price
        self._recalc()

    def order_send(
        self,
        symbol: str,
        side: str,
        volume: float,
        order_type: str = "market",
        price: float | None = None,
        sl: float | None = None,
        tp: float | None = None,
        comment: str = "",
    ) -> dict[str, Any]:
        sym = symbol.upper()
        if sym not in self._symbols:
            return {"ok": False, "error": f"unknown symbol {symbol}"}
        side_l = side.strip().lower()
        if side_l not in {"buy", "sell"}:
            return {"ok": False, "error": "side must be buy or sell"}
        if volume <= 0:
            return {"ok": False, "error": "volume must be > 0"}
        ot = (order_type or "market").strip().lower()
        if ot not in {"market", "buy_limit", "sell_limit", "buy_stop", "sell_stop"}:
            return {"ok": False, "error": f"unsupported order_type {order_type}"}
        q = self._symbols[sym]
        if ot == "market":
            open_price = q["ask"] if side_l == "buy" else q["bid"]
        else:
            if price is None:
                return {"ok": False, "error": "pending order requires price"}
            open_price = float(price)
        ticket = self._next_ticket()
        margin = round(volume * 1000 / max(1, self._leverage / 10), 2)
        order = {
            "ticket": ticket,
            "symbol": sym,
            "side": side_l,
            "volume": float(volume),
            "type": "market" if ot == "market" else ot,
            "open_price": open_price,
            "sl": sl,
            "tp": tp,
            "comment": comment or "mt4-mcp",
            "profit": 0.0,
            "margin": margin,
            "open_time": time.time(),
            "magic": 0,
        }
        self._orders[ticket] = order
        self._mark_to_market()
        return {"ok": True, "ticket": ticket, "order": deepcopy(order)}

    def order_modify(
        self,
        ticket: int,
        price: float | None = None,
        sl: float | None = None,
        tp: float | None = None,
    ) -> dict[str, Any]:
        o = self._orders.get(int(ticket))
        if not o:
            return {"ok": False, "error": f"ticket {ticket} not found"}
        if price is not None and o["type"] != "market":
            o["open_price"] = float(price)
        if sl is not None:
            o["sl"] = float(sl)
        if tp is not None:
            o["tp"] = float(tp)
        return {"ok": True, "order": deepcopy(o)}

    def order_close(self, ticket: int, volume: float | None = None) -> dict[str, Any]:
        o = self._orders.get(int(ticket))
        if not o:
            return {"ok": False, "error": f"ticket {ticket} not found"}
        self._mark_to_market()
        close_vol = float(volume) if volume is not None else float(o["volume"])
        if close_vol <= 0 or close_vol > o["volume"] + 1e-9:
            return {"ok": False, "error": "invalid close volume"}
        q = self._symbols[o["symbol"]]
        close_price = q["bid"] if o["side"] == "buy" else q["ask"]
        # proportional profit if partial
        ratio = close_vol / o["volume"]
        profit = round(float(o["profit"]) * ratio, 2)
        self._balance = round(self._balance + profit, 2)
        hist = {
            "ticket": o["ticket"],
            "symbol": o["symbol"],
            "side": o["side"],
            "volume": close_vol,
            "open_price": o["open_price"],
            "close_price": close_price,
            "profit": profit,
            "comment": o.get("comment", ""),
            "closed_at": time.time(),
        }
        self._history.insert(0, hist)
        if abs(close_vol - o["volume"]) < 1e-9:
            del self._orders[int(ticket)]
        else:
            o["volume"] = round(o["volume"] - close_vol, 2)
            o["margin"] = round(float(o["margin"]) * (1 - ratio), 2)
        self._recalc()
        return {"ok": True, "closed": hist, "balance": self._balance}

    def history(self, limit: int = 20) -> list[dict[str, Any]]:
        n = max(1, min(int(limit), 100))
        return [deepcopy(h) for h in self._history[:n]]
