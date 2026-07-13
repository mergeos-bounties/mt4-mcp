from __future__ import annotations

import os
from typing import Literal

Mode = Literal["mock", "live"]
_PREFIX = "MT4_MCP"


def get_mode() -> Mode:
    raw = (os.environ.get(f"{_PREFIX}_MODE") or "mock").strip().lower()
    return "live" if raw == "live" else "mock"


def set_mode(mode: str) -> Mode:
    m: Mode = "live" if mode.strip().lower() == "live" else "mock"
    os.environ[f"{_PREFIX}_MODE"] = m
    return m


def bridge_url() -> str | None:
    v = (os.environ.get(f"{_PREFIX}_BRIDGE_URL") or "").strip()
    return v or None


def bridge_file() -> str | None:
    v = (os.environ.get(f"{_PREFIX}_BRIDGE_FILE") or "").strip()
    return v or None


def symbol_allowlist() -> set[str]:
    raw = os.environ.get(f"{_PREFIX}_SYMBOL_ALLOWLIST") or ""
    return {item.strip().upper() for item in raw.split(",") if item.strip()}


def max_volume() -> float | None:
    raw = (os.environ.get(f"{_PREFIX}_MAX_VOLUME") or "").strip()
    if not raw:
        return None
    try:
        value = float(raw)
    except ValueError:
        return None
    return value if value > 0 else None
