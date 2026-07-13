from mt4_mcp.backend.mock import MockBackend
from mt4_mcp.config import set_mode
from mt4_mcp.backend import get_backend


def test_seed_account_and_symbols():
    b = MockBackend()
    s = b.seed_demo()
    assert s["ok"] is True
    acc = b.account()
    assert acc["balance"] == 10000.0
    syms = b.symbols()
    assert any(x["symbol"] == "EURUSD" for x in syms)


def test_order_roundtrip():
    b = MockBackend()
    b.seed_demo()
    sent = b.order_send("EURUSD", "buy", 0.1, "market")
    assert sent["ok"] is True
    ticket = sent["ticket"]
    orders = b.orders()
    assert any(o["ticket"] == ticket for o in orders)
    mod = b.order_modify(ticket, sl=1.08, tp=1.09)
    assert mod["ok"] is True
    closed = b.order_close(ticket)
    assert closed["ok"] is True
    assert b.history(5)
    assert not any(o["ticket"] == ticket for o in b.orders())


def test_pending_requires_price():
    b = MockBackend()
    b.seed_demo()
    bad = b.order_send("EURUSD", "buy", 0.1, "buy_limit")
    assert bad["ok"] is False
    ok = b.order_send("EURUSD", "buy", 0.1, "buy_limit", price=1.08)
    assert ok["ok"] is True


def test_get_backend_mock():
    set_mode("mock")
    assert get_backend().name == "mock"


def test_doctor_ok():
    b = MockBackend()
    d = b.doctor()
    assert d["ok"] is True
    assert d["connected"] is True
