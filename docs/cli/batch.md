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
| `--output PATH` | Write the JSON output to a file instead of stdout |
| `--html PATH` | Write a self-contained HTML report (with thumbnails + warnings) instead of JSON. Mutually exclusive with `--output`. |
| `--no-recursive` | Only scan the top-level directory, don't descend into subdirectories |

By default, the scan is **recursive** — it finds files in subdirectories too.

---

## Examples

```bash
# print results to stdout
voxelkit report-batch data/study_01/

# save to a file
voxelkit report-batch data/study_01/ --output batch_report.json

# render a self-contained HTML report with thumbnails + warnings
voxelkit report-batch data/study_01/ --html batch_report.html

# top-level only
voxelkit report-batch data/study_01/ --no-recursive
```

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
