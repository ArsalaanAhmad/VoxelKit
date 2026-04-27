"""Public library entry points for VoxelKit format-dispatched operations."""

from pathlib import Path
from typing import Any

from voxelkit.core.batch_report import report_batch
from voxelkit.core.errors import ValidationError
from voxelkit.core.formats import FormatName, detect_format
from voxelkit.core.types import (
    FileReportResult,
    H5InspectResult,
    NiftiMetadataResult,
    NpyInspectResult,
    NpzInspectResult,
    TiffInspectResult,
)
from voxelkit.h5 import inspect as inspect_h5
from voxelkit.h5 import preview as preview_h5
from voxelkit.h5 import report as report_h5
from voxelkit.nifti import inspect as nifti_metadata
from voxelkit.nifti import preview as preview_nifti
from voxelkit.nifti import report as report_nifti
from voxelkit.npy import inspect as inspect_npy
from voxelkit.npy import preview as preview_npy
from voxelkit.npy import report as report_npy
from voxelkit.tiff import inspect as inspect_tiff
from voxelkit.tiff import preview as preview_tiff
from voxelkit.tiff import report as report_tiff
from voxelkit.embedding import report as report_embedding
from voxelkit.embedding import preview as preview_embedding


def inspect_file(
    file_path: str | Path,
) -> H5InspectResult | NiftiMetadataResult | NpyInspectResult | NpzInspectResult | TiffInspectResult:
    """Inspect a supported file by routing to the corresponding format module.

    Args:
        file_path: Path to a supported imaging file.

    Returns:
        Format-specific metadata dictionary produced by the library module.

    Raises:
        ValueError: If `file_path` does not use a supported extension.
    """
    format_name = detect_format(file_path)
    if format_name == "hdf5":
        return inspect_h5(str(file_path))
    if format_name == "nifti":
        return nifti_metadata(str(file_path))
    if format_name == "numpy":
        return inspect_npy(str(file_path))
    if format_name == "tiff":
        return inspect_tiff(str(file_path))
    raise ValueError("Unsupported file extension for inspect().")


# Backward-compatible name.
inspect = inspect_file


def preview_file(
    file_path: str | Path,
    *,
    plane: str = "axial",
    dataset_path: str | None = None,
    array_name: str | None = None,
    axis: int | None = None,
    slice_index: int | None = None,
) -> bytes:
    """Generate a preview image by dispatching to the format-specific module."""
    format_name: FormatName = detect_format(file_path)

    if format_name == "nifti":
        if dataset_path is not None:
            raise ValidationError("dataset_path is only valid for HDF5 preview.")
        if array_name is not None:
            raise ValidationError("array_name is only valid for NumPy NPZ preview.")
        return preview_nifti(str(file_path), plane=plane, slice_index=slice_index)

    if format_name == "hdf5":
        if dataset_path is None:
            raise ValidationError("dataset_path is required for HDF5 preview.")
        if array_name is not None:
            raise ValidationError("array_name is only valid for NumPy NPZ preview.")
        if axis is None:
            raise ValidationError("axis is required for HDF5 preview.")
        return preview_h5(
            file_path=str(file_path),
            dataset_path=dataset_path,
            axis=axis,
            slice_index=slice_index,
        )

    if format_name == "numpy":
        if dataset_path is not None:
            raise ValidationError("dataset_path is only valid for HDF5 preview.")
        if axis is None:
            axis = 0
        return preview_npy(
            file_path=str(file_path),
            array_name=array_name,
            axis=axis,
            slice_index=slice_index,
        )

    if format_name == "tiff":
        if dataset_path is not None:
            raise ValidationError("dataset_path is only valid for HDF5 preview.")
        if array_name is not None:
            raise ValidationError("array_name is only valid for NumPy NPZ preview.")
        if axis is None:
            axis = 0
        return preview_tiff(
            file_path=str(file_path),
            axis=axis,
            slice_index=slice_index,
        )

    raise ValueError("Unsupported file extension for preview_file().")


def report_file(
    file_path: str | Path,
    dataset_path: str | None = None,
    array_name: str | None = None,
) -> FileReportResult:
    """Generate a QA report by dispatching based on file extension.

    Args:
        file_path: Path to a supported imaging file.
        dataset_path: Optional HDF5 dataset path.
        array_name: Optional NumPy NPZ array name.

    Returns:
        Format-specific QA report dictionary.

    Raises:
        ValueError: If `file_path` does not use a supported extension.
    """
    format_name: FormatName = detect_format(file_path)
    if format_name == "hdf5":
        if array_name is not None:
            raise ValidationError("array_name is only valid for NumPy NPZ report.")
        return report_h5(str(file_path), dataset_path=dataset_path)
    if format_name == "nifti":
        if dataset_path is not None:
            raise ValidationError("dataset_path is only valid for HDF5 report.")
        if array_name is not None:
            raise ValidationError("array_name is only valid for NumPy NPZ report.")
        return report_nifti(str(file_path))
    if format_name == "numpy":
        if dataset_path is not None:
            raise ValidationError("dataset_path is only valid for HDF5 report.")
        return report_npy(str(file_path), array_name=array_name)
    if format_name == "tiff":
        if dataset_path is not None:
            raise ValidationError("dataset_path is only valid for HDF5 report.")
        if array_name is not None:
            raise ValidationError("array_name is only valid for NumPy NPZ report.")
        return report_tiff(str(file_path))
    raise ValueError("Unsupported file extension for report_file().")


__all__ = [
    "inspect_file",
    "preview_file",
    "inspect",
    "inspect_h5",
    "preview_h5",
    "report_h5",
    "inspect_npy",
    "preview_npy",
    "report_npy",
    "nifti_metadata",
    "preview_nifti",
    "report_nifti",
    "inspect_tiff",
    "preview_tiff",
    "report_tiff",
    "report_embedding",
    "preview_embedding",
    "report_file",
    "report_batch",
]
