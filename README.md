<div align="center">

<img src="assets/voxelkit_github_banner.svg" alt="VoxelKit" width="600"/>

### Inspect. Preview. QA-check. One toolkit, every format.

[![PyPI](https://img.shields.io/pypi/v/voxelkit?style=flat-square&color=00c4b4&logo=pypi&logoColor=white)](https://pypi.org/project/voxelkit/)
[![Downloads](https://static.pepy.tech/badge/voxelkit?style=flat-square)](https://pepy.tech/projects/voxelkit)
[![Stars](https://img.shields.io/github/stars/ArsalaanAhmad/VoxelKit?style=flat-square&color=ffd700&logo=github)](https://github.com/ArsalaanAhmad/VoxelKit/stargazers)
[![Python](https://img.shields.io/pypi/pyversions/voxelkit?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/voxelkit/)
[![License: MIT](https://img.shields.io/github/license/ArsalaanAhmad/VoxelKit?style=flat-square&color=00c4b4)](LICENSE)
[![DOI](https://zenodo.org/badge/1210656483.svg)](https://doi.org/10.5281/zenodo.19774569)

**[Documentation](https://arsalaanahmad.github.io/VoxelKit/) · [Getting Started](https://arsalaanahmad.github.io/VoxelKit/getting-started/) · [CLI Reference](https://arsalaanahmad.github.io/VoxelKit/cli/) · [Python API](https://arsalaanahmad.github.io/VoxelKit/library/)**

</div>

---

You just received 500 brain scans. Before you write a single line of training code — do you know if the data is actually healthy?

VoxelKit answers that in one command.

```bash
voxelkit report-batch data/scans/
```

No format-specific boilerplate. No juggling `nibabel`, `h5py`, and `tifffile` separately. One consistent interface across every file type you work with.

---

## Features

- 🔍 **Inspect** — shape, dtype, and metadata from any supported file, instantly
- 🖼️ **Preview** — PNG slice from any 3D/4D volume, one command
- 📊 **QA Reports** — per-file stats and warnings (NaNs, constant arrays, zero-dominated volumes)
- 📁 **Batch QA** — scan an entire directory, surface dataset-level risks in one shot
- 🧬 **Embedding Analysis** — dead dimensions, outlier samples, collapsed spaces
- 🌐 **REST API** — FastAPI server for HTTP-based workflows
- 🖥️ **Local GUI** — optional Streamlit interface, runs entirely offline

## Supported Formats

| Format | Extensions |
|---|---|
| NIfTI | `.nii` `.nii.gz` |
| HDF5 | `.h5` `.hdf5` |
| NumPy | `.npy` `.npz` |
| TIFF | `.tif` `.tiff` |

## Install

```bash
pip install voxelkit
```

```bash
pip install voxelkit[gui]   # optional Streamlit GUI
```

Requires Python ≥ 3.9.

## Quick Start

```bash
# What's in this file?
voxelkit inspect scan.nii.gz

# Is the data healthy?
voxelkit report scan.nii.gz

# Show me a slice
voxelkit preview scan.nii.gz --plane axial --output preview.png

# Check a whole dataset at once
voxelkit report-batch data/scans/
```

Or from Python:

```python
from voxelkit import inspect_file, report_file, report_batch

info   = inspect_file("scan.nii.gz")
report = report_file("scan.nii.gz")
batch  = report_batch("data/scans/")
```

## Full Documentation

Everything else — complete CLI reference, Python API docs, REST API, QA warning explanations, and contributing guide — lives at:

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
