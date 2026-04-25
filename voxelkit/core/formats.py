"""Shared file-format and extension helpers used across VoxelKit layers."""

from __future__ import annotations

from typing import Literal, TypeAlias


FormatName: TypeAlias = Literal["hdf5", "nifti"]

# Keep extension ordering stable for CLI help text and predictable matching.
NIFTI_EXTENSIONS: tuple[str, ...] = (".nii.gz", ".nii")
HDF5_EXTENSIONS: tuple[str, ...] = (".h5", ".hdf5")
SUPPORTED_DATA_EXTENSIONS: tuple[str, ...] = NIFTI_EXTENSIONS + HDF5_EXTENSIONS


def has_extension(file_path_or_name: str, extensions: tuple[str, ...]) -> bool:
    """Return True when a path or filename matches any extension in `extensions`."""
    return file_path_or_name.lower().endswith(extensions)


def first_matching_extension(file_path_or_name: str, extensions: tuple[str, ...]) -> str | None:
    """Return the first matching extension in input order, or None if no match."""
    lowered = file_path_or_name.lower()
    for extension in extensions:
        if lowered.endswith(extension):
            return extension
    return None


def detect_format(file_path: str) -> FormatName:
    """Detect VoxelKit format key from file extension.

    Raises:
        ValueError: If the extension is unsupported.
    """
    if has_extension(file_path, HDF5_EXTENSIONS):
        return "hdf5"
    if has_extension(file_path, NIFTI_EXTENSIONS):
        return "nifti"
    raise ValueError("Unsupported file extension.")
