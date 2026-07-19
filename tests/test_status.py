"""Tests for mt4-mcp status (issue #291 / mt4-mcp#2)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "mt4_mcp", *args],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env={"PYTHONPATH": str(REPO_ROOT / "src"), "MT4_MCP_MODE": "mock"},
    )


def test_status_json_has_required_fields():
    """`mt4-mcp status --json` returns mode, balance, equity, open_orders_count."""
    proc = _run("status", "--json")
    assert proc.returncode == 0, f"status failed: {proc.stderr}"
    payload = json.loads(proc.stdout)
    assert payload["mode"] == "mock"
    assert "account" in payload
    assert "balance" in payload["account"]
    assert "equity" in payload["account"]
    assert isinstance(payload["open_orders_count"], int)
    assert payload["open_orders_count"] >= 0


def test_status_balance_is_number():
    """Balance / equity / margin are numeric in mock mode."""
    proc = _run("status", "--json")
    payload = json.loads(proc.stdout)
    acct = payload["account"]
    assert isinstance(acct["balance"], (int, float))
    assert isinstance(acct["equity"], (int, float))


def test_status_open_orders_count_matches():
    """open_orders_count matches len(orders()) on the same backend."""
    proc_status = _run("status", "--json")
    proc_orders = _run("call", "orders")
    assert proc_status.returncode == 0
    assert proc_orders.returncode == 0
    status_payload = json.loads(proc_status.stdout)
    orders_payload = json.loads(proc_orders.stdout)
    assert status_payload["open_orders_count"] == len(orders_payload)


def test_status_with_orders_flag_returns_list():
    """--orders flag adds the open_orders list to the JSON payload."""
    proc = _run("status", "--json", "--orders")
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert "open_orders" in payload
    assert payload["open_orders"] is None or isinstance(payload["open_orders"], list)


def test_status_works_offline_mock():
    """Works fully offline — mock backend does not touch network."""
    proc = _run("status", "--json")
    assert proc.returncode == 0
    assert "Connection" not in proc.stderr  # no network errors
    assert "Traceback" not in proc.stderr
