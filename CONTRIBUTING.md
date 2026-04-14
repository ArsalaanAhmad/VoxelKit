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
