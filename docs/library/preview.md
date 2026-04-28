---
description: preview_file — generate a PNG slice preview from any supported multidimensional imaging file.
---

# preview_file

```python
from voxelkit import preview_file

png_bytes = preview_file("scan.nii.gz", plane="axial", slice_index=10)

with open("preview.png", "wb") as f:
    f.write(png_bytes)
```

`preview_file` extracts a 2D slice from your file and returns it as raw PNG bytes. The center slice is used by default if you don't specify one. The image is grayscale, normalised to 0–255.

---

## Signature

```python
def preview_file(
    file_path: str | Path,
    *,
    plane: str = "axial",
    dataset_path: str | None = None,
    array_name: str | None = None,
    axis: int | None = None,
    slice_index: int | None = None,
) -> bytes
```

---

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `file_path` | `str` or `Path` | — | Path to a supported file |
| `plane` | `str` | `"axial"` | **NIfTI only.** One of `"axial"`, `"coronal"`, `"sagittal"` |
| `dataset_path` | `str` or `None` | `None` | **HDF5 only.** Path to the dataset inside the file, e.g. `"data/subject01/run1/bold"` |
| `array_name` | `str` or `None` | `None` | **NumPy .npz only.** Name of the array inside the archive |
| `axis` | `int` or `None` | `None` | **HDF5, NumPy, TIFF.** Which axis to slice along (0, 1, or 2). Required for HDF5 3D datasets |
| `slice_index` | `int` or `None` | `None` | Index of the slice to extract. Defaults to the centre slice |

!!! warning "Format-specific rules"
    Some parameters are only valid for certain formats — passing the wrong one raises a `ValidationError`.

    - `plane` → NIfTI only
    - `dataset_path` → HDF5 only (required for HDF5)
    - `array_name` → `.npz` only
    - `axis` → HDF5 / NumPy / TIFF (required for 3D HDF5 datasets)

---

## Return value

Raw PNG image as `bytes`. Save it to disk, pass it to a web response, or decode it with a library like Pillow.

---

## Errors

| Exception | When it's raised |
|---|---|
| `ValidationError` | Wrong parameter used for the detected format |
| `ValueError` | File extension not supported |

---

## Examples

=== "NIfTI"
    ```python
    from voxelkit import preview_file

    # axial centre slice (default)
    png = preview_file("bold.nii.gz")

    # specific plane and slice
    png = preview_file("bold.nii.gz", plane="coronal", slice_index=15)

    with open("preview.png", "wb") as f:
        f.write(png)
    ```

=== "HDF5"
    ```python
    from voxelkit import preview_file

    # dataset_path and axis are both required for 3D HDF5 datasets
    png = preview_file(
        "experiment.h5",
        dataset_path="data/subject01/run1/bold",
        axis=2,
        slice_index=10,
    )

    with open("preview.png", "wb") as f:
        f.write(png)
    ```

=== "NumPy .npy"
    ```python
    from voxelkit import preview_file

    # axis defaults to 0
    png = preview_file("volume.npy", axis=0, slice_index=5)

    with open("preview.png", "wb") as f:
        f.write(png)
    ```

=== "NumPy .npz"
    ```python
    from voxelkit import preview_file

    # specify which array inside the archive
    png = preview_file("data.npz", array_name="X", axis=0)

    with open("preview.png", "wb") as f:
        f.write(png)
    ```

=== "TIFF"
    ```python
    from voxelkit import preview_file

    # 3D z-stack — pick an axis and slice
    png = preview_file("zstack.tiff", axis=0, slice_index=25)

    with open("preview.png", "wb") as f:
        f.write(png)
    ```

---

## Using the bytes directly (e.g. in a notebook)

```python
from io import BytesIO
from PIL import Image
from voxelkit import preview_file

png = preview_file("scan.nii.gz", plane="axial")
img = Image.open(BytesIO(png))
img.show()
```
