from voxelkit.core.batch_report import report_batch
from voxelkit.h5 import inspect as inspect_h5
from voxelkit.h5 import preview as preview_h5
from voxelkit.h5 import report as report_h5
from voxelkit.nifti import inspect as nifti_metadata
from voxelkit.nifti import preview as preview_nifti
from voxelkit.nifti import report as report_nifti


def _detect_format(file_path: str) -> str:
    """Return normalized format key inferred from file extension."""
    lowered = file_path.lower()
    if lowered.endswith(".h5") or lowered.endswith(".hdf5"):
        return "hdf5"
    if lowered.endswith(".nii") or lowered.endswith(".nii.gz"):
        return "nifti"
    raise ValueError("Unsupported file extension.")


def inspect(file_path: str) -> dict:
    """Dispatch inspect() to the correct format module based on file extension.

    Inputs:
        file_path: Path to a supported imaging file.

    Output:
        Format-specific metadata dictionary.
    """
    format_name = _detect_format(file_path)
    if format_name == "hdf5":
        return inspect_h5(file_path)
    if format_name == "nifti":
        return nifti_metadata(file_path)
    raise ValueError("Unsupported file extension for inspect().")


def report_file(file_path: str, dataset_path: str | None = None) -> dict:
    """Dispatch report generation by file extension.

    Inputs:
        file_path: Path to a supported imaging file.
        dataset_path: Optional HDF5 dataset path.

    Output:
        Format-specific QA report dictionary.
    """
    format_name = _detect_format(file_path)
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
