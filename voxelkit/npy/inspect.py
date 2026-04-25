"""NumPy file inspection for .npy and .npz inputs."""

from __future__ import annotations

import os
import numpy as np

from voxelkit.core.errors import ValidationError
from voxelkit.core.formats import NUMPY_EXTENSIONS, has_extension
from voxelkit.core.types import NpyInspectResult, NpzInspectResult
from voxelkit.core.validation import require_supported_extension


def _inspect_npy(file_path: str) -> NpyInspectResult:
    try:
        array = np.load(file_path, allow_pickle=False)
    except (OSError, ValueError) as exc:
        raise ValidationError("Invalid, corrupted, or unreadable NumPy file.") from exc

    values = np.asarray(array)
    return {
        "filename": os.path.basename(file_path),
        "format": "numpy",
        "shape": list(values.shape),
        "ndim": int(values.ndim),
        "dtype": str(values.dtype),
    }


def _inspect_npz(file_path: str) -> NpzInspectResult:
    try:
        with np.load(file_path, allow_pickle=False) as archive:
            arrays = []
            for name in archive.files:
                values = np.asarray(archive[name])
                arrays.append(
                    {
                        "name": name,
                        "shape": list(values.shape),
                        "ndim": int(values.ndim),
                        "dtype": str(values.dtype),
                    }
                )
    except (OSError, ValueError, KeyError) as exc:
        raise ValidationError("Invalid, corrupted, or unreadable NumPy file.") from exc

    return {
        "filename": os.path.basename(file_path),
        "format": "numpy",
        "arrays": arrays,
    }


def inspect(file_path: str) -> NpyInspectResult | NpzInspectResult:
    """Inspect a NumPy file and return metadata.

    For `.npy` files this returns shape/ndim/dtype metadata.
    For `.npz` files this returns an array inventory with name/shape/ndim/dtype.
    """
    require_supported_extension(
        file_path=file_path,
        extensions=NUMPY_EXTENSIONS,
        message="Unsupported file type. Please provide a .npy or .npz file.",
    )

    if has_extension(file_path, (".npz",)):
        return _inspect_npz(file_path)
    return _inspect_npy(file_path)
