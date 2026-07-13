from __future__ import annotations

from mt4_mcp.config import max_volume, symbol_allowlist


def validate_live_order(symbol: str, volume: float) -> dict[str, object]:
    sym = symbol.upper()
    allowed_symbols = symbol_allowlist()
    if allowed_symbols and sym not in allowed_symbols:
        return {
            "ok": False,
            "error": (
                f"symbol {sym} is not allowed by MT4_MCP_SYMBOL_ALLOWLIST "
                f"({', '.join(sorted(allowed_symbols))})"
            ),
        }

    cap = max_volume()
    if cap is not None and float(volume) > cap:
        return {
            "ok": False,
            "error": f"volume {volume:g} exceeds MT4_MCP_MAX_VOLUME {cap:g}",
        }

    return {"ok": True}
