---
description: preview_dicom -- render a PNG slice from a DICOM file or series.
---

# preview_dicom

```python
from voxelkit import preview_dicom

png_bytes = preview_dicom("scan.dcm")
with open("preview.png", "wb") as f:
    f.write(png_bytes)
```

Returns a PNG as raw bytes. For a single `.dcm` file you get the 2D pixel data rendered as an image. For a series directory VoxelKit assembles the 3D volume first and then extracts one slice from it.

---

## Signature

```python
def preview_dicom(
    file_path: str | Path,
    *,
    axis: int = 0,
    slice_index: int | None = None,
    as_array: bool = False,
) -> bytes | np.ndarray
```

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `file_path` | `str` or `Path` | required | Path to a `.dcm` file or series directory |
| `axis` | `int` | `0` | Which axis to slice along. Ignored for single 2D files. |
| `slice_index` | `int` or `None` | `None` | Index of the slice to extract. Defaults to the centre slice. |
| `as_array` | `bool` | `False` | When `True`, returns a `uint8` NumPy array instead of PNG bytes. |

---

## Examples

```python
from voxelkit import preview_dicom

# Single .dcm file
png = preview_dicom("scan.dcm")

# Series directory, default axis (0 = slice axis)
png = preview_dicom("./series/")

# Coronal view
png = preview_dicom("./series/", axis=1)

# Pick a specific slice
png = preview_dicom("./series/", axis=0, slice_index=64)

# Get a NumPy array for embedding in your own report or GUI
arr = preview_dicom("./series/", as_array=True)
# arr.shape == (rows, cols), dtype uint8

with open("preview.png", "wb") as f:
    f.write(png)
```

The output image is grayscale and normalised to 0-255 regardless of the original bit depth or window level.
