---
description: dicom_to_nifti -- convert a DICOM file or series directory into a NIfTI volume.
---

# dicom_to_nifti

```python
from voxelkit.dicom import dicom_to_nifti

summary = dicom_to_nifti(
    input_path="./series/",
    output_path="./volume.nii.gz",
)
print(summary["shape"])      # [rows, cols, slices]
print(summary["voxel_size"]) # [row_mm, col_mm, slice_mm]
```

Converts a `.dcm` file or a series directory into a NIfTI-1 file. The affine matrix is built from `ImageOrientationPatient`, `PixelSpacing`, `SliceThickness`, and `ImagePositionPatient`, with the standard DICOM-LPS to NIfTI-RAS sign flip applied.

---

## Signature

```python
def dicom_to_nifti(
    input_path: str | Path,
    output_path: str | Path,
) -> ConversionSummary
```

## Parameters

| Parameter | Type | Description |
|---|---|---|
| `input_path` | `str` or `Path` | Path to a `.dcm` file or series directory |
| `output_path` | `str` or `Path` | Output path for the `.nii` or `.nii.gz` file |

---

## Return value

```python
{
    "shape": [512, 512, 128],
    "voxel_size": [0.7, 0.7, 1.2],
    "warnings": []
}
```

The `warnings` list is populated when DICOM headers are incomplete. For example, if `ImagePositionPatient` is missing the affine falls back to a default and a warning is added to tell you.

---

## Example

```python
from voxelkit.dicom import dicom_to_nifti

summary = dicom_to_nifti("./series/", "./output.nii.gz")

print(summary["shape"])       # [512, 512, 128]
print(summary["voxel_size"])  # [0.7, 0.7, 1.2]

if summary["warnings"]:
    print("Header warnings:")
    for w in summary["warnings"]:
        print(" ", w)
```

---

## Notes and limitations

This function handles the common single-series case well. For anything more complex, `dcm2niix` is the more battle-tested option. Known limitations:

- **Multi-echo or 4D series** are not automatically split. Slices are assembled in Z order and returned as a 3D volume regardless of echo time or time point.
- **Diffusion series** with varying gradient directions are assembled the same way. Use `dcm2niix` if you need per-direction bval/bvec files.
- **Compressed transfer syntaxes** (JPEG, JPEG 2000, RLE) depend on your `pydicom` installation having the correct pixel data handlers available.

See [voxelkit convert (CLI)](../../cli/convert.md) for the equivalent command-line usage.
