---
description: report_file — generate a QA report with statistics and data-quality warnings for any supported file.
---

# report_file

```python
from voxelkit import report_file

report = report_file("scan.nii.gz")
print(report["warnings"])  # [] if everything looks clean
```

`report_file` runs a quality check on your file and gives you back a dictionary of statistics — min, max, mean, std, NaN counts, zero fraction — along with a `warnings` list that flags anything suspicious. It's the quickest way to answer "is this data healthy?"

---

## Signature

```python
def report_file(
    file_path: str | Path,
    dataset_path: str | None = None,
    array_name: str | None = None,
) -> dict
```

---

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `file_path` | `str` or `Path` | — | Path to a supported file |
| `dataset_path` | `str` or `None` | `None` | **HDF5 only.** Dataset path inside the file. If omitted, the first dataset is used |
| `array_name` | `str` or `None` | `None` | **NumPy .npz only.** Array name inside the archive |

---

## Return value

A dictionary with QA statistics for the file. The `warnings` key is always present — it's an empty list if no issues were found.

Example (NIfTI):

```json
{
  "filename": "scan.nii.gz",
  "format": "nifti",
  "shape": [64, 64, 30],
  "dtype": "float32",
  "min": -1.2,
  "max": 4103.5,
  "mean": 812.3,
  "std": 401.1,
  "nan_count": 0,
  "inf_count": 0,
  "zero_fraction": 0.04,
  "warnings": []
}
```

See [QA Warnings](../qa-warnings.md) for a full list of what can appear in `warnings`.

---

## Errors

| Exception | When it's raised |
|---|---|
| `ValueError` | File extension not supported |
| `ValidationError` | Wrong parameter for the detected format |

---

## Examples

=== "NIfTI"
    ```python
    from voxelkit import report_file

    report = report_file("bold.nii.gz")

    if report["warnings"]:
        for w in report["warnings"]:
            print("WARNING:", w)
    else:
        print("All clear.")
    ```

=== "HDF5"
    ```python
    from voxelkit import report_file

    # target a specific dataset inside the file
    report = report_file(
        "experiment.h5",
        dataset_path="data/subject01/run1/bold",
    )
    print(report["nan_count"])  # 0
    ```

=== "NumPy .npy"
    ```python
    from voxelkit import report_file

    report = report_file("features.npy")
    print(report["zero_fraction"])  # e.g. 0.02
    ```

=== "NumPy .npz"
    ```python
    from voxelkit import report_file

    report = report_file("data.npz", array_name="X")
    print(report["warnings"])
    ```

=== "TIFF"
    ```python
    from voxelkit import report_file

    report = report_file("volume.tiff")
    print(report["shape"], report["dtype"])
    ```
