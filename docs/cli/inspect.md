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
| `FILE` | Path to any supported file (`.nii`, `.nii.gz`, `.h5`, `.hdf5`, `.npy`, `.npz`, `.tif`, `.tiff`, `.dcm`) or a directory of `.dcm` slices (a DICOM series) |

### Flags

| Flag | Description |
|---|---|
| `--phi` | DICOM only. Include patient-identifying fields in the output. Prints a stderr warning when set — treat the result as PHI. |
| `--format {json,text}` | Output format. `json` (default) prints the raw JSON. `text` prints a human-readable table. |

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

# DICOM — single slice
voxelkit inspect scan.dcm

# DICOM — series directory (folder of .dcm slices forming a 3-D volume)
voxelkit inspect ./series/

# DICOM with PHI included (warns on stderr)
voxelkit inspect scan.dcm --phi

# Human-readable table instead of JSON
voxelkit inspect scan.nii.gz --format text
```

Example `--format text` output for a NIfTI file:

```
filename  scan.nii.gz
shape     64 x 64 x 30
ndim      3
voxel_size  3.0 x 3.0 x 4.0 mm
dtype     float32
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
