---
description: report_dicom -- QA statistics for a DICOM file or series.
---

# report_dicom

```python
from voxelkit import report_dicom

report = report_dicom("./series/")
print(report["warnings"])  # [] if everything looks fine
```

Returns the same QA statistics structure as every other format in VoxelKit: min, max, mean, std, NaN count, inf count, zero fraction, and a `warnings` list. PHI is never present in the output, regardless of what the DICOM headers contain.

---

## Signature

```python
def report_dicom(file_path: str | Path) -> FileReportResult
```

## Parameters

| Parameter | Type | Description |
|---|---|---|
| `file_path` | `str` or `Path` | Path to a `.dcm` file or series directory |

---

## Return value

```json
{
  "filename": "series",
  "format": "dicom",
  "shape": [128, 512, 512],
  "ndim": 3,
  "dtype": "uint16",
  "min": -1024.0,
  "max": 3071.0,
  "mean": 312.4,
  "std": 891.2,
  "nan_count": 0,
  "inf_count": 0,
  "zero_fraction": 0.012,
  "warnings": []
}
```

See [QA Warnings](../../qa-warnings.md) for what can appear in `warnings`.

---

## Examples

```python
from voxelkit import report_dicom

report = report_dicom("./series/")

if report["warnings"]:
    for w in report["warnings"]:
        print("WARNING:", w)
else:
    print("All clear.")

# Single file works the same way
report = report_dicom("scan.dcm")
print(report["shape"])  # [512, 512]
```

You can also call `report_file("scan.dcm")` and it routes here automatically.
