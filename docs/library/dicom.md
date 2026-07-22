---
description: DICOM support in VoxelKit -- inspect, preview, report, anonymise, and convert.
---

# DICOM

VoxelKit handles both single `.dcm` files and series directories (a folder of per-slice `.dcm` files forming a 3D volume) through the same set of functions. You point the function at a file or a directory and it figures out which case it is.

Patient identifiers are stripped from `inspect_dicom` output by default. You have to opt in with `include_phi=True` to see them, which keeps accidental PHI exposure out of logs and debug prints.

```python
from voxelkit import inspect_dicom, preview_dicom, report_dicom
from voxelkit.dicom import anonymise_directory, dicom_to_nifti
```

---

## Functions

| Function | What it does |
|---|---|
| [`inspect_dicom`](dicom-inspect.md) | Metadata dict from a `.dcm` file or series directory |
| [`preview_dicom`](dicom-preview.md) | PNG slice from a `.dcm` file or series |
| [`report_dicom`](dicom-report.md) | QA stats for a `.dcm` file or series |
| [`anonymise_directory`](dicom-anonymise.md) | Scrub PHI tags from a whole directory tree |
| [`dicom_to_nifti`](dicom-convert.md) | Convert a `.dcm` file or series to NIfTI |

---

## Series detection

When you pass a directory to any of the DICOM functions, VoxelKit looks for `.dcm` files at the top level and assembles them as a single series:

1. Slices are sorted by `ImagePositionPatient[2]` when present (patient-relative Z).
2. Falls back to `InstanceNumber`, then filename order.
3. All slices must share the same in-plane shape and dtype. A heterogeneous directory raises `ValidationError` so you notice if two acquisitions have been mixed together.

For nested directory trees (one folder per study, one per series), call the function once per series folder. There is no cross-folder auto-grouping in this release.
