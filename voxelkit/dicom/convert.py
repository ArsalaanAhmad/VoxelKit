"""Convert DICOM (single .dcm or a series directory) into a NIfTI volume.

This is a deliberately small implementation, not a replacement for
`dcm2niix`. It covers the common case — a sorted axial CT/MR series with
a regular slice spacing — and emits a NIfTI-1 file with:

- pixel data transposed from `(slice, row, col)` to NIfTI's expected
  `(row, col, slice)`;
- a 4×4 affine built from `ImageOrientationPatient`, `PixelSpacing`,
  `SliceThickness`, and `ImagePositionPatient` of the first slice;
- a DICOM-LPS → NIfTI-RAS sign flip applied to the first two rows of the
  affine, matching the convention used by every major converter.

When headers are missing or incomplete, the function falls back to an
identity-scaled affine so the volume is at least viewable, and surfaces
the gap via the returned summary's `warnings` list. It does not silently
fabricate physical coordinates.
"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

import nibabel as nib
import numpy as np

from voxelkit.core.errors import ValidationError
from voxelkit.dicom.loader import load_dicom


class DicomConvertResult(TypedDict):
    """Summary of a DICOM-to-NIfTI conversion."""

    input_path: str
    output_path: str
    source: str
    shape: list[int]
    voxel_size: list[float]
    slice_count: int
    warnings: list[str]


def dicom_to_nifti(input_path: str | Path, output_path: str | Path) -> DicomConvertResult:
    """Convert a `.dcm` file or a DICOM series directory into a NIfTI file.

    The output filename's extension picks the encoding:
        - `.nii`     -> uncompressed NIfTI-1
        - `.nii.gz`  -> gzipped NIfTI-1

    Args:
        input_path: Path to a `.dcm` file or a directory of slices.
        output_path: Destination `.nii` or `.nii.gz` path. Parent directory
            is created if it does not exist.

    Returns:
        A `DicomConvertResult` with the saved shape, derived voxel size,
        and any data-quality warnings discovered while building the affine.

    Raises:
        ValidationError: when the input cannot be loaded, the output path
            has an unsupported extension, or the source data is below 2-D.
    """
    output = Path(output_path)
    if not (output.name.lower().endswith(".nii") or output.name.lower().endswith(".nii.gz")):
        raise ValidationError(
            f"Output must end in .nii or .nii.gz, got: {output.name}"
        )
    output.parent.mkdir(parents=True, exist_ok=True)

    loaded = load_dicom(input_path)
    array = loaded.pixel_array

    if array.ndim < 2:
        raise ValidationError("DICOM data must be at least 2-dimensional for NIfTI conversion.")

    warnings: list[str] = []
    affine, voxel_size = _build_affine(
        dataset=loaded.representative_dataset,
        ndim=array.ndim,
        warnings=warnings,
    )

    # NIfTI convention puts slice as the LAST axis (rows, cols, slices).
    # Our series loader stacks slices on axis 0 (slices, rows, cols), so we
    # transpose 3-D arrays. 2-D arrays are saved as 2-D NIfTI.
    if array.ndim == 3:
        nifti_array = np.transpose(array, (1, 2, 0))
    else:
        nifti_array = array

    nifti_array = _to_nifti_dtype(nifti_array)

    image = nib.Nifti1Image(nifti_array, affine)
    nib.save(image, str(output))

    return {
        "input_path": str(Path(input_path).resolve()),
        "output_path": str(output.resolve()),
        "source": loaded.source,
        "shape": list(nifti_array.shape),
        "voxel_size": voxel_size,
        "slice_count": loaded.slice_count,
        "warnings": warnings,
    }


def _build_affine(
    *, dataset, ndim: int, warnings: list[str]
) -> tuple[np.ndarray, list[float]]:
    """Build a 4x4 NIfTI affine from DICOM header tags.

    The affine columns are:
        col 0 = row direction × pixel_spacing[0]    (in-plane row step)
        col 1 = column direction × pixel_spacing[1] (in-plane column step)
        col 2 = slice direction × slice_thickness   (between-slice step)
        col 3 = origin (ImagePositionPatient of first slice)

    The DICOM patient frame is LPS. NIfTI uses RAS. The conversion is two
    sign flips: negate the first row and second row of the affine (so the
    L/R and A/P axes swap direction; superior stays the same).
    """
    pixel_spacing = getattr(dataset, "PixelSpacing", None)
    slice_thickness = getattr(dataset, "SliceThickness", None)
    orientation = getattr(dataset, "ImageOrientationPatient", None)
    position = getattr(dataset, "ImagePositionPatient", None)

    row_spacing = float(pixel_spacing[0]) if pixel_spacing else 1.0
    col_spacing = float(pixel_spacing[1]) if pixel_spacing else 1.0
    slice_spacing = float(slice_thickness) if slice_thickness else 1.0

    if pixel_spacing is None:
        warnings.append("PixelSpacing missing — using 1.0 mm for in-plane spacing.")
    if slice_thickness is None and ndim == 3:
        warnings.append("SliceThickness missing — using 1.0 mm for slice spacing.")

    if orientation is not None and len(orientation) >= 6:
        row_direction = np.array([float(orientation[0]), float(orientation[1]), float(orientation[2])])
        col_direction = np.array([float(orientation[3]), float(orientation[4]), float(orientation[5])])
        slice_direction = np.cross(row_direction, col_direction)
    else:
        warnings.append("ImageOrientationPatient missing — using identity orientation.")
        row_direction = np.array([1.0, 0.0, 0.0])
        col_direction = np.array([0.0, 1.0, 0.0])
        slice_direction = np.array([0.0, 0.0, 1.0])

    if position is not None and len(position) >= 3:
        origin = np.array([float(position[0]), float(position[1]), float(position[2])])
    else:
        warnings.append("ImagePositionPatient missing — placing origin at (0, 0, 0).")
        origin = np.array([0.0, 0.0, 0.0])

    affine = np.eye(4, dtype=np.float64)
    affine[:3, 0] = row_direction * row_spacing
    affine[:3, 1] = col_direction * col_spacing
    affine[:3, 2] = slice_direction * slice_spacing
    affine[:3, 3] = origin

    # LPS -> RAS: invert the first two physical axes.
    affine[0, :] *= -1.0
    affine[1, :] *= -1.0

    voxel_size = [row_spacing, col_spacing, slice_spacing]
    return affine, voxel_size


def _to_nifti_dtype(array: np.ndarray) -> np.ndarray:
    """Cast unusual DICOM dtypes into ones nibabel writes without complaining.

    DICOMs commonly arrive as `uint16` (CT/MR) or `int16`. Those are
    NIfTI-native. Some vendors emit float64 or bool, which round-trip fine
    but cost more space; we leave them as-is rather than guessing. The
    one cast we must perform is bool -> uint8, since nibabel rejects bool.
    """
    if array.dtype == np.bool_:
        return array.astype(np.uint8)
    return array
