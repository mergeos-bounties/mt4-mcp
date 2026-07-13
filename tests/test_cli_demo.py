from typer.testing import CliRunner

from mt4_mcp.cli import app

runner = CliRunner()


def test_version():
    r = runner.invoke(app, ["version"])
    assert r.exit_code == 0
    assert "0.1.0" in r.stdout


def test_demo():
    r = runner.invoke(app, ["demo"])
    assert r.exit_code == 0
    assert "demo complete" in r.stdout


def test_tools_list():
    r = runner.invoke(app, ["tools", "list"])
    assert r.exit_code == 0
    assert "mt4_order_send" in r.stdout


def test_call_account():
    r = runner.invoke(app, ["call", "account"])
    assert r.exit_code == 0
    assert "balance" in r.stdout
