from voxelkit.h5 import inspect as inspect_h5
from voxelkit.h5 import preview as preview_h5
from voxelkit.nifti import inspect as nifti_metadata
from voxelkit.nifti import preview as preview_nifti


def inspect(file_path: str) -> dict:
    """Dispatch inspect() to the correct format module based on file extension.

    Inputs:
        file_path: Path to a supported imaging file.

    Output:
        Format-specific metadata dictionary.
    """
    lowered = file_path.lower()
    if lowered.endswith(".h5") or lowered.endswith(".hdf5"):
        return inspect_h5(file_path)
    if lowered.endswith(".nii") or lowered.endswith(".nii.gz"):
        return nifti_metadata(file_path)
    raise ValueError("Unsupported file extension for inspect().")


__all__ = [
    "inspect",
    "inspect_h5",
    "preview_h5",
    "nifti_metadata",
    "preview_nifti",
]
