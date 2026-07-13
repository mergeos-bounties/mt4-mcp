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


def main() -> None:
    app()


if __name__ == "__main__":
    app()
