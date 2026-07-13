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


def test_pending_buy_limit_fills_on_quote_cross():
    b = MockBackend()
    b.seed_demo()
    pending = b.order_send("EURUSD", "buy", 0.1, "buy_limit", price=1.08)
    ticket = pending["ticket"]

    b.set_quote("EURUSD", bid=1.0798, ask=1.0800)
    order = next(o for o in b.orders() if o["ticket"] == ticket)

    assert order["type"] == "market"
    assert order["open_price"] == 1.08
    assert order["filled_from"] == "buy_limit"


def test_pending_sell_stop_fills_on_quote_cross():
    b = MockBackend()
    b.seed_demo()
    pending = b.order_send("EURUSD", "sell", 0.1, "sell_stop", price=1.08)
    ticket = pending["ticket"]

    b.set_quote("EURUSD", bid=1.0800, ask=1.0802)
    order = next(o for o in b.orders() if o["ticket"] == ticket)

    assert order["type"] == "market"
    assert order["open_price"] == 1.08
    assert order["filled_from"] == "sell_stop"


def test_tick_history_buffer():
    b = MockBackend()
    b.seed_demo()
    first = b.quote("EURUSD")
    second = b.quote("EURUSD")

    ticks = b.ticks("EURUSD", limit=2)

    assert len(ticks) == 2
    assert ticks[0]["time"] == second["time"]
    assert ticks[1]["time"] == first["time"]
    assert all(t["symbol"] == "EURUSD" for t in ticks)
    assert b.ticks("EURUSD", limit=1)[0]["time"] == second["time"]


def test_get_backend_mock():
    set_mode("mock")
    assert get_backend().name == "mock"


def test_doctor_ok():
    b = MockBackend()
    d = b.doctor()
    assert d["ok"] is True
    assert d["connected"] is True
