---
description: voxelkit report-batch — run QA reports across every supported file in a directory.
---

# voxelkit report-batch

```bash
voxelkit report-batch <directory>
```

Scans a directory, finds every supported file, runs a QA report on each one, and prints the combined results as a JSON array. This is the go-to command when you need a health check across an entire dataset.

---

## Usage

```
voxelkit report-batch DIRECTORY [options]
```

### Arguments

| Argument | Description |
|---|---|
| `DIRECTORY` | Path to a directory to scan |

### Flags

| Flag | Description |
|---|---|
| `--output PATH` | Write JSON output to a file instead of stdout |
| `--html PATH` | Write a self-contained HTML report (with thumbnails + warnings). Mutually exclusive with `--output` and `--csv`. |
| `--csv PATH` | Write a flat CSV (one row per file) to this path. Mutually exclusive with `--output` and `--html`. |
| `--no-recursive` | Only scan the top-level directory, don't descend into subdirectories |

By default, the scan is **recursive** — it finds files in subdirectories too.

---

## Examples

```bash
# print results to stdout
voxelkit report-batch data/study_01/

# save JSON to a file
voxelkit report-batch data/study_01/ --output batch_report.json

# render a self-contained HTML report with thumbnails + warnings
voxelkit report-batch data/study_01/ --html batch_report.html

# export a flat CSV for pandas / Excel
voxelkit report-batch data/study_01/ --csv batch_report.csv

# top-level only
voxelkit report-batch data/study_01/ --no-recursive
```

---

## CSV export

The `--csv` flag writes a flat CSV — one row per successfully reported file — that you can load directly into pandas or Excel:

```bash
voxelkit report-batch data/ --csv batch.csv
```

```csv
file_path,filename,format,shape,ndim,dtype,min,max,mean,std,nan_count,inf_count,zero_fraction,warnings
/data/scan_01.nii.gz,scan_01.nii.gz,nifti,64 x 64 x 30,3,float32,-2.1,4102.8,810.5,398.2,0,0,0.03,
/data/scan_02.nii.gz,scan_02.nii.gz,nifti,64 x 64 x 30,3,float32,0.0,0.0,0.0,0.0,0,0,1.0,Array is constant (all zeros). | Array is mostly zeros.
```

Multiple warnings are joined with ` | ` so each row stays on one line. Failures (files that could not be opened) are excluded from the CSV.

---

## HTML report

The `--html` flag produces a single self-contained `.html` file you can email, attach to a ticket, or drop on a colleague's machine — no external CSS, JS, or images. For every successful report it embeds a base64-encoded PNG thumbnail; cards with warnings are highlighted so scanning a large dataset surfaces issues at a glance.

---

## Output format

A JSON array — one report object per file:

```json
[
  {
    "filename": "subject01_bold.nii.gz",
    "format": "nifti",
    "shape": [64, 64, 30, 200],
    "warnings": []
  },
  {
    "filename": "subject02_bold.nii.gz",
    "format": "nifti",
    "shape": [64, 64, 30, 200],
    "warnings": ["Array is mostly zeros."]
  }
]
```

---

## Find all flagged files at once

```bash
voxelkit report-batch data/ --output batch.json
jq '[.[] | select(.warnings | length > 0) | .filename]' batch.json
```

---

!!! tip "Supported extensions"
    VoxelKit picks up `.nii`, `.nii.gz`, `.h5`, `.hdf5`, `.npy`, `.npz`, `.tif`, `.tiff`, and `.dcm`. Everything else is skipped silently. DICOM series directories are not auto-grouped in the batch scan — each `.dcm` file is reported individually. For a whole-series report, point `voxelkit report` at the directory directly.
