---
description: VoxelKit Python API for DICOM — inspect, preview, report, anonymise, convert.
---

# DICOM (Python API)

VoxelKit's DICOM support handles **both single `.dcm` files and series directories** (folders of per-slice `.dcm` files forming a 3-D volume) through the same functions. Patient identifiers are stripped from `inspect()` output by default — you must opt in with `include_phi=True` to see them.

```python
from voxelkit import (
    inspect_dicom,
    preview_dicom,
    report_dicom,
)
from voxelkit.dicom import anonymise_directory, dicom_to_nifti
```

---

## `inspect_dicom(file_path, *, include_phi=False)`

Returns metadata for a DICOM file or series directory as a JSON-serialisable dict.

```python
from voxelkit import inspect_dicom

inspect_dicom("scan.dcm")
# {
#   "filename": "scan.dcm",
#   "format": "dicom",
#   "source": "file",
#   "shape": [512, 512],
#   "ndim": 2,
#   "dtype": "uint16",
#   "slice_count": 1,
#   "modality": "CT",
#   "voxel_size": [0.7, 0.7, 1.0],
#   ...
# }

# Series directory
inspect_dicom("./series/")
# { ..., "source": "series", "slice_count": 128, "shape": [128, 512, 512], ... }

# Include patient identifiers (treat the result as PHI)
inspect_dicom("scan.dcm", include_phi=True)
# { ..., "patient_name": "...", "patient_id": "...", ... }
```

**Stripped fields (default):** PatientName, PatientID, PatientBirthDate, PatientSex, PatientAge, AccessionNumber, ReferringPhysicianName, InstitutionName, StudyDate, StudyTime, and more. See [`voxelkit/dicom/phi.py`](https://github.com/ArsalaanAhmad/VoxelKit/blob/main/voxelkit/dicom/phi.py) for the full list.

---

## `preview_dicom(file_path, *, axis=0, slice_index=None, as_array=False)`

Render one 2-D slice as PNG bytes (or a `uint8` numpy array).

```python
from voxelkit import preview_dicom

# Single .dcm -> 2-D PNG
png_bytes = preview_dicom("scan.dcm")

# Series directory -> centre slice along the slice axis (axis=0)
png_bytes = preview_dicom("./series/")

# Coronal view
png_bytes = preview_dicom("./series/", axis=1)

# Array form (for embedding in your own report or GUI)
array = preview_dicom("./series/", as_array=True)
# array.shape == (rows, cols), dtype uint8
```

---

## `report_dicom(file_path)`

QA-statistics dict (same schema as every other VoxelKit format).

```python
from voxelkit import report_dicom

report_dicom("./series/")
# {
#   "filename": "series",
#   "format": "dicom",
#   "shape": [128, 512, 512],
#   "ndim": 3,
#   "dtype": "uint16",
#   "min": -1024.0, "max": 3071.0, "mean": ..., "std": ...,
#   "nan_count": 0, "inf_count": 0, "zero_fraction": 0.012,
#   "warnings": []
# }
```

`report_dicom()` reads pixel data only — PHI is never present in the output regardless of headers.

---

## `anonymise_directory(input_dir, output_dir, *, recursive=True)`

Scrub PHI tags from every `.dcm` under `input_dir` and write the cleaned copies into `output_dir`. The directory structure is mirrored, the source tree is left untouched, and non-DICOM files are skipped.

```python
from voxelkit.dicom import anonymise_directory

summary = anonymise_directory(
    input_dir="./incoming_studies/",
    output_dir="./anonymised/",
)
print(summary["files_anonymised"], "of", summary["total_dcm_files"], "files scrubbed")
print("Tags scrubbed:", summary["scrubbed_tag_counts"])
```

The returned `AnonymiseSummary` includes per-tag scrub counts, a list of failures, and absolute input/output paths. The function never raises mid-run; a corrupt or unreadable file is recorded in `failures` so the rest of the dataset still gets processed.

`anonymise_directory()` refuses to run when `input_dir == output_dir` to avoid corrupting the source tree.

---

## `dicom_to_nifti(input_path, output_path)`

Convert a `.dcm` or series directory into a NIfTI-1 file (`.nii` or `.nii.gz`). The affine is built from `ImageOrientationPatient`, `PixelSpacing`, `SliceThickness`, and `ImagePositionPatient`, with the standard DICOM-LPS → NIfTI-RAS sign flip applied.

```python
from voxelkit.dicom import dicom_to_nifti

summary = dicom_to_nifti(
    input_path="./series/",
    output_path="./volume.nii.gz",
)
print(summary["shape"])         # [rows, cols, slices]
print(summary["voxel_size"])    # [row_mm, col_mm, slice_mm]
print(summary["warnings"])      # filled when DICOM headers are incomplete
```

See [voxelkit convert (CLI)](../cli/convert.md) for the full behaviour notes and limitations vs `dcm2niix`.

---

## Series detection

When you pass a **directory** path to any of the functions above, VoxelKit looks at the top level for `.dcm` files. The directory is loaded as a single series:

1. Slices are sorted by `ImagePositionPatient[2]` when present (patient-relative Z).
2. Falls back to `InstanceNumber`, then to filename order.
3. All slices must share the same in-plane shape and dtype — a heterogeneous directory raises `ValidationError` so users notice that two acquisitions are mixed together.

For nested directory trees (one folder per study, one folder per series), call the function once per series folder. There is no auto-grouping across multiple folders in this release.
