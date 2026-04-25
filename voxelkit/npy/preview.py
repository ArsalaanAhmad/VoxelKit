"""NumPy preview rendering for .npy and .npz arrays."""

from __future__ import annotations

import numpy as np

from voxelkit.core.errors import ValidationError
from voxelkit.core.formats import NUMPY_EXTENSIONS, has_extension
from voxelkit.core.image_utils import to_png_bytes
from voxelkit.core.normalization import normalize_to_uint8
from voxelkit.core.validation import require_supported_extension, resolve_slice_index


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


def _extract_preview_slice(values: np.ndarray, axis: int, slice_index: int | None) -> np.ndarray:
    if values.ndim == 2:
        return np.asarray(values, dtype=np.float32)

    if values.ndim != 3:
        raise ValidationError("Only 2D or 3D NumPy arrays are supported for preview.")

    if axis not in (0, 1, 2):
        raise ValidationError("Invalid axis for 3D array. Axis must be 0, 1, or 2.")

    resolved_index = resolve_slice_index(
        length=values.shape[axis],
        slice_index=slice_index,
        context=f"axis {axis}",
    )

    if axis == 0:
        return np.asarray(values[resolved_index, :, :], dtype=np.float32)
    if axis == 1:
        return np.asarray(values[:, resolved_index, :], dtype=np.float32)
    return np.asarray(values[:, :, resolved_index], dtype=np.float32)


def preview(
    file_path: str,
    array_name: str | None = None,
    axis: int = 0,
    slice_index: int | None = None,
    as_array: bool = False,
) -> bytes | np.ndarray:
    """Generate a NumPy preview as PNG bytes or uint8 array.

    Args:
        file_path: Path to a .npy or .npz file.
        array_name: Optional array selector for .npz containers.
        axis: Slice axis for 3D arrays.
        slice_index: Optional index for 3D arrays; defaults to center slice.
        as_array: When True, return a uint8 array instead of PNG bytes.
    """
    require_supported_extension(
        file_path=file_path,
        extensions=NUMPY_EXTENSIONS,
        message="Unsupported file type. Please provide a .npy or .npz file.",
    )

    values = _load_numpy_array(file_path=file_path, array_name=array_name)
    slice_2d = _extract_preview_slice(values=values, axis=axis, slice_index=slice_index)
    normalized = normalize_to_uint8(slice_2d)
    if as_array:
        return normalized
    return to_png_bytes(normalized)
