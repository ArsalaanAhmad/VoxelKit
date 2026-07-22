---
description: voxelkit compare — diff QA reports for two files side by side.
---

# voxelkit compare

```bash
voxelkit compare <file_a> <file_b>
```

Runs a QA report on two files and diffs them — shape, dtype, and per-stat deltas. Useful for verifying that a preprocessing step, conversion, or anonymisation didn't corrupt or drift the data.

---

## Usage

```
voxelkit compare FILE_A FILE_B [options]
```

### Arguments

| Argument | Description |
|---|---|
| `FILE_A` | First file (any supported format) |
| `FILE_B` | Second file (any supported format) |

### Flags

| Flag | Description |
|---|---|
| `--format {json,text}` | Output format. `json` (default) or `text` for a human-readable table. |
| `--dataset PATH` | HDF5 only. Dataset path applied to both files. |
| `--array NAME` | NumPy NPZ only. Array name applied to both files. |

---

## Examples

```bash
# Compare two NIfTI volumes
voxelkit compare before.nii.gz after.nii.gz

# Human-readable table
voxelkit compare before.nii.gz after.nii.gz --format text

# Compare HDF5 datasets
voxelkit compare a.h5 b.h5 --dataset data/subject01/run1/bold
```

Example `--format text` output:

```
file_a         before.nii.gz
file_b         after.nii.gz
shape          ✓  [64, 64, 30]  vs  [64, 64, 30]
dtype          ✓  float32  vs  float32
format         ✓

stat              file_a       file_b        delta
--------------------------------------------------------
min              -2.100000    -2.100000     0.000000
max           4102.800000  4098.200000    -4.600000
mean           810.500000   809.100000    -1.400000
std            398.200000   397.800000    -0.400000
nan_count               0            0            0
inf_count               0            0            0
zero_fraction        0.03         0.03            0
```

Example JSON output:

```json
{
  "file_a": "before.nii.gz",
  "file_b": "after.nii.gz",
  "shape_match": true,
  "dtype_match": true,
  "format_match": true,
  "shape_a": [64, 64, 30],
  "shape_b": [64, 64, 30],
  "dtype_a": "float32",
  "dtype_b": "float32",
  "stats": {
    "min":  { "a": -2.1,   "b": -2.1,   "delta": 0.0 },
    "max":  { "a": 4102.8, "b": 4098.2, "delta": -4.6 },
    "mean": { "a": 810.5,  "b": 809.1,  "delta": -1.4 }
  },
  "warnings_a": [],
  "warnings_b": []
}
```

---

## Use cases

**Verify a preprocessing step didn't corrupt data:**
```bash
voxelkit compare raw.nii.gz preprocessed.nii.gz --format text
```

**Check that anonymisation preserved pixel values:**
```bash
voxelkit compare original.dcm anonymised.dcm --format text
```

**CI gate — fail if shape changes:**
```bash
voxelkit compare baseline.nii.gz output.nii.gz | jq '.shape_match' | grep -q true
```
