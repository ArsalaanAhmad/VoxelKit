---
description: VoxelKit exceptions -- when each error is raised and how to catch it.
---

# Errors

VoxelKit uses three exception classes. All three are importable from `voxelkit.core.errors`.

```python
from voxelkit.core.errors import ValidationError, ThresholdViolationError, UnsupportedFormatError
```

---

## ValidationError

Raised when a parameter is valid Python but wrong for the detected format. For example, passing `dataset_path` to a NIfTI file, or setting `include_phi=True` on a non-DICOM path.

```python
from voxelkit import inspect_file
from voxelkit.core.errors import ValidationError

try:
    result = inspect_file("scan.nii.gz", include_phi=True)
except ValidationError as e:
    print("Wrong parameter for this format:", e)
```

`ValidationError` is a subclass of `ValueError`, so existing code that catches `ValueError` will still catch it.

---

## UnsupportedFormatError

Raised when the file extension is not one VoxelKit recognises. Also a subclass of `ValueError`.

```python
from voxelkit import inspect_file
from voxelkit.core.errors import UnsupportedFormatError

try:
    result = inspect_file("data.parquet")
except UnsupportedFormatError as e:
    print("Format not supported:", e)
```

Catching `UnsupportedFormatError` specifically is more precise than catching `ValueError`, since it won't accidentally swallow unrelated errors.

---

## ThresholdViolationError

Raised by the VoxelKit CLI when a threshold flag like `--max-nan` or `--no-warnings` is violated. This is a CLI concept, not a library one. The library functions `report_file`, `report_dicom`, and `report_batch` always return a result dict; they never raise `ThresholdViolationError` themselves.

If you are building a pipeline in Python and want threshold behaviour, read the stats and `warnings` fields from the result dict directly:

```python
from voxelkit import report_file

report = report_file("scan.nii.gz")

if report["nan_count"] > 0:
    raise ValueError(f"NaN check failed: {report['nan_count']} NaNs found")

if report["warnings"]:
    raise ValueError(f"QA warnings: {report['warnings']}")
```

`ThresholdViolationError` is a distinct class (not a subclass of `ValueError`) so the CLI can exit with code 3, which lets scripts tell "threshold violated" apart from "hard error". See [report threshold flags](../cli/report.md#qa-thresholds) for the CLI usage.

---

## Catching errors in practice

```python
from voxelkit import inspect_file, report_file
from voxelkit.core.errors import ValidationError, UnsupportedFormatError

def safe_inspect(path):
    try:
        return inspect_file(path)
    except UnsupportedFormatError:
        return None  # skip unsupported files silently
    except ValidationError as e:
        print(f"Parameter error on {path}: {e}")
        return None
    except FileNotFoundError:
        print(f"File not found: {path}")
        return None
```
