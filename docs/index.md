# VoxelKit

Inspect, preview, and QA-check multidimensional imaging data from one unified Python and CLI workflow.

[Get Started](getting-started.md){ .md-button .md-button--primary }
[How To Use (CLI)](cli.md){ .md-button }
[Python Usage](python-usage.md){ .md-button }

## Project Snapshot

[![PyPI version](https://img.shields.io/pypi/v/voxelkit.svg)](https://pypi.org/project/voxelkit/)
[![PyPI Downloads](https://static.pepy.tech/badge/voxelkit)](https://pepy.tech/projects/voxelkit)
[![GitHub stars](https://img.shields.io/github/stars/ArsalaanAhmad/VoxelKit?style=social)](https://github.com/ArsalaanAhmad/VoxelKit/stargazers)
[![DOI](https://zenodo.org/badge/1210656483.svg)](https://doi.org/10.5281/zenodo.19774569)
[![GitHub clones](https://img.shields.io/badge/GitHub%20clones-track%20in%20Traffic-4C9AFF)](https://github.com/ArsalaanAhmad/VoxelKit/graphs/traffic)

## Why VoxelKit

Low-level libraries like `nibabel`, `h5py`, and `tifffile` are excellent building blocks.
VoxelKit sits on top of that ecosystem and gives you one consistent workflow for:

- quick inspection of structure and metadata
- PNG previews for 2D/3D data
- per-file QA statistics and warnings
- directory-level QA aggregation with `report-batch`

## Format Coverage

- NIfTI (`.nii`, `.nii.gz`)
- HDF5 (`.h5`, `.hdf5`)
- NumPy (`.npy`, `.npz`)
- TIFF (`.tif`, `.tiff`) routing support

## Start Using It

### CLI

```bash
voxelkit inspect tests/fixtures/sample_3d.nii.gz
voxelkit preview tests/fixtures/sample_3d.nii.gz --plane axial --slice 4 --output preview.png
voxelkit report tests/fixtures/sample_nested.h5 --dataset data/subject01/run1/bold
voxelkit report-batch tests/fixtures --output batch_report.json
```

### Python

```python
from voxelkit import inspect_file, preview_file, report_file, report_batch

meta = inspect_file("tests/fixtures/sample_3d.nii.gz")
png = preview_file("tests/fixtures/sample_3d.nii.gz", plane="axial", slice_index=4)
report = report_file("tests/fixtures/sample_nested.h5", dataset_path="data/subject01/run1/bold")
batch = report_batch("tests/fixtures", recursive=True)
```

## Next Step

Read [Getting Started](getting-started.md) for install, first commands, and project setup.
