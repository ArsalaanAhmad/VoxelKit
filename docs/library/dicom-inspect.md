---
description: inspect_dicom -- extract metadata from a DICOM file or series directory.
---

# inspect_dicom

```python
from voxelkit import inspect_dicom

result = inspect_dicom("scan.dcm")
```

Returns a JSON-serialisable dict with structural metadata for a `.dcm` file or a series directory. Patient identifiers are stripped from the output by default.

---

## Signature

```python
def inspect_dicom(
    file_path: str | Path,
    *,
    include_phi: bool = False,
) -> DicomInspectResult
```

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `file_path` | `str` or `Path` | required | Path to a `.dcm` file or a directory containing `.dcm` slices |
| `include_phi` | `bool` | `False` | When `True`, patient identifiers are included in the result. Treat the output as PHI if you enable this. |

---

## Return value

=== "Single file"
    ```json
    {
      "filename": "scan.dcm",
      "format": "dicom",
      "source": "file",
      "shape": [512, 512],
      "ndim": 2,
      "dtype": "uint16",
      "slice_count": 1,
      "modality": "CT",
      "voxel_size": [0.7, 0.7, 1.0]
    }
    ```

=== "Series directory"
    ```json
    {
      "filename": "series",
      "format": "dicom",
      "source": "series",
      "shape": [128, 512, 512],
      "ndim": 3,
      "dtype": "uint16",
      "slice_count": 128,
      "modality": "MR",
      "voxel_size": [1.0, 1.0, 1.2]
    }
    ```

=== "With PHI"
    ```json
    {
      "filename": "scan.dcm",
      "format": "dicom",
      "source": "file",
      "shape": [512, 512],
      "patient_name": "Smith^John",
      "patient_id": "PAT001",
      "patient_birth_date": "19800101",
      "study_date": "20240315",
      "institution_name": "General Hospital"
    }
    ```

---

## PHI fields stripped by default

The following tags are removed unless `include_phi=True`:

`PatientName`, `PatientID`, `PatientBirthDate`, `PatientSex`, `PatientAge`, `AccessionNumber`, `ReferringPhysicianName`, `InstitutionName`, `StudyDate`, `StudyTime`, and more.

See [`voxelkit/dicom/phi.py`](https://github.com/ArsalaanAhmad/VoxelKit/blob/main/voxelkit/dicom/phi.py) for the full list.

---

## Examples

```python
from voxelkit import inspect_dicom

# Single file
result = inspect_dicom("scan.dcm")
print(result["shape"])    # [512, 512]
print(result["modality"]) # "CT"

# Series directory
result = inspect_dicom("./series/")
print(result["source"])      # "series"
print(result["slice_count"]) # 128

# With PHI (handle the result carefully)
result = inspect_dicom("scan.dcm", include_phi=True)
print(result["patient_id"])
```

You can also call `inspect_file` on a `.dcm` path and it routes here automatically. The `include_phi` parameter is the main reason to call `inspect_dicom` directly instead.
