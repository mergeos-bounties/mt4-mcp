"""Tests for mt4://account MCP resource."""

from mt4_mcp.backend import get_backend, set_mode


def test_account_resource():
    set_mode("mock")
    b = get_backend()
    acct = b.account()
    assert "balance" in acct
    assert "equity" in acct
