---
description: inspect_file — extract shape, dtype, and metadata from any supported imaging file.
---

# inspect_file

```python
from voxelkit import inspect_file

result = inspect_file("scan.nii.gz")
```

Point it at any supported file and you get back a dictionary with the structural facts about that file — shape, dtype, headers — without loading the actual voxel/pixel data into memory. Think of it as a fast "what is this thing?" tool.

---

## Signature

```python
def inspect_file(
    file_path: str | Path,
    *,
    include_phi: bool = False,
) -> dict
```

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `file_path` | `str` or `Path` | required | Path to a `.nii`, `.nii.gz`, `.h5`, `.hdf5`, `.npy`, `.npz`, `.tif`, `.tiff`, or `.dcm` file. Can also be a directory containing DICOM slices. |
| `include_phi` | `bool` | `False` | DICOM only. When `True`, patient identifiers are included in the result. No effect on any other format. |

---

## Return value

The shape of the returned dictionary depends on the file format.

=== "NIfTI"
    ```json
    {
      "filename": "scan.nii.gz",
      "format": "nifti",
      "shape": [64, 64, 30],
      "affine": [[...], ...],
      "voxel_sizes": [3.0, 3.0, 4.0],
      "data_dtype": "float32",
      "header": { "...": "..." }
    }
    ```

=== "HDF5"
    ```json
    {
      "filename": "data.h5",
      "format": "hdf5",
      "datasets": [
        {
          "path": "data/subject01/run1/bold",
          "shape": [64, 64, 30, 200],
          "dtype": "float32"
        }
      ]
    }
    ```

=== "NumPy .npy"
    ```json
    {
      "filename": "features.npy",
      "format": "numpy",
      "shape": [1000, 512],
      "dtype": "float32"
    }
    ```

=== "NumPy .npz"
    ```json
    {
      "filename": "data.npz",
      "format": "numpy",
      "arrays": [
        { "name": "X", "shape": [500, 256], "dtype": "float64" },
        { "name": "y", "shape": [500],      "dtype": "int64"   }
      ]
    }
    ```

=== "TIFF"
    ```json
    {
      "filename": "volume.tiff",
      "format": "tiff",
      "shape": [50, 512, 512],
      "ndim": 3,
      "dtype": "uint16",
      "page_count": 50,
      "axes": "ZYX"
    }
    ```

=== "DICOM"
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

    For a series directory the `source` field is `"series"` and `shape` becomes three-dimensional:

    ```json
    {
      "filename": "series",
      "format": "dicom",
      "source": "series",
      "shape": [128, 512, 512],
      "ndim": 3,
      "slice_count": 128,
      "modality": "MR",
      "voxel_size": [1.0, 1.0, 1.2]
    }
    ```

    See [inspect_dicom](dicom-inspect.md) for full DICOM details including PHI fields.

---

## Errors

| Exception | When it's raised |
|---|---|
| `ValueError` | The file extension is not supported |
| `FileNotFoundError` | The file path doesn't exist |

---

## Example

```python
from voxelkit import inspect_file

result = inspect_file("subject01_bold.nii.gz")

print(result["shape"])       # [64, 64, 30, 200]
print(result["data_dtype"])  # "float32"
print(result["voxel_sizes"]) # [3.0, 3.0, 4.0]
```

For HDF5 files, you get a list of all datasets inside:

```python
result = inspect_file("experiment.h5")

for ds in result["datasets"]:
    print(ds["path"], ds["shape"])
# data/subject01/run1/bold  [64, 64, 30, 200]
# data/subject02/run1/bold  [64, 64, 30, 198]
```
