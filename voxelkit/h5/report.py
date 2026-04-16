"""HDF5 QA report generation."""

import os

import h5py
import numpy as np

from voxelkit.core.errors import ValidationError
from voxelkit.core.report import build_array_report
from voxelkit.core.types import FileReportResult
from voxelkit.core.validation import require_supported_extension


def _first_dataset_path(h5_file: h5py.File) -> str | None:
    """Return the first dataset path found in the file, if any."""
    first_path: str | None = None

    def _visitor(path: str, node) -> None:
        nonlocal first_path
        if first_path is None and isinstance(node, h5py.Dataset):
            first_path = path

    h5_file.visititems(_visitor)
    return first_path


def report(file_path: str, dataset_path: str | None = None) -> FileReportResult:
    """Generate a QA report for an HDF5 dataset."""
    require_supported_extension(
        file_path=file_path,
        extensions=(".h5", ".hdf5"),
        message="Unsupported file type. Please provide a .h5 or .hdf5 file.",
    )

    filename = os.path.basename(file_path)
    warnings: list[str] = []

    try:
        with h5py.File(file_path, "r") as h5_file:
            resolved_dataset_path = dataset_path
            if resolved_dataset_path is None:
                resolved_dataset_path = _first_dataset_path(h5_file)
                if resolved_dataset_path is None:
                    raise ValidationError(
                        "No readable dataset found in HDF5 file. Provide --dataset / dataset_path."
                    )
                warnings.append(
                    f"dataset_path not provided; using first dataset '{resolved_dataset_path}'."
                )

            if resolved_dataset_path not in h5_file:
                raise ValidationError(f"dataset_path not found: '{resolved_dataset_path}'.")

            node = h5_file[resolved_dataset_path]
            if isinstance(node, h5py.Group):
                raise ValidationError(
                    f"dataset_path '{resolved_dataset_path}' points to a group, not a dataset."
                )

            if not isinstance(node, h5py.Dataset):
                raise ValidationError(f"dataset_path '{resolved_dataset_path}' is not a valid dataset.")

            data = np.asarray(node[...])
    except OSError as exc:
        raise ValidationError("Invalid, corrupted, or unreadable HDF5 file.") from exc

    return build_array_report(
        array=data,
        filename=filename,
        format_name="hdf5",
        preview_supported=data.ndim in (2, 3),
        extra_warnings=warnings,
    )
