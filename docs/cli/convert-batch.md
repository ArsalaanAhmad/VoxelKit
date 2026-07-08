---
description: voxelkit convert-batch — convert every DICOM file and series directory under a folder to NIfTI volumes.
---

# voxelkit convert-batch

```bash
voxelkit convert-batch <directory> --output <output_dir>
```

Scans a directory for `.dcm` files, groups them into series, and converts each to a NIfTI volume. Follows the same resilience pattern as `anonymise` — failures are collected per input and reported in the summary, never raised mid-run.

A directory with multiple `.dcm` files is treated as a single series and produces one volume. A lone `.dcm` in a directory is converted individually.

---

## Usage

```
voxelkit convert-batch DIRECTORY --output OUTPUT [options]
```

### Arguments

| Argument | Description |
|---|---|
| `DIRECTORY` | Root directory to scan for `.dcm` files |

### Flags

| Flag | Description |
|---|---|
| `--output PATH` | Output directory for NIfTI volumes. Created if needed. Mirrors the input directory structure. |
| `--no-recursive` | Only scan the top-level directory, don't descend into subdirectories |

By default, the scan is **recursive**.

---

## Examples

```bash
# Convert all DICOM series under a study directory
voxelkit convert-batch ./incoming/ --output ./niftis/

# Top-level only
voxelkit convert-batch ./incoming/ --output ./niftis/ --no-recursive
```

Example output:

```json
{
  "input_dir": "/data/incoming",
  "output_dir": "/data/niftis",
  "recursive": true,
  "total_dicom_inputs": 4,
  "successful_conversions": 3,
  "failed_conversions": 1,
  "conversions": [
    {
      "input_path": "/data/incoming/series_01",
      "output_path": "/data/niftis/series_01.nii.gz",
      "source": "series",
      "shape": [512, 512, 40],
      "voxel_size": [0.7, 0.7, 2.0],
      "slice_count": 40,
      "warnings": []
    }
  ],
  "failures": [
    {
      "input_path": "/data/incoming/corrupt.dcm",
      "error": "Invalid, corrupted, or unreadable HDF5 file."
    }
  ]
}
```

The summary is also printed to stderr as a human-readable line:

```
Converted 3 of 4 DICOM sources -> /data/niftis
```

---

## How inputs are grouped

`convert-batch` groups `.dcm` files by their parent directory:

- **Multiple `.dcm` files in the same directory** → treated as a series, converted to one volume named after the directory (e.g. `series_01.nii.gz`)
- **A lone `.dcm` file** → converted individually, named after the file stem (e.g. `scan.nii.gz`)

The output directory structure mirrors the input structure, so nested series directories stay organised.

---

!!! tip "Converting a single file or series"
    For a single `.dcm` file or series directory, use [`voxelkit convert`](convert.md) instead.

!!! tip "Affine and header warnings"
    Each conversion uses the same affine-building logic as `voxelkit convert`. If DICOM header tags are missing, fallback values are used and surfaced in the `warnings` list. See [voxelkit convert](convert.md) for details.
