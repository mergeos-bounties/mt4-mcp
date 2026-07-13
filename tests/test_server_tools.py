from mt4_mcp.server import (
    mt4_account,
    mt4_doctor,
    mt4_order_send,
    mt4_seed_demo,
)


def test_tools_json():
    assert "mock" in mt4_doctor()
    assert "ok" in mt4_seed_demo()
    assert "balance" in mt4_account()
    r = mt4_order_send("EURUSD", "sell", 0.05)
    assert "ticket" in r or "ok" in r
