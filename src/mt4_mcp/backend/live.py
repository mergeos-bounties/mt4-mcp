"""Optional live bridge to a MetaTrader 4 expert / gateway."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen

from mt4_mcp.config import bridge_file, bridge_url


class LiveBackend:
    name = "live"

    def doctor(self) -> dict[str, Any]:
        url = bridge_url()
        path = bridge_file()
        if url:
            try:
                req = Request(url.rstrip("/") + "/health", method="GET")
                with urlopen(req, timeout=2) as resp:  # noqa: S310
                    body = resp.read().decode("utf-8", errors="replace")
                return {
                    "ok": True,
                    "mode": "live",
                    "terminal": "MetaTrader 4 (bridge)",
                    "connected": True,
                    "bridge": url,
                    "health": body[:500],
                }
            except (URLError, TimeoutError, OSError) as e:
                return {
                    "ok": False,
                    "mode": "live",
                    "connected": False,
                    "bridge": url,
                    "error": str(e),
                    "message": "Live bridge URL not reachable",
                }
        if path and Path(path).is_file():
            return {
                "ok": True,
                "mode": "live",
                "connected": True,
                "bridge_file": path,
                "message": "Bridge file present (EA must write responses)",
            }
        return {
            "ok": False,
            "mode": "live",
            "connected": False,
            "message": (
                "No live bridge. Set MT4_MCP_BRIDGE_URL or MT4_MCP_BRIDGE_FILE, "
                "or use mock mode."
            ),
        }

    def seed_demo(self) -> dict[str, Any]:
        return {"ok": False, "error": "seed_demo is mock-only"}

    def _unavailable(self, op: str) -> dict[str, Any]:
        d = self.doctor()
        if d.get("connected"):
            return {
                "ok": False,
                "error": f"live {op} not implemented for this bridge yet",
                "doctor": d,
            }
        return {"ok": False, "error": "live backend not connected", "doctor": d}

    def account(self) -> dict[str, Any]:
        return self._unavailable("account")

    def symbols(self) -> list[dict[str, Any]]:
        return []

    def quote(self, symbol: str) -> dict[str, Any]:
        return self._unavailable("quote")

    def ticks(self, symbol: str, limit: int = 20) -> list[dict[str, Any]]:
        return []

    def orders(self) -> list[dict[str, Any]]:
        return []

    def order_send(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self._unavailable("order_send")

    def order_modify(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self._unavailable("order_modify")

    def order_close(self, *args: Any, **kwargs: Any) -> dict[str, Any]:
        return self._unavailable("order_close")

    def history(self, limit: int = 20) -> list[dict[str, Any]]:
        return []
