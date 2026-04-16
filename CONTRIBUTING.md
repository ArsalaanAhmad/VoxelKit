# Contributing to VoxelKit

Thanks for contributing to VoxelKit.

## Workflow

1. Fork the repository.
2. Create a feature branch from main.
3. Keep your changes focused and atomic.
4. Add or update tests when behavior changes.
5. Open a pull request with a clear summary of what changed and why.

## Local Setup

1. Install dependencies:

```powershell
pip install -r requirements.txt
```

2. Run the API:

```powershell
py -m uvicorn app.main:app --reload
```

3. Run tests:

```powershell
pytest -q
```

## Code Guidelines

- Follow existing project structure and naming style.
- Prefer small, well-scoped functions.
- Handle invalid input with clear error responses.
- Update docs for new endpoints or behavior changes.

## Extending File Formats

When adding a new image format, keep the project library-first:

- Add format logic under `voxelkit/<format>/` (inspect + preview + report).
- Keep `app/routers/` and `voxelkit/cli.py` as thin adapters.
- In `voxelkit/cli.py`, add small adapters and register the format in `_register_builtin_formats()` using `register_format(FormatRoute(...))`.
- Add tests and CLI examples in README for the new format.

## Pull Request Checklist

- Tests added or updated if behavior changed.
- README/API docs updated if needed.
- No unrelated refactors bundled with feature changes.
- Commit messages are clear and descriptive.

## Reporting Issues

When filing an issue, include:

- Expected behavior
- Actual behavior
- Steps to reproduce
- Example input files (if possible)
- Environment details (OS, Python version)
