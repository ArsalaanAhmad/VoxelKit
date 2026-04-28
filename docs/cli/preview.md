---
description: voxelkit preview — generate and save a PNG slice from any supported imaging file.
---

# voxelkit preview

```bash
voxelkit preview <file> --output preview.png
```

Generates a 2D PNG slice from your file and saves it to disk. The centre slice is used by default. You can control the plane, axis, and slice index with flags.

---

## Usage

```
voxelkit preview FILE --output OUTPUT [options]
```

### Arguments

| Argument | Description |
|---|---|
| `FILE` | Path to a supported file |

### Flags

| Flag | Format | Description |
|---|---|---|
| `--output PATH` | All | **Required.** Output `.png` file path |
| `--plane PLANE` | NIfTI only | One of `axial`, `coronal`, `sagittal`. Defaults to `axial` |
| `--dataset PATH` | HDF5 only | Dataset path inside the file, e.g. `data/subject01/run1/bold` |
| `--array NAME` | `.npz` only | Array name inside the archive |
| `--axis INT` | HDF5 / NumPy / TIFF | Axis to slice along (0, 1, or 2). Required for 3D HDF5 datasets |
| `--slice INT` | All | Slice index. Defaults to the centre slice |

!!! warning "Format-specific flags"
    `--plane` is NIfTI-only. `--dataset` is HDF5-only. `--array` is `.npz`-only. Passing the wrong flag for a format raises an error.

---

## Examples

=== "NIfTI"
    ```bash
    # centre axial slice (default)
    voxelkit preview bold.nii.gz --output preview.png

    # specific plane and slice
    voxelkit preview bold.nii.gz --plane coronal --slice 20 --output coronal.png
    ```

=== "HDF5"
    ```bash
    # dataset_path and axis required for 3D datasets
    voxelkit preview experiment.h5 \
      --dataset data/subject01/run1/bold \
      --axis 2 \
      --slice 10 \
      --output h5_preview.png
    ```

=== "NumPy .npy"
    ```bash
    voxelkit preview volume.npy --axis 0 --slice 5 --output npy_preview.png
    ```

=== "NumPy .npz"
    ```bash
    voxelkit preview data.npz --array X --axis 0 --output npz_preview.png
    ```

=== "TIFF"
    ```bash
    voxelkit preview zstack.tiff --axis 0 --slice 25 --output tiff_preview.png
    ```

---

## Output

The PNG is written to the path given by `--output`. Parent directories are created automatically if they don't exist. The image is grayscale, normalised to 0–255.
