---
description: How to contribute to VoxelKit — fork, branch, test, and open a pull request.
---

# How to Contribute

First off — thank you for even thinking about contributing. VoxelKit is open-source and genuinely gets better when people use it, find rough edges, and send fixes.

You don't need to add a whole new feature to contribute. Fixing a typo in the docs, adding a missing test, or clarifying an error message are all genuinely useful.

---

## Getting set up locally

```bash
git clone https://github.com/ArsalaanAhmad/VoxelKit.git
cd VoxelKit
pip install -r requirements.txt
```

Run the test suite to make sure everything is green before you start:

```bash
pytest -q
```

Generate the test fixtures if you need sample files to work with:

```bash
python tests/create_fixtures.py
```

Start the API server locally:

```bash
python -m uvicorn app.main:app --reload
```

---

## The workflow

1. **Fork** the repo on GitHub
2. **Create a branch** from `main` — give it a name that describes what you're doing (`fix/nan-warning-message`, `feat/zarr-support`)
3. **Make your changes** — keep them focused. One thing per PR
4. **Run the tests** — add or update tests if you changed behaviour
5. **Open a pull request** with a short summary of what you changed and why

That's it. No CLA, no hoops.

---

## What makes a good PR

- **Focused** — one fix or one feature, not five things at once
- **Tested** — if you changed how something behaves, there should be a test that proves it
- **Documented** — if you added a new CLI flag or Python parameter, update the docs
- **Clean commits** — "fix NaN warning threshold" is better than "stuff"

---

## Project architecture (quick orientation)

VoxelKit is **library-first**:

- `voxelkit/<format>/` — the real logic lives here (inspect, preview, report per format)
- `voxelkit/cli.py` — thin adapter that routes CLI arguments to library functions
- `app/routers/` — thin FastAPI wrappers, same idea as the CLI
- `voxelkit/core/` — shared utilities (validation, types, errors, batch reporting)

**Adding a new file format?**

1. Add `voxelkit/<format>/` with `inspect.py`, `preview.py`, `report.py`
2. Register it in `voxelkit/cli.py` via `register_format(FormatRoute(...))`
3. Add a FastAPI router under `app/routers/` and include it in `app/main.py`
4. Add tests and a fixture file under `tests/`

---

## Code guidelines

- Small, well-scoped functions
- Handle invalid input with clear error messages (use `ValidationError` from `voxelkit.core.errors`)
- No unrelated refactors bundled into a feature PR
- Follow the naming style of the existing code

---

## Pull request checklist

- [ ] Tests added or updated if behaviour changed
- [ ] Docs updated if you added a new parameter, flag, or endpoint
- [ ] No unrelated changes bundled in
- [ ] Commit messages are clear

---

## Questions?

Open an issue — even just to ask. [Reporting Issues →](issues.md)
