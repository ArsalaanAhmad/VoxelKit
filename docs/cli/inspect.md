---
description: voxelkit inspect — print file metadata as JSON from the terminal.
---

# voxelkit inspect

```bash
voxelkit inspect <file>
```

Prints a JSON snapshot of the file's structure — shape, dtype, headers — to stdout. No pixel data is loaded. This is the fastest way to answer "what is this file?"

---

## Usage

```
voxelkit inspect FILE
```

### Arguments

| Argument | Description |
|---|---|
| `FILE` | Path to any supported file (`.nii`, `.nii.gz`, `.h5`, `.hdf5`, `.npy`, `.npz`, `.tif`, `.tiff`) |

---

## Examples

```bash
# NIfTI
voxelkit inspect scan.nii.gz

# HDF5 — lists all datasets inside the file
voxelkit inspect experiment.h5

# NumPy
voxelkit inspect features.npy

# TIFF
voxelkit inspect volume.tiff
```

Example output for a NIfTI file:

```json
{
  "filename": "scan.nii.gz",
  "format": "nifti",
  "shape": [64, 64, 30],
  "voxel_sizes": [3.0, 3.0, 4.0],
  "data_dtype": "float32"
}
```

---

## Tips

Pipe the output to `jq` to query specific fields:

```bash
voxelkit inspect scan.nii.gz | jq '.shape'
# [64, 64, 30]

voxelkit inspect experiment.h5 | jq '.datasets[].path'
# "data/subject01/run1/bold"
# "data/subject02/run1/bold"
```
