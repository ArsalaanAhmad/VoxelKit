"""TIFF preview rendering for .tif and .tiff images.

Supports both 2D TIFFs (single page, grayscale or RGB) and 3D TIFFs
(multi-page z-stacks where each page is one Z-slice). The output is always
a PNG-encoded image of a single 2D slice.
"""

from __future__ import annotations

import numpy as np
import tifffile

from voxelkit.core.errors import ValidationError
from voxelkit.core.formats import TIFF_EXTENSIONS
from voxelkit.core.image_utils import to_png_bytes
from voxelkit.core.normalization import normalize_to_uint8
from voxelkit.core.validation import require_supported_extension, resolve_slice_index


def _load_tiff_array(file_path: str) -> np.ndarray:
    """Read all pixel data from a TIFF file into a NumPy array.

    `tifffile.imread` is the canonical way to load a TIFF as a NumPy array.
    It handles both single-page and multi-page files transparently, returning:
      - shape (H, W)       for a 2D grayscale image
      - shape (H, W, C)    for a 2D colour image (e.g. RGB with C=3)
      - shape (Z, H, W)    for a z-stack (multi-page grayscale)
      - shape (Z, H, W, C) for a multi-page colour stack
    """
    try:
        return tifffile.imread(file_path)
    except tifffile.TiffFileError as exc:
        raise ValidationError("Invalid or unreadable TIFF file.") from exc
    except (OSError, ValueError) as exc:
        raise ValidationError("Could not open TIFF file.") from exc


def _extract_preview_slice(
    array: np.ndarray,
    axis: int,
    slice_index: int | None,
) -> np.ndarray:
    """Extract a single 2D plane from a TIFF array for preview rendering.

    For 2D arrays (including colour images whose channel dimension is treated
    as part of the 2D frame) the array is returned as-is after squeezing any
    trailing channel dimension down to a single-channel grayscale.

    For 3D arrays (Z, H, W) an index along `axis` selects the slice. For a
    z-stack the natural axis is 0 (one page per Z position).

    Args:
        array:       NumPy array loaded from the TIFF file.
        axis:        Which dimension to slice when the array is 3D.
        slice_index: Index of the slice to extract; defaults to centre.

    Returns:
        A float32 2D array ready for normalisation and PNG encoding.

    Raises:
        ValidationError: For unsupported dimensionality or out-of-bounds index.
    """
    if array.ndim == 2:
        return np.asarray(array, dtype=np.float32)

    if array.ndim == 3:
        # Colour image (H, W, C) — collapse channels to grayscale before slicing.
        if array.shape[-1] in (3, 4):
            return np.mean(array, axis=-1).astype(np.float32)

        # Z-stack (Z, H, W) — extract one plane along the requested axis.
        if axis not in (0, 1, 2):
            raise ValidationError("Invalid axis for 3D TIFF. Axis must be 0, 1, or 2.")

        resolved_index = resolve_slice_index(
            length=array.shape[axis],
            slice_index=slice_index,
            context=f"axis {axis}",
        )

        if axis == 0:
            return np.asarray(array[resolved_index, :, :], dtype=np.float32)
        if axis == 1:
            return np.asarray(array[:, resolved_index, :], dtype=np.float32)
        return np.asarray(array[:, :, resolved_index], dtype=np.float32)

    raise ValidationError(
        f"TIFF arrays with {array.ndim} dimensions are not supported for preview. "
        "Only 2D and 3D arrays are supported."
    )


def preview(
    file_path: str,
    axis: int = 0,
    slice_index: int | None = None,
    as_array: bool = False,
) -> bytes | np.ndarray:
    """Generate a PNG preview from a TIFF file.

    For 2D TIFFs the entire image is rendered. For 3D z-stacks a single slice
    is extracted along `axis` (default 0, the Z axis). The pixel data is
    normalised to the [0, 255] uint8 range before encoding.

    Args:
        file_path:   Path to a .tif or .tiff file.
        axis:        Slice axis for 3D arrays (0=Z, 1=Y, 2=X). Ignored for 2D.
        slice_index: Index of the slice; defaults to the centre of that axis.
        as_array:    When True, return the uint8 NumPy array instead of PNG bytes.

    Returns:
        PNG-encoded bytes, or a uint8 NumPy array when `as_array` is True.

    Raises:
        ValidationError: If the extension is unsupported, the file is
            unreadable, or the dimensionality is not supported.
    """
    require_supported_extension(
        file_path=file_path,
        extensions=TIFF_EXTENSIONS,
        message="Unsupported file type. Please provide a .tif or .tiff file.",
    )

    array = _load_tiff_array(file_path)
    slice_2d = _extract_preview_slice(array=array, axis=axis, slice_index=slice_index)
    normalized = normalize_to_uint8(slice_2d)

    if as_array:
        return normalized
    return to_png_bytes(normalized)
