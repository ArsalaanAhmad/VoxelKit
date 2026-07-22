---
description: How VoxelKit works -- format detection, library-first architecture, result types, and PHI handling.
---

# How VoxelKit works

This page explains the design decisions behind VoxelKit so you can predict what it will do in cases the reference docs don't spell out.

---

## Format auto-detection

All four top-level functions (`inspect_file`, `preview_file`, `report_file`, `report_batch`) detect the file format from the extension and route to the right module automatically. You never pass a format flag.

| Extension | Format module |
|---|---|
| `.nii`, `.nii.gz` | NIfTI (nibabel) |
| `.h5`, `.hdf5` | HDF5 (h5py) |
| `.npy`, `.npz` | NumPy |
| `.tif`, `.tiff` | TIFF (tifffile, optionally rasterio for GeoTIFFs) |
| `.dcm` | DICOM (pydicom) |

Detection is purely by extension. VoxelKit does not read magic bytes. If a file has a `.tif` extension it is treated as TIFF regardless of its contents.

DICOM series directories are a special case. You can pass a directory path to any DICOM-aware function and VoxelKit will assemble the slices inside it into a 3D volume automatically. The top-level `inspect_file`, `preview_file`, and `report_file` all route directory paths to the DICOM handler.

---

## Library-first architecture

The CLI and REST API are thin layers on top of the library. Every CLI command calls the same Python function you would call directly:

```
voxelkit inspect scan.nii.gz       --> inspect_file("scan.nii.gz")
voxelkit report scan.nii.gz        --> report_file("scan.nii.gz")
POST /nifti/inspect                 --> inspect_file(uploaded_file)
```

This means you can reproduce any CLI output in Python with one function call and get back the same result dict. It also means improvements and bug fixes in the library automatically apply to the CLI and API with no extra work.

The only things the CLI adds that aren't in the library are output formatting (`--format text`, `--csv`) and threshold gates (`--max-nan`, `--no-warnings`). These are presentation concerns, not data concerns.

---

## Result types

Every function returns a TypedDict subclass. In practice these behave like plain dicts so you can index them, pass them to `json.dumps`, and iterate their keys without any special handling.

The type annotations are there for editor autocompletion and static analysis. If you work in VS Code or PyCharm you get inline type hints for free:

```python
from voxelkit.core.types import (
    NiftiMetadataResult,
    DicomInspectResult,
    GeoTiffInspectResult,
    FileReportResult,
)
```

---

## PHI handling

Any function that reads DICOM metadata strips patient identifiers from the result by default. You have to pass `include_phi=True` explicitly to get them back.

The design intent is to make accidental PHI exposure in logs, debug prints, and JSON exports hard. Even if you call `inspect_file` on a DICOM file that has every PHI tag populated, the result you get back is safe to print or store by default.

`report_dicom` and `report_batch` never include PHI in their output regardless of any flags, because QA statistics don't depend on patient data at all.

See [anonymise_directory](dicom-anonymise.md) for bulk scrubbing of a directory tree before sharing data.

---

## Optional dependencies

VoxelKit has two optional dependency groups:

| Install command | Package | What it enables |
|---|---|---|
| `pip install voxelkit[gui]` | streamlit | `voxelkit gui` browser interface |
| `pip install voxelkit[geo]` | rasterio | GeoTIFF CRS and bounds in inspect results |

Both are strictly optional. All core functionality works without them. When an optional package is missing, the code that needs it either skips quietly (GeoTIFF enrichment just returns no geo fields) or raises a clear error with an install hint (`voxelkit gui` without streamlit installed).

---

## Error model

The library raises:

- `UnsupportedFormatError` when the file extension is not recognised
- `ValidationError` when a parameter is valid Python but wrong for the format being used
- `FileNotFoundError` when the path does not exist (from the underlying file system)

`ThresholdViolationError` is raised only by the CLI layer, not by library functions. See [Errors](errors.md) for details on catching each one.
