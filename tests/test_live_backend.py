from mt4_mcp.backend.live import LiveBackend


def test_live_order_symbol_allowlist(monkeypatch):
    monkeypatch.setenv("MT4_MCP_SYMBOL_ALLOWLIST", "EURUSD, XAUUSD")
    monkeypatch.delenv("MT4_MCP_MAX_VOLUME", raising=False)

    denied = LiveBackend().order_send("GBPUSD", "buy", 0.1)

    assert denied["ok"] is False
    assert "MT4_MCP_SYMBOL_ALLOWLIST" in denied["error"]


def test_live_order_max_volume(monkeypatch):
    monkeypatch.delenv("MT4_MCP_SYMBOL_ALLOWLIST", raising=False)
    monkeypatch.setenv("MT4_MCP_MAX_VOLUME", "0.25")

    denied = LiveBackend().order_send("EURUSD", "buy", 0.3)

    assert denied["ok"] is False
    assert "MT4_MCP_MAX_VOLUME" in denied["error"]


def test_live_order_policy_passes_to_backend_unavailable(monkeypatch):
    monkeypatch.setenv("MT4_MCP_SYMBOL_ALLOWLIST", "EURUSD")
    monkeypatch.setenv("MT4_MCP_MAX_VOLUME", "0.25")

    result = LiveBackend().order_send("EURUSD", "buy", 0.1)

    assert result["ok"] is False
    assert result["error"] == "live backend not connected"
