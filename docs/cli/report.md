---
description: voxelkit report — print a QA report with statistics and warnings for a single file.
---

# voxelkit report

```bash
voxelkit report <file>
```

Runs a quality check on a single file and prints the result as JSON. You get statistics (min, max, mean, std, NaN count, zero fraction) and a `warnings` list that flags anything that looks off.

---

## Usage

```
voxelkit report FILE [options]
```

### Arguments

| Argument | Description |
|---|---|
| `FILE` | Path to a supported file |

### Flags

| Flag | Format | Description |
|---|---|---|
| `--dataset PATH` | HDF5 only | Dataset path inside the file. If omitted, the first dataset is used |
| `--array NAME` | `.npz` only | Array name inside the archive |
| `--format {json,text}` | all | Output format. `json` (default) prints the raw JSON. `text` prints a human-readable table. |

---

## Examples

```bash
# NIfTI
voxelkit report bold.nii.gz

# HDF5 — specify a dataset
voxelkit report experiment.h5 --dataset data/subject01/run1/bold

# NumPy
voxelkit report features.npy

# TIFF
voxelkit report volume.tiff
```

Example output:

```json
{
  "filename": "bold.nii.gz",
  "format": "nifti",
  "shape": [64, 64, 30, 200],
  "dtype": "float32",
  "min": -2.1,
  "max": 4102.8,
  "mean": 810.5,
  "std": 398.2,
  "nan_count": 0,
  "inf_count": 0,
  "zero_fraction": 0.03,
  "warnings": []
}
```

---

## Checking for warnings

```bash
voxelkit report subject02.nii.gz | jq '.warnings'
# [
#   "Array is mostly zeros."
# ]
```

See [QA Warnings](../qa-warnings.md) for what each warning means and what to do about it.

---

## Text output

```bash
voxelkit report bold.nii.gz --format text
```

```
filename      bold.nii.gz
format        nifti
shape         64 x 64 x 30 x 200
ndim          4
dtype         float32
min           -2.1
max           4102.8
mean          810.5
std           398.2
nan_count     0
inf_count     0
zero_fraction 3.0%
warnings      none
```

---

## Saving the report

```bash
voxelkit report bold.nii.gz > report.json
```
