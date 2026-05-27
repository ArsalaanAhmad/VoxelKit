---
description: voxelkit convert — turn a DICOM file or series directory into a NIfTI volume.
---

# voxelkit convert

```bash
voxelkit convert <input> <output.nii.gz>
```

Converts a single DICOM file or a directory of DICOM slices into a NIfTI-1 volume. Builds the affine matrix from the DICOM headers (`ImageOrientationPatient`, `PixelSpacing`, `SliceThickness`, `ImagePositionPatient`) and applies the standard DICOM-LPS → NIfTI-RAS sign flip.

This is a small built-in converter, not a replacement for `dcm2niix`. It covers the common case — a sorted axial series with regular slice spacing — and surfaces any header gaps in a `warnings` list rather than silently fabricating physical coordinates.

---

## Usage

```
voxelkit convert INPUT OUTPUT
```

### Arguments

| Argument | Description |
|---|---|
| `INPUT`  | Path to a `.dcm` file or a directory of DICOM slices |
| `OUTPUT` | Destination NIfTI path. Must end in `.nii` (uncompressed) or `.nii.gz` (gzipped). |

---

## Examples

```bash
# Single .dcm -> 2-D NIfTI
voxelkit convert scan.dcm scan.nii.gz

# Series directory -> 3-D NIfTI volume
voxelkit convert ./series/ volume.nii.gz

# Uncompressed output
voxelkit convert ./series/ volume.nii
```

Output JSON summary:

```json
{
  "input_path": "/data/scan.dcm",
  "output_path": "/data/scan.nii.gz",
  "source": "file",
  "shape": [512, 512],
  "voxel_size": [0.7, 0.7, 1.0],
  "slice_count": 1,
  "warnings": []
}
```

`warnings` will list any DICOM tags that were missing and had to fall back to defaults — for example, `"PixelSpacing missing — using 1.0 mm for in-plane spacing."`

---

## How the affine is built

For an axial CT/MR series:

```
col 0 = row direction × pixel_spacing[0]    (in-plane row step)
col 1 = column direction × pixel_spacing[1] (in-plane column step)
col 2 = slice direction × slice_thickness   (between-slice step)
col 3 = ImagePositionPatient of the first slice (origin)
```

The first two rows are negated to map DICOM-LPS to NIfTI-RAS.

---

!!! tip "When to reach for dcm2niix instead"
    If you need vendor-specific quirk handling (b-vector reconstruction for DWI, slice-timing extraction for fMRI, 4-D temporal sorting, sub-millisecond timing), use `dcm2niix`. VoxelKit's converter is intentionally simple.
