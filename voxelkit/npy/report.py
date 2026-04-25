"""NumPy QA report generation for .npy and .npz arrays."""

from __future__ import annotations

import os

import numpy as np

from voxelkit.core.errors import ValidationError
from voxelkit.core.formats import NUMPY_EXTENSIONS, has_extension
from voxelkit.core.report import build_array_report
from voxelkit.core.types import FileReportResult
from voxelkit.core.validation import require_supported_extension


def _resolve_npz_array_name(archive: np.lib.npyio.NpzFile, array_name: str | None) -> str:
    names = list(archive.files)
    if not names:
        raise ValidationError("NPZ archive contains no arrays.")

    if array_name is not None:
        if array_name not in archive:
            available = ", ".join(names)
            raise ValidationError(f"array_name not found: '{array_name}'. Available arrays: {available}")
        return array_name

    if len(names) == 1:
        return names[0]

    raise ValidationError("array_name is required for NPZ files containing multiple arrays.")


def _load_numpy_array(file_path: str, array_name: str | None) -> np.ndarray:
    try:
        if has_extension(file_path, (".npz",)):
            with np.load(file_path, allow_pickle=False) as archive:
                resolved_name = _resolve_npz_array_name(archive, array_name)
                return np.asarray(archive[resolved_name])

        if array_name is not None:
            raise ValidationError("array_name is only valid for .npz files.")

        return np.asarray(np.load(file_path, allow_pickle=False))
    except ValidationError:
        raise
    except (OSError, ValueError, KeyError) as exc:
        raise ValidationError("Invalid, corrupted, or unreadable NumPy file.") from exc


def report(file_path: str, array_name: str | None = None) -> FileReportResult:
    """Generate a QA report for a .npy or .npz array payload."""
    require_supported_extension(
        file_path=file_path,
        extensions=NUMPY_EXTENSIONS,
        message="Unsupported file type. Please provide a .npy or .npz file.",
    )

    values = _load_numpy_array(file_path=file_path, array_name=array_name)
    return build_array_report(
        array=values,
        filename=os.path.basename(file_path),
        format_name="numpy",
        preview_supported=values.ndim in (2, 3),
    )
