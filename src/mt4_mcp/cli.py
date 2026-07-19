from __future__ import annotations

import json
from typing import Any, Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from mt4_mcp import __version__
from mt4_mcp.backend import get_backend, switch_mode
from mt4_mcp.config import get_mode, set_mode

app = typer.Typer(help="mt4-mcp — MCP server for MetaTrader 4", no_args_is_help=True)
tools_app = typer.Typer(help="List / probe tools")
app.add_typer(tools_app, name="tools")
console = Console()

TOOL_NAMES = [
    "mt4_mode",
    "mt4_doctor",
    "mt4_seed_demo",
    "mt4_account",
    "mt4_symbols",
    "mt4_quote",
    "mt4_ticks",
    "mt4_orders",
    "mt4_order_send",
    "mt4_order_modify",
    "mt4_order_close",
    "mt4_history",
]


@app.command("version")
def version_cmd() -> None:
    rprint({"version": __version__, "mode": get_mode()})


@app.command("doctor")
def doctor_cmd() -> None:
    b = get_backend()
    info = b.doctor()
    info["mt4_mcp_version"] = __version__
    info["mode"] = get_mode()
    rprint(info)


@app.command("status")
def status_cmd() -> None:
    """Print mode, balance, equity, and open order count."""
    account = get_backend().account()
    status = {
        "mode": get_mode(),
        "balance": account.get("balance"),
        "equity": account.get("equity"),
        "open_orders": account.get("open_orders"),
        "version": __version__,
    }
    rprint(status)


@app.command("demo")
def demo_cmd() -> None:
    """Offline smoke: seed mock account and place/close a tiny trade."""
    set_mode("mock")
    b = get_backend()
    rprint(b.seed_demo())
    rprint(b.doctor())
    rprint({"account": b.account()})
    rprint({"quote": b.quote("EURUSD")})
    sent = b.order_send("EURUSD", "buy", 0.10, "market", sl=1.0800, tp=1.0900, comment="demo")
    rprint({"order_send": sent})
    rprint({"orders": b.orders()})
    ticket = int(sent["ticket"])
    rprint({"modify": b.order_modify(ticket, sl=1.0810, tp=1.0890)})
    rprint({"close": b.order_close(ticket)})
    rprint({"history": b.history(5)})
    rprint({"account_after": b.account()})
    rprint("mt4-mcp demo complete (mock).")


@tools_app.command("list")
def tools_list() -> None:
    table = Table(title="mt4-mcp tools")
    table.add_column("Tool")
    for n in TOOL_NAMES:
        table.add_row(n)
    console.print(table)


@app.command("call")
def call_cmd(
    tool: str = typer.Argument(..., help="Short name e.g. account or mt4_account"),
    arg: Optional[list[str]] = typer.Argument(None, help="key=value pairs"),
) -> None:
    """One-shot mock/live tool call without MCP host."""
    b = get_backend()
    name = tool if tool.startswith("mt4_") else f"mt4_{tool}"
    kv: dict[str, Any] = {}
    for a in arg or []:
        if "=" in a:
            k, v = a.split("=", 1)
            try:
                kv[k] = json.loads(v)
            except json.JSONDecodeError:
                kv[k] = v

    dispatch = {
        "mt4_mode": lambda: switch_mode(str(kv.get("mode", get_mode()))),
        "mt4_doctor": b.doctor,
        "mt4_seed_demo": b.seed_demo,
        "mt4_account": b.account,
        "mt4_symbols": b.symbols,
        "mt4_quote": lambda: b.quote(str(kv.get("symbol", "EURUSD"))),
        "mt4_ticks": lambda: b.ticks(
            str(kv.get("symbol", "EURUSD")),
            int(kv.get("limit", 20)),
        ),
        "mt4_orders": b.orders,
        "mt4_order_send": lambda: b.order_send(
            str(kv.get("symbol", "EURUSD")),
            str(kv.get("side", "buy")),
            float(kv.get("volume", 0.1)),
            str(kv.get("order_type", "market")),
            kv.get("price"),
            kv.get("sl"),
            kv.get("tp"),
            str(kv.get("comment", "")),
        ),
        "mt4_order_modify": lambda: b.order_modify(
            int(kv.get("ticket", 0)),
            kv.get("price"),
            kv.get("sl"),
            kv.get("tp"),
        ),
        "mt4_order_close": lambda: b.order_close(
            int(kv.get("ticket", 0)),
            float(kv["volume"]) if "volume" in kv else None,
        ),
        "mt4_history": lambda: b.history(int(kv.get("limit", 20))),
    }
    if name not in dispatch:
        raise typer.BadParameter(f"unknown tool {name}")
    rprint(dispatch[name]())


@app.command("serve")
def serve_cmd() -> None:
    """Run MCP server over stdio."""
    from mt4_mcp.server import run_stdio

    run_stdio()

"""
mt4-mcp status — V0.11.G.7 老板下单

Task: #291 / mergeos-bounties/mt4-mcp #2
Reward: 25 MRG
Goal: `mt4-mcp status` prints mode, balance, equity, open order count.
Acceptance:
  - [x] Works offline mock
  - [x] Test (tests/test_status.py)
  - [x] README updated

This adds ONE command: `mt4-mcp status` that:
  - Resolves current mode (mock|live)
  - Pulls account().balance / account().equity
  - Counts len(orders()) for open orders
  - Renders a clean Rich table when stdout is a TTY,
    falls back to JSON when --json or non-TTY (CI-friendly).
"""


def _fmt_money(value: float | int | None, currency: str = "USD") -> str:
    if value is None:
        return "—"
    try:
        return f"{float(value):,.2f} {currency}"
    except (TypeError, ValueError):
        return f"{value} {currency}"


@app.command("status")
def status_cmd(
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Emit JSON (default for non-TTY / CI / piping).",
    ),
    show_orders: bool = typer.Option(
        False,
        "--orders",
        help="Also list the open orders (off by default to keep status compact).",
    ),
) -> None:
    """Print mode, balance, equity, and open-order count."""
    backend = get_backend()
    mode = get_mode()
    account = backend.account()
    orders = backend.orders()

    payload = {
        "mt4_mcp_version": __version__,
        "mode": mode,
        "backend": getattr(backend, "name", mode),
        "account": {
            "login": account.get("login"),
            "server": account.get("server"),
            "currency": account.get("currency", "USD"),
            "leverage": account.get("leverage"),
            "balance": account.get("balance"),
            "equity": account.get("equity"),
            "margin": account.get("margin"),
            "free_margin": account.get("free_margin"),
            "margin_level": account.get("margin_level"),
        },
        "open_orders_count": len(orders),
        "open_orders": orders if show_orders else None,
    }

    # Auto-pick JSON when not a TTY (so CI / pipelines get machine-readable output)
    use_json = json_output or not sys.stdout.isatty()

    if use_json:
        typer.echo(json.dumps(payload, indent=2, default=str))
        return

    table = Table(title=f"mt4-mcp status — mode={mode}")
    table.add_column("Field", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")

    acct = payload["account"]
    table.add_row("version", __version__)
    table.add_row("mode", mode)
    table.add_row("backend", payload["backend"])
    table.add_row("login", str(acct["login"]))
    table.add_row("server", str(acct["server"]))
    table.add_row("currency", str(acct["currency"]))
    table.add_row("leverage", str(acct["leverage"]))
    table.add_row("balance", _fmt_money(acct["balance"], acct["currency"]))
    table.add_row("equity", _fmt_money(acct["equity"], acct["currency"]))
    table.add_row("margin", _fmt_money(acct["margin"], acct["currency"]))
    table.add_row("free_margin", _fmt_money(acct["free_margin"], acct["currency"]))
    table.add_row("margin_level", str(acct["margin_level"]))
    table.add_row("open_orders_count", str(payload["open_orders_count"]))

    console.print(table)

    if show_orders and orders:
        orders_table = Table(title=f"Open orders ({len(orders)})")
        orders_table.add_column("ticket", style="magenta")
        orders_table.add_column("symbol", style="cyan")
        orders_table.add_column("side", style="yellow")
        orders_table.add_column("volume", justify="right")
        orders_table.add_column("price", justify="right")
        for o in orders:
            orders_table.add_row(
                str(o.get("ticket", "")),
                str(o.get("symbol", "")),
                str(o.get("side", "")),
                f"{o.get('volume', 0):.2f}",
                f"{o.get('price_open', o.get('price', 0)):.5f}",
            )
        console.print(orders_table)



def main() -> None:
    app()


if __name__ == "__main__":
    app()
