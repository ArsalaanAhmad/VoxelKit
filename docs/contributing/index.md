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

## Project architecture

VoxelKit is **library-first**. Everything you can do with the CLI or the REST API maps to a Python function that lives in `voxelkit/`. The CLI and the API are thin adapters over those functions — they translate `argparse.Namespace` (or a FastAPI request) into kwargs and call straight through. Hold onto that mental model and the rest of the layout falls into place.

### Repository layout

```
VoxelKit/
├── voxelkit/                     # the Python library (the source of truth)
│   ├── __init__.py               # public API: inspect_file, preview_file, report_file, …
│   ├── cli.py                    # CLI: argparse + FormatRoute dispatch
│   ├── core/                     # cross-format building blocks (no format logic here)
│   │   ├── errors.py             #   ValidationError, UnsupportedFormatError
│   │   ├── formats.py            #   extension lists, detect_format(), DICOM series sniffing
│   │   ├── handler.py            #   InspectFn/PreviewFn/ReportFn Protocols + arity validator
│   │   ├── image_utils.py        #   uint8 array -> PNG bytes
│   │   ├── normalization.py      #   float slice -> uint8 (windowing)
│   │   ├── report.py             #   build_array_report(): the shared QA stats helper
│   │   ├── batch_report.py       #   directory walker + per-file dispatch
│   │   ├── html_report.py        #   self-contained HTML report with thumbnails
│   │   ├── types.py              #   TypedDict definitions for every public return type
│   │   └── validation.py         #   require_supported_extension, resolve_slice_index, …
│   ├── nifti/, h5/, npy/, tiff/  # one subpackage per format
│   │   ├── inspect.py            #   metadata-only read
│   │   ├── preview.py            #   pixel data -> 2-D PNG bytes (or uint8 array)
│   │   └── report.py             #   pixel data -> FileReportResult
│   ├── dicom/                    # DICOM is a little richer than other formats
│   │   ├── loader.py             #   load .dcm OR series directory into one LoadedDicom
│   │   ├── phi.py                #   PHI tag list + in-place scrub
│   │   ├── inspect.py            #   metadata, PHI-stripped by default
│   │   ├── preview.py / report.py
│   │   ├── anonymise.py          #   directory-tree PHI scrub
│   │   └── convert.py            #   DICOM -> NIfTI (affine + LPS->RAS flip)
│   ├── embedding/                # 2-D feature matrix QA (separate from build_array_report)
│   ├── gui/                      # optional Streamlit launcher
│   └── templates/                # contributor copy-paste skeletons
│       └── format_template.py    #   start here when adding a new format
├── app/                          # FastAPI server (optional, mirrors the CLI surface)
│   ├── main.py                   #   app + router includes
│   └── routers/                  #   one router per format/feature
├── tests/                        # pytest suite + synthetic fixtures
│   ├── create_fixtures.py        #   regenerates tests/fixtures/ deterministically
│   ├── fixtures/                 #   tiny synthetic files — no real patient data, ever
│   └── test_*_feature.py         #   one file per feature
├── docs/                         # the docs site (MkDocs Material) you're reading now
├── hooks/                        # MkDocs build hooks (sitemap rename, …)
└── pyproject.toml                # deps + package config
```

### The three layers (library / CLI / API)

Every supported format is exposed through the same three callables:

```
inspect(file_path: str)                                       -> dict
preview(file_path: str, **format_specific_kwargs)             -> bytes | np.ndarray
report(file_path: str, **format_specific_kwargs)              -> FileReportResult
```

These live inside the format subpackage (`voxelkit/<format>/inspect.py`, etc.). They take **format-specific keyword arguments** — e.g. NIfTI's `plane="axial"`, HDF5's `dataset_path=...`, DICOM's `include_phi=False`. They're the canonical implementation.

Both the CLI and the REST API call those library functions. They differ only in how they collect their arguments:

- **CLI** (`voxelkit/cli.py`) — argparse parses flags into an `argparse.Namespace`. Per-format **adapter functions** (`_preview_nifti`, `_preview_dicom`, …) translate that Namespace into the library function's kwargs and reject flags that do not apply to this format. Adapters all share the same `(file_path: str, args: argparse.Namespace) -> bytes | dict` signature — that's what the Protocol in `core/handler.py` pins down.
- **REST API** (`app/routers/<format>.py`) — FastAPI's pydantic models parse query/body params. The router calls the library function directly. No adapter needed because FastAPI is doing the equivalent translation.

Public top-level dispatchers in `voxelkit/__init__.py` (`inspect_file`, `preview_file`, `report_file`, `report_batch`) auto-detect the format from the path and forward to the right library function. **This is what most Python users call** — they don't import the per-format functions unless they need something specific.

### The `FormatRoute` pattern

`voxelkit/cli.py` keeps a registry of `FormatRoute` objects — one per supported format — and the CLI dispatcher (`_resolve_route`) looks one up based on the file extension (or directory contents, for DICOM series). A route is just:

```python
FormatRoute(
    name="nifti",
    extensions=NIFTI_EXTENSIONS,
    inspect_fn=_inspect_nifti,   # CLI adapter, NOT the library inspect()
    preview_fn=_preview_nifti,
    report_fn=_report_nifti,
)
```

The three callables must conform to the `InspectFn` / `PreviewFn` / `ReportFn` Protocols in `voxelkit.core.handler`. `FormatRoute.__post_init__` runs `validate_handler_signatures()` to arity-check them at registration time, so a typo'd signature blows up at import — not when a user runs the CLI.

This is the extension point. To add a new format, you do not modify the dispatcher — you add a new `register_format(FormatRoute(...))` call.

### Why it's split this way

A few decisions repeat across the codebase. Knowing the reasoning helps avoid bikeshedding.

- **Library-first instead of CLI-first.** Most imaging tools are CLI utilities with a tacked-on Python wrapper. VoxelKit inverts that: the CLI exists to make the library convenient from a shell, and the API exists to make it convenient over HTTP. Pixel-touching logic always lives in the library; new features are written there first.
- **Cross-format helpers live in `core/`, format-specific code never does.** `core/report.py::build_array_report` computes min/max/mean/std/NaN/Inf/zero-fraction for any numpy array; every format's `report.py` is just a few lines that load the pixels and call into it. This keeps the warning catalogue consistent across formats — a "constant array" warning means the same thing on a NIfTI as on a DICOM.
- **TypedDicts for every public return shape.** `core/types.py` is the authoritative schema. Tools that consume VoxelKit output (the GUI, downstream pipelines, the API) can rely on a stable shape per format without importing format-specific modules.
- **Adapter signatures, not "smart" library functions.** The library functions take keyword arguments like `dataset_path=...` and `plane=...`. The CLI adapters do the translation from `args.dataset` and `args.plane`. We deliberately do *not* pass `argparse.Namespace` into the library — that would couple a generic Python API to the CLI's argument schema.
- **Synthetic test fixtures, never real data.** Everything under `tests/fixtures/` is built by `tests/create_fixtures.py`. The DICOM fixtures look like they have PHI but the values are all literal strings like `"Test^Patient"`. This is non-negotiable, especially for DICOM.

### Adding a new file format

There's a worked skeleton at [`voxelkit/templates/format_template.py`](https://github.com/ArsalaanAhmad/VoxelKit/blob/main/voxelkit/templates/format_template.py) — copy it, rename, and follow the seven numbered steps inside. The short version:

1. Add `voxelkit/<format>/` with `inspect.py`, `preview.py`, `report.py`. Re-export them from `voxelkit/<format>/__init__.py`.
2. Add `<FORMAT>_EXTENSIONS` and a branch to `detect_format()` in `voxelkit/core/formats.py`. Append to `SUPPORTED_DATA_EXTENSIONS` and the `FormatName` literal.
3. Write three small CLI adapter functions in `voxelkit/cli.py` (`_inspect_<format>`, `_preview_<format>`, `_report_<format>`) that conform to the Protocols in `voxelkit.core.handler`. Reject flags that only apply to other formats with `ValidationError("--foo is only valid for X.")`.
4. Register the route in `_register_builtin_formats()` with `register_format(FormatRoute(...))`.
5. Wire library-level dispatch in `voxelkit/__init__.py` — add a branch to each of `inspect_file`, `preview_file`, `report_file`. Add the format-specific functions to `__all__`.
6. (Optional) Add a FastAPI router under `app/routers/<format>.py` and include it in `app/main.py`.
7. Add a fixture generator in `tests/create_fixtures.py` (synthetic — no real data) and a `tests/test_<format>_feature.py` covering inspect / preview / report and the CLI dispatch path. Update docs under `docs/cli/`, `docs/library/`, and `mkdocs.yml`'s nav.

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
