# VoxelKit

![VoxelKit banner](assets/voxelkit_github_banner.svg)

[![Python](https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PyPI version](https://img.shields.io/pypi/v/voxelkit.svg)](https://pypi.org/project/voxelkit/)
[![FastAPI](https://img.shields.io/badge/FastAPI-thin%20wrapper-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Formats](https://img.shields.io/badge/formats-NIfTI%20%7C%20HDF5%20%7C%20NumPy%20%7C%20TIFF-5A67D8)](#supported-formats)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-2EA44F)](#roadmap)

VoxelKit helps you inspect, preview, and QA-check multidimensional imaging files from one consistent CLI and Python API.

## Quick CLI Demo

```powershell
# Inspect structure/metadata
python -m voxelkit.cli inspect tests/fixtures/sample_nested.h5

# Generate a PNG preview slice
python -m voxelkit.cli preview tests/fixtures/sample_3d.nii.gz --plane axial --slice 4 --output nifti_preview.png

# Run per-file QA stats + warnings
python -m voxelkit.cli report tests/fixtures/sample_nested.h5 --dataset data/subject01/run1/bold

# Run directory-level QA summary
python -m voxelkit.cli report-batch tests/fixtures --output batch_report.json
```

## Why VoxelKit?

Low-level libraries like `nibabel`, `h5py`, and `tifffile` are powerful and flexible. VoxelKit does not replace them.

Instead, VoxelKit provides a unified workflow on top for day-to-day dataset triage:

- inspect file structure and metadata quickly
- preview representative slices as PNGs
- generate QA stats and warnings for suspicious arrays
- summarize QA signals across whole directories with `report-batch`

This keeps common inspection and QA tasks fast, scriptable, and consistent across formats.

## Supported Formats

- NIfTI (`.nii`, `.nii.gz`)
- HDF5 (`.h5`, `.hdf5`)
- NumPy arrays (`.npy`, `.npz`)
- TIFF (`.tif`, `.tiff`) in format routing (full inspect/preview/report coverage is in progress)

## Installation

Editable install (recommended while iterating on the project):

```powershell
cd VoxelKit
pip install -e .
```

Optional dependencies used by demos/tests:

```powershell
pip install -r requirements.txt
```

When a PyPI release is available, installation will be:

```powershell
pip install voxelkit
```

## Python Usage

```python
from voxelkit import inspect_file, preview_file, report_file, report_batch

# Inspect
info = inspect_file("tests/fixtures/sample_nested.h5")

# Preview (returns PNG bytes)
png = preview_file(
    "tests/fixtures/sample_3d.nii.gz",
    plane="axial",
    slice_index=4,
)
with open("nifti_preview.png", "wb") as f:
    f.write(png)

# Single-file QA report
single_report = report_file(
    "tests/fixtures/sample_nested.h5",
    dataset_path="data/subject01/run1/bold",
)

# Batch QA report
batch = report_batch("tests/fixtures", recursive=True)
```

## Visual Demos

Add screenshots/snippets here so visitors can see value in under 30 seconds:

- Terminal screenshot: `inspect` and `report` output side by side
- Preview image: one generated PNG slice (`nifti_preview.png` or `h5_preview.png`)
- Batch report snippet: short JSON excerpt showing `files_with_warnings` and `warning_counts`

## Run The API

```powershell
py -m uvicorn app.main:app --reload
```

Open API docs:

- Swagger UI: `http://127.0.0.1:8000/docs`

## Optional Local GUI

VoxelKit includes an optional Streamlit prototype for local/offline inspect, report, and preview workflows.
The GUI runs entirely on your machine and does not upload files to external services.

Install optional GUI extras:

```powershell
pip install -e .[gui]
```

Launch the GUI:

```powershell
voxelkit gui
```

If Streamlit is not installed, the CLI prints:

```text
Install GUI extras with: pip install voxelkit[gui]
```

## API Endpoints

- `POST /h5/inspect`
- `POST /h5/slice`
- `POST /nifti/metadata`
- `POST /nifti/preview`
- `GET /health`

## API Usage Examples

### NIfTI Metadata

```bash
curl -X POST "http://127.0.0.1:8000/nifti/metadata" \
	-F "file=@tests/fixtures/sample_3d.nii.gz"
```

### NIfTI Preview

```bash
curl -X POST "http://127.0.0.1:8000/nifti/preview?plane=axial&slice_index=4" \
	-F "file=@tests/fixtures/sample_3d.nii.gz" \
	--output nifti_preview.png
```

### HDF5 Inspect

```bash
curl -X POST "http://127.0.0.1:8000/h5/inspect" \
	-F "file=@tests/fixtures/sample_nested.h5"
```

### HDF5 Slice

```bash
curl -X POST "http://127.0.0.1:8000/h5/slice?dataset_path=data/subject01/run1/bold&axis=2&slice_index=3" \
	-F "file=@tests/fixtures/sample_nested.h5" \
	--output h5_preview.png
```

## Project Layout

```text
voxelkit/
  core/      # shared cross-format utilities (validation, types, errors, normalization)
  h5/        # HDF5 inspect/preview logic
  nifti/     # NIfTI metadata/preview logic

app/
  routers/   # thin FastAPI wrappers over voxelkit library functions
```

## Test Fixtures

Generate tiny deterministic fixtures for local testing/demo:

```powershell
py tests/create_fixtures.py
```

This creates:

- `tests/fixtures/sample_3d.nii.gz`: small 3D NIfTI volume
- `tests/fixtures/sample_2d.h5`: 2D HDF5 dataset at `image`
- `tests/fixtures/sample_3d.h5`: 3D HDF5 dataset at `volume`
- `tests/fixtures/sample_nested.h5`: nested HDF5 dataset at `data/subject01/run1/bold`

## Running Tests

```powershell
pytest -q
```

## Extending CLI Formats

The CLI in `voxelkit/cli.py` is registry-based and intentionally thin.

To add a new image format later (for example, GeoTIFF):

1. Implement library functions in a format module (inspect + preview bytes).
2. Implement a format report function in the format module.
3. Add small CLI adapters in `voxelkit/cli.py` that map CLI args into preview/report functions.
4. Register the format in `_register_builtin_formats()` with `register_format(FormatRoute(...))`.
5. Add any new format-specific CLI flags in `build_parser()` only if needed.

Minimal registration pattern:

```python
register_format(
	FormatRoute(
		name="geotiff",
		extensions=(".tif", ".tiff"),
		inspect_fn=inspect_geotiff,
		preview_fn=_preview_geotiff,
		report_fn=_report_geotiff,
	)
)
```

This keeps CLI routing simple while all format behavior remains in the library layer.

## Roadmap

- multi-file request support
- CI for tests
- docs expansion for format-specific library usage
- pip packaging

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for contribution workflow, coding standards, and pull request guidance.

## Disclaimer

VoxelKit is a developer/research utility tool. It is not a clinical decision system and must not be used for diagnosis or treatment decisions.
