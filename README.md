# VoxelKit

Lightweight FastAPI utility for inspecting, previewing, and slicing multidimensional imaging data (NIfTI and HDF5).

## Motivation

VoxelKit removes repetitive one-off scripts for inspecting and previewing imaging datasets during development and research workflows.

## Features

- NIfTI metadata inspection via `POST /nifti/metadata`
- NIfTI slice preview (PNG) via `POST /nifti/preview`
- HDF5 recursive structure inspection via `POST /h5/inspect`
- HDF5 dataset slice preview (PNG) via `POST /h5/slice`

## Quickstart

### 1) Install dependencies

```powershell
cd neuroprep-api
pip install -r requirements.txt
```

### 2) Run the API

In this environment, the reliable command is:

```powershell
py -m uvicorn app.main:app --reload
```

### 3) Open API docs

- Swagger UI: `http://127.0.0.1:8000/docs`

## Usage

### Health

```bash
curl -X GET "http://127.0.0.1:8000/health"
```

### NIfTI metadata

```bash
curl -X POST "http://127.0.0.1:8000/nifti/metadata" \
	-F "file=@tests/fixtures/sample_3d.nii.gz"
```

Example response:

```json
{
	"filename": "sample_3d.nii.gz",
	"shape": [8, 9, 10],
	"ndim": 3,
	"voxel_size": [1.0, 1.0, 1.0],
	"dtype": "float32"
}
```

### NIfTI preview

```bash
curl -X POST "http://127.0.0.1:8000/nifti/preview?plane=axial&slice_index=4" \
	-F "file=@tests/fixtures/sample_3d.nii.gz" \
	--output nifti_preview.png
```

### HDF5 inspect

```bash
curl -X POST "http://127.0.0.1:8000/h5/inspect" \
	-F "file=@tests/fixtures/sample_nested.h5"
```

### HDF5 slice

```bash
curl -X POST "http://127.0.0.1:8000/h5/slice?dataset_path=data/subject01/run1/bold&axis=2&slice_index=3" \
	-F "file=@tests/fixtures/sample_nested.h5" \
	--output h5_preview.png
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

## Roadmap

- normalization improvements
- batch processing
- API keys
- lightweight Python client

## Contributing

Contributions are welcome.

1. Fork the repo and create a feature branch.
2. Keep changes small and focused.
3. Add or update tests when behavior changes.
4. Open a PR with a clear summary and rationale.

## Disclaimer

VoxelKit is a developer/research utility tool. It is not a clinical decision system and must not be used for diagnosis or treatment decisions.
