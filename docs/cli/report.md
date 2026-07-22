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
| `--format {json,text}` | all | Output format. `json` (default) or `text` for a human-readable table. Mutually exclusive with `--output`. |
| `--output PATH` | all | Write JSON to a file instead of stdout. Mutually exclusive with `--format text`. |
| `--max-nan N` | all | Exit with code 3 if `nan_count` exceeds N |
| `--max-zero-fraction F` | all | Exit with code 3 if `zero_fraction` exceeds F (0.0–1.0) |
| `--max-inf N` | all | Exit with code 3 if `inf_count` exceeds N |
| `--no-warnings` | all | Exit with code 3 if the report contains any QA warnings |

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
# Redirect stdout
voxelkit report bold.nii.gz > report.json

# Or use --output
voxelkit report bold.nii.gz --output report.json
```

---

## QA thresholds

Use threshold flags to make `voxelkit report` behave like a CI gate — it exits with code **3** when a constraint is violated, code **0** when everything passes, and code **2** on a hard error.

```bash
# Fail if any NaNs
voxelkit report scan.nii.gz --max-nan 0

# Fail if more than 10% zeros
voxelkit report scan.nii.gz --max-zero-fraction 0.1

# Fail if any QA warnings
voxelkit report scan.nii.gz --no-warnings

# Combine
voxelkit report scan.nii.gz --max-nan 0 --max-zero-fraction 0.1 --no-warnings
```

Exit codes:

| Code | Meaning |
|---|---|
| 0 | Report generated, all thresholds passed |
| 2 | Hard error (file unreadable, unsupported format) |
| 3 | Threshold violated — report was generated but a constraint failed |
