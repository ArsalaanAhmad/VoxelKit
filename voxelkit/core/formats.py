"""Shared file-format and extension helpers used across VoxelKit layers."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, TypeAlias


FormatName: TypeAlias = Literal["hdf5", "nifti", "tiff", "numpy", "dicom"]

# Keep extension ordering stable for CLI help text and predictable matching.
NIFTI_EXTENSIONS: tuple[str, ...] = (".nii.gz", ".nii")
HDF5_EXTENSIONS: tuple[str, ...] = (".h5", ".hdf5")
TIFF_EXTENSIONS: tuple[str, ...] = (".tif", ".tiff")
NUMPY_EXTENSIONS: tuple[str, ...] = (".npy", ".npz")
DICOM_EXTENSIONS: tuple[str, ...] = (".dcm",)
SUPPORTED_DATA_EXTENSIONS: tuple[str, ...] = (
    NIFTI_EXTENSIONS + HDF5_EXTENSIONS + TIFF_EXTENSIONS + NUMPY_EXTENSIONS + DICOM_EXTENSIONS
)


def _normalize_path_text(file_path_or_name: str | Path) -> str:
    """Normalize input path-like value to lowercase string for suffix matching."""
    return str(file_path_or_name).lower()


def has_extension(file_path_or_name: str | Path, extensions: tuple[str, ...]) -> bool:
    """Return True when a path or filename matches any extension in `extensions`."""
    return _normalize_path_text(file_path_or_name).endswith(extensions)


def first_matching_extension(file_path_or_name: str | Path, extensions: tuple[str, ...]) -> str | None:
    """Return the first matching extension in input order, or None if no match."""
    lowered = _normalize_path_text(file_path_or_name)
    for extension in extensions:
        if lowered.endswith(extension):
            return extension
    return None


def directory_contains_dicom(directory: str | Path) -> bool:
    """Return True when a directory has at least one .dcm file at its top level.

    Used by `detect_format` to recognise a DICOM series directory (one folder
    of per-slice .dcm files forming a single volume). The check is shallow on
    purpose — recursing into arbitrary trees would mis-identify a parent
    folder of mixed datasets as a single series. Callers that need recursive
    discovery should use the batch-report scanner instead.
    """
    path = Path(directory)
    try:
        for entry in path.iterdir():
            if entry.is_file() and entry.suffix.lower() == ".dcm":
                return True
    except (OSError, PermissionError):
        return False
    return False


def detect_format(file_path: str | Path) -> str:
    """Detect a known VoxelKit format name from a file or directory path.

    Known formats:
        - nifti: .nii, .nii.gz
        - hdf5: .h5, .hdf5
        - tiff: .tif, .tiff
        - numpy: .npy, .npz
        - dicom: a .dcm file, OR a directory containing .dcm files (series)

    Raises:
        ValueError: If the extension/contents are unsupported.
    """
    path = Path(file_path)
    if path.is_dir():
        if directory_contains_dicom(path):
            return "dicom"
        raise ValueError(
            f"Directory does not contain a recognised VoxelKit format: {file_path}"
        )

    if has_extension(file_path, HDF5_EXTENSIONS):
        return "hdf5"
    if has_extension(file_path, NIFTI_EXTENSIONS):
        return "nifti"
    if has_extension(file_path, TIFF_EXTENSIONS):
        return "tiff"
    if has_extension(file_path, NUMPY_EXTENSIONS):
        return "numpy"
    if has_extension(file_path, DICOM_EXTENSIONS):
        return "dicom"

    supported = ", ".join(
        NIFTI_EXTENSIONS + HDF5_EXTENSIONS + TIFF_EXTENSIONS + NUMPY_EXTENSIONS + DICOM_EXTENSIONS
    )
    raise ValueError(f"Unsupported file extension. Supported extensions: {supported}")
