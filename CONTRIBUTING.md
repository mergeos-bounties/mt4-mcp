# Contributing to mt4-mcp

Thanks for contributing! This guide covers local setup, running tests, and the
MergeOS bounty claim flow.

---

## 1. Setup

### Prerequisites

- **Python 3.11+** ([download](https://www.python.org/downloads/))
- **Git**
- (optional) [uv](https://docs.astral.sh/uv/) — the repo ships a `uv.lock`

### Clone & install

```bash
git clone https://github.com/mergeos-bounties/mt4-mcp.git
cd mt4-mcp
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

The dev extra installs `pytest` and `ruff`.

### Verify the install

```bash
mt4-mcp version
mt4-mcp status
mt4-mcp demo
```

All three should run with **no MetaTrader install** — default mode is an offline
**mock** (`MT4_MCP_MODE=mock`).

### Project layout

| Path | Purpose |
| --- | --- |
| `src/mt4_mcp/` | Python package (CLI, MCP server, backend) |
| `tests/` | Pytest suite |
| `docs/` | Setup, live-bridge, and mock-trading guides |
| `examples/` | MCP host config samples (Claude, Cursor, env) |
| `.github/workflows/ci.yml` | CI: ruff → pytest → demo |

---

## 2. Tests

### Run the suite

```bash
ruff check src tests
pytest -q
mt4-mcp demo
```

- **pytest** — full offline suite; no broker or terminal needed.
- **ruff** — lint (line-length 100, target `py311`).
- **demo** — end-to-end smoke of core backend APIs.

### What the tests cover

| File | Area |
| --- | --- |
| `test_cli_demo.py` | CLI commands (`version`, `status`, `demo`, `tools list`, `call`) |
| `test_mock_backend.py` | Mock backend — account, quotes, orders, history |
| `test_live_backend.py` | Live-bridge error handling (no bridge → structured errors) |
| `test_account_resource.py` | Account resource model |
| `test_server_tools.py` | MCP tool registration & behavior |

### Adding a test

1. Create `tests/test_<area>.py`.
2. Use `typer.testing.CliRunner` for CLI tests; call backend functions directly
   for unit tests.
3. Keep tests **offline** — mock mode only, no live bridge.

---

## 3. Claim flow (MergeOS bounties)

mt4-mcp is part of the [MergeOS](https://github.com/mergeos-bounties) bounty
ecosystem. Paid bounties are denominated in **MRG** and claimed via pull
request.

### How to claim a bounty

1. **Star** the repository (required by the claim protocol).
2. **Find an open bounty issue** — look for issues labeled `bounty` with an MRG
   amount, e.g. `[25 MRG]`.
3. **Comment to claim** — post `I claim this bounty` (or the issue's specified
   claim phrase) so maintainers can assign it.
4. **Fork** the repo and create a branch from `master`:
   ```bash
   git checkout -b feat/<short-description>
   ```
5. **Implement** the feature/fix described in the issue.
6. **Add or update tests** covering your change.
7. **Run the full suite** (ruff + pytest + demo) and make sure it passes.
8. **Push to your fork** and open a PR against `mergeos-bounties/mt4-mcp`
   `master`.
9. **Reference the issue** — put `Fixes #<number>` in the PR body.

### Acceptance criteria

Every bounty issue lists its own acceptance criteria. Common ones:

- [ ] Works in offline **mock** mode
- [ ] Tests added / updated and passing
- [ ] README / docs updated if behavior changed
- [ ] PR targets `master` with `Fixes #<issue>`

### Reward

Once the PR is merged, the maintainer credits the bounty in **MRG** per the
repo's [BOUNTY-POLICY](https://github.com/mergeos-bounties/mergeos/blob/master/BOUNTY-POLICY.md).

---

## 4. Pull-request checklist

- [ ] Branch is up to date with `upstream/master`
- [ ] `ruff check src tests` passes
- [ ] `pytest -q` passes
- [ ] `mt4-mcp demo` runs clean
- [ ] No secrets / `.env` committed
- [ ] PR body references the issue (`Fixes #<number>`)

---

## 5. Questions?

Open a [GitHub issue](https://github.com/mergeos-bounties/mt4-mcp/issues) for
bugs or feature requests. For bounty-specific questions, comment on the bounty
issue itself.