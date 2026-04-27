"""Shared file-format and extension helpers used across VoxelKit layers."""

from __future__ import annotations

from pathlib import Path
from typing import Literal, TypeAlias


FormatName: TypeAlias = Literal["hdf5", "nifti", "tiff", "numpy"]

# Keep extension ordering stable for CLI help text and predictable matching.
NIFTI_EXTENSIONS: tuple[str, ...] = (".nii.gz", ".nii")
HDF5_EXTENSIONS: tuple[str, ...] = (".h5", ".hdf5")
TIFF_EXTENSIONS: tuple[str, ...] = (".tif", ".tiff")
# Reserved for upcoming numpy format support.
NUMPY_EXTENSIONS: tuple[str, ...] = (".npy", ".npz")
SUPPORTED_DATA_EXTENSIONS: tuple[str, ...] = (
    NIFTI_EXTENSIONS + HDF5_EXTENSIONS + TIFF_EXTENSIONS + NUMPY_EXTENSIONS
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


def detect_format(file_path: str | Path) -> str:
    """Detect a known VoxelKit format name from file extension.

    Known formats:
        - nifti: .nii, .nii.gz
        - hdf5: .h5, .hdf5
        - tiff: .tif, .tiff
        - numpy: .npy, .npz

    Raises:
        ValueError: If the extension is unsupported.
    """
    if has_extension(file_path, HDF5_EXTENSIONS):
        return "hdf5"
    if has_extension(file_path, NIFTI_EXTENSIONS):
        return "nifti"
    if has_extension(file_path, TIFF_EXTENSIONS):
        return "tiff"
    if has_extension(file_path, NUMPY_EXTENSIONS):
        return "numpy"

    supported = ", ".join(NIFTI_EXTENSIONS + HDF5_EXTENSIONS + TIFF_EXTENSIONS)
    raise ValueError(f"Unsupported file extension. Supported extensions: {supported}")
