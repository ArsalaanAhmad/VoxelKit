"""Public library entry points for VoxelKit format-dispatched operations."""

from typing import Any

from voxelkit.core.batch_report import report_batch
from voxelkit.core.formats import detect_format
from voxelkit.core.types import FileReportResult, H5InspectResult, NiftiMetadataResult
from voxelkit.h5 import inspect as inspect_h5
from voxelkit.h5 import preview as preview_h5
from voxelkit.h5 import report as report_h5
from voxelkit.nifti import inspect as nifti_metadata
from voxelkit.nifti import preview as preview_nifti
from voxelkit.nifti import report as report_nifti


def inspect(file_path: str) -> H5InspectResult | NiftiMetadataResult | dict[str, Any]:
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
        return inspect_h5(file_path)
    if format_name == "nifti":
        return nifti_metadata(file_path)
    raise ValueError("Unsupported file extension for inspect().")


def report_file(file_path: str, dataset_path: str | None = None) -> FileReportResult:
    """Generate a QA report by dispatching based on file extension.

    Args:
        file_path: Path to a supported imaging file.
        dataset_path: Optional HDF5 dataset path.

    Returns:
        Format-specific QA report dictionary.

    Raises:
        ValueError: If `file_path` does not use a supported extension.
    """
    format_name = detect_format(file_path)
    if format_name == "hdf5":
        return report_h5(file_path, dataset_path=dataset_path)
    if format_name == "nifti":
        return report_nifti(file_path)
    raise ValueError("Unsupported file extension for report_file().")


__all__ = [
    "inspect",
    "inspect_h5",
    "preview_h5",
    "report_h5",
    "nifti_metadata",
    "preview_nifti",
    "report_nifti",
    "report_file",
    "report_batch",
]
