---
description: VoxelKit Python library overview -- four functions, one import, every supported format.
---

# Library Reference

VoxelKit was built library-first. The CLI and REST API are thin layers on top of these Python functions, which means you get the full power of the toolkit when you use it directly in your code.

One import covers the common cases:

```python
from voxelkit import inspect_file, preview_file, report_file, report_batch
```

---

## The four main functions

Each function auto-detects the file format from the extension, so you don't have to think about which module handles which format.

| Function | What it returns | Page |
|---|---|---|
| `inspect_file(path)` | Metadata dict: shape, dtype, headers | [inspect_file](inspect.md) |
| `preview_file(path, ...)` | PNG image as `bytes` | [preview_file](preview.md) |
| `report_file(path, ...)` | QA stats and warnings dict | [report_file](report.md) |
| `report_batch(path, ...)` | List of reports for a whole directory | [report_batch](batch.md) |

---

## DICOM

DICOM has two extra concerns no other format shares: **single-file vs. series-directory inputs**, and **PHI (Protected Health Information)**. The standard functions handle both shapes already and strip PHI by default. When you need to opt into PHI, anonymise a tree, or convert a series to NIfTI, use the DICOM-specific entry points:

| Function | What it does | Page |
|---|---|---|
| `inspect_dicom(path, include_phi=False)` | DICOM metadata dict | [inspect_dicom](dicom-inspect.md) |
| `preview_dicom(path, ...)` | PNG slice from a `.dcm` or series | [preview_dicom](dicom-preview.md) |
| `report_dicom(path)` | QA stats for a `.dcm` or series | [report_dicom](dicom-report.md) |
| `anonymise_directory(in, out)` | Scrubbed copies of every `.dcm` in a tree | [anonymise_directory](dicom-anonymise.md) |
| `dicom_to_nifti(in, out)` | NIfTI-1 conversion | [dicom_to_nifti](dicom-convert.md) |

See [DICOM overview](dicom.md) for series detection behaviour and import paths.

---

## Embedding-specific functions

If you're working with 2D feature matrices (N samples by D dimensions), these two go deeper than `report_file`:

| Function | What it returns | Page |
|---|---|---|
| `report_embedding(path)` | Per-dimension and per-sample QA | [Embedding Analysis](embedding.md) |
| `preview_embedding(path, ...)` | Heatmap PNG as `bytes` | [Embedding Analysis](embedding.md) |

---

## Further reading

| Page | What's in it |
|---|---|
| [GeoTIFF](geotiff.md) | How inspect and report work on georeferenced raster files |
| [Errors](errors.md) | What each exception class means and how to catch it |
| [Concepts](concepts.md) | Format detection, library-first architecture, result types, PHI philosophy |

---

## Format-specific imports

The four main functions cover 95% of use cases. If you need direct access to a format module:

```python
from voxelkit import (
    inspect_h5, preview_h5, report_h5,
    inspect_npy, preview_npy, report_npy,
    nifti_metadata, preview_nifti, report_nifti,
    inspect_tiff, preview_tiff, report_tiff,
    inspect_dicom, preview_dicom, report_dicom,
    report_embedding, preview_embedding,
)
from voxelkit.dicom import anonymise_directory, dicom_to_nifti
```

For most work, stick with `inspect_file`, `preview_file`, `report_file`, and `report_batch`.
