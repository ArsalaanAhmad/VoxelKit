<div align="center">

# VoxelKit

A Python toolkit for inspecting, previewing, and QA-checking 3D/4D volumetric data.

[![PyPI](https://img.shields.io/pypi/v/voxelkit?style=flat-square&color=00c4b4&logo=pypi&logoColor=white)](https://pypi.org/project/voxelkit/)
[![Stars](https://img.shields.io/github/stars/ArsalaanAhmad/VoxelKit?style=flat-square&color=ffd700&logo=github)](https://github.com/ArsalaanAhmad/VoxelKit/stargazers)
[![Python](https://img.shields.io/pypi/pyversions/voxelkit?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/voxelkit/)
[![License: MIT](https://img.shields.io/github/license/ArsalaanAhmad/VoxelKit?style=flat-square&color=00c4b4)](LICENSE)
[![DOI](https://zenodo.org/badge/1210656483.svg)](https://doi.org/10.5281/zenodo.19774569)

**[Documentation](https://arsalaanahmad.github.io/VoxelKit/) · [Getting Started](https://arsalaanahmad.github.io/VoxelKit/getting-started/) · [CLI Reference](https://arsalaanahmad.github.io/VoxelKit/cli/) · [Python API](https://arsalaanahmad.github.io/VoxelKit/library/)**

</div>

---

<!-- Replace with an actual recording (e.g. asciinema, terminalizer, or a screen-captured GIF). -->
<!-- Recommended: ~60-80 chars wide, under 15 seconds, showing inspect + report on a real file. -->
<p align="center">
  <img src="docs/assets/demo.gif" alt="VoxelKit CLI demo" width="700">
</p>

---

VoxelKit gives you a single CLI and Python API to inspect metadata, generate slice previews, and run QA checks across NIfTI, HDF5, NumPy, TIFF, and DICOM files. Instead of wiring up `nibabel`, `h5py`, and `tifffile` separately, you get one consistent interface for all of them.

```bash
# quick sanity check on a whole dataset
voxelkit report-batch data/scans/
```

## Features

- **Inspect** - shape, dtype, and metadata from any supported file
- **Preview** - PNG slice from any 3D/4D volume
- **QA Reports** - per-file stats and warnings (NaNs, constant arrays, zero-dominated volumes)
- **Batch QA** - scan an entire directory, output JSON or a self-contained HTML report with thumbnails
- **DICOM Support** - single `.dcm` files and full series directories; PHI stripped by default
- **Anonymisation** - `voxelkit anonymise ./dicoms/ --output ./clean/` scrubs PHI in bulk
- **DICOM to NIfTI** - `voxelkit convert scan.dcm scan.nii.gz`
- **Embedding Analysis** - dead dimensions, outlier samples, collapsed spaces
- **REST API** - FastAPI server for HTTP-based workflows
- **Local GUI** - optional Streamlit interface, runs entirely offline

## Supported Formats

| Format | Extensions / Input |
|---|---|
| NIfTI | `.nii` `.nii.gz` |
| HDF5 | `.h5` `.hdf5` |
| NumPy | `.npy` `.npz` |
| TIFF | `.tif` `.tiff` |
| DICOM | `.dcm` file or directory of slices (series) |

## Install

```bash
pip install voxelkit
```

```bash
pip install voxelkit[gui]   # optional Streamlit GUI
```

Requires Python 3.9+.

## Quick Start

```bash
# What's in this file?
voxelkit inspect scan.nii.gz

# Run QA checks
voxelkit report scan.nii.gz

# Grab a slice
voxelkit preview scan.nii.gz --plane axial --output preview.png

# Batch QA across a directory (JSON or self-contained HTML)
voxelkit report-batch data/scans/
voxelkit report-batch data/scans/ --html report.html
```

DICOM workflows:

```bash
# Inspect a single .dcm or a whole series directory (PHI stripped by default)
voxelkit inspect scan.dcm
voxelkit inspect ./series/

# Scrub PHI from every .dcm under a directory
voxelkit anonymise ./incoming/ --output ./anonymised/

# Convert DICOM to NIfTI
voxelkit convert ./series/ volume.nii.gz
```

Or from Python:

```python
from voxelkit import inspect_file, report_file, report_batch

info   = inspect_file("scan.nii.gz")        # also handles .dcm + series dirs
report = report_file("scan.nii.gz")
batch  = report_batch("data/scans/")

# DICOM-specific helpers
from voxelkit.dicom import anonymise_directory, dicom_to_nifti
anonymise_directory("./incoming/", "./anonymised/")
dicom_to_nifti("./series/", "volume.nii.gz")
```

## Full Documentation

Complete CLI reference, Python API docs, REST API, QA warning explanations, and contributing guide:

**[arsalaanahmad.github.io/VoxelKit](https://arsalaanahmad.github.io/VoxelKit/)**

## Contributing

Contributions are welcome. See the **[Contributing Guide](https://arsalaanahmad.github.io/VoxelKit/contributing/)** for setup instructions, workflow, and how to report issues.

## Citation

If you use VoxelKit in research, please cite:

```bibtex
@software{voxelkit,
  author  = {Arsalaan Ahmad},
  title   = {VoxelKit},
  doi     = {10.5281/zenodo.19774569},
  url     = {https://github.com/ArsalaanAhmad/VoxelKit},
}
```

## Disclaimer

VoxelKit is a developer and research utility. It is not a clinical decision system and must not be used for diagnosis or treatment.
