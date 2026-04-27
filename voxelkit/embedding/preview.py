"""Embedding preview: render a (N_samples, D_dims) matrix as a PNG heatmap.

Each row is a sample, each column a dimension. Values are normalised per-
column (not globally) so that active dimensions show contrast while dead
dimensions (std ≈ 0) appear as a uniform grey stripe — making them instantly
visible. For large matrices only a random subset of rows is rendered.
"""

from __future__ import annotations

import numpy as np

from voxelkit.core.errors import ValidationError
from voxelkit.core.image_utils import to_png_bytes
from voxelkit.core.validation import require_supported_extension

# Maximum number of sample rows rendered in the preview image. Keeps the PNG
# small and generation fast even for million-sample embedding files.
_MAX_PREVIEW_SAMPLES = 256


def _load_embedding(file_path: str) -> np.ndarray:
    """Load a .npy file and validate it is a 2D numeric array."""
    try:
        array = np.asarray(np.load(file_path, allow_pickle=False))
    except (OSError, ValueError) as exc:
        raise ValidationError("Invalid or unreadable NumPy file.") from exc

    if not np.issubdtype(array.dtype, np.number):
        raise ValidationError("Embedding array must contain numeric values.")

    if array.ndim != 2:
        raise ValidationError(
            f"Embedding preview requires a 2D array (N_samples, D_dims), "
            f"but got {array.ndim}D array with shape {array.shape}."
        )

    return array


def _per_column_normalize(matrix: np.ndarray) -> np.ndarray:
    """Normalise each column of a float matrix to the [0, 255] uint8 range.

    Per-column (per-dimension) normalisation means each dimension is scaled
    independently. This makes dead dimensions (constant values) show as a
    uniform mid-grey stripe, while active dimensions show contrast — far more
    informative than global normalisation which would wash out the structure.

    NaN and Inf values are replaced with the column's finite minimum before
    normalisation so they don't silently break the scaling arithmetic.
    """
    result = matrix.astype(np.float64)

    for col_idx in range(result.shape[1]):
        col = result[:, col_idx]
        col_min = np.nanmin(col) if np.any(np.isfinite(col)) else 0.0
        # Replace non-finite values with the column minimum so they map to 0.
        col = np.where(np.isfinite(col), col, col_min)
        col_range = col.max() - col.min()
        if col_range > 0:
            col = (col - col.min()) / col_range * 255.0
        else:
            # Constant column → mid-grey (128) so it's distinguishable from
            # true zeros (0) and maximally active dimensions (255).
            col = np.full_like(col, 128.0)
        result[:, col_idx] = col

    return result.astype(np.uint8)


def preview(
    file_path: str,
    max_samples: int = _MAX_PREVIEW_SAMPLES,
    seed: int = 0,
    as_array: bool = False,
) -> bytes | np.ndarray:
    """Render an embedding matrix as a per-column-normalised PNG heatmap.

    Each pixel row = one sample, each pixel column = one embedding dimension.
    Dead dimensions appear as uniform mid-grey stripes; active dimensions show
    variation across samples.

    For large matrices, `max_samples` rows are drawn at random using `seed`
    for reproducibility.

    Args:
        file_path:   Path to a .npy file with a 2D (N_samples, D_dims) array.
        max_samples: Maximum number of sample rows to render. Defaults to 256.
        seed:        Random seed for reproducible row sampling. Defaults to 0.
        as_array:    When True, return the uint8 NumPy array instead of PNG bytes.

    Returns:
        PNG-encoded bytes, or a uint8 NumPy array when `as_array` is True.

    Raises:
        ValidationError: If the file is not a 2D numeric .npy array.
        UnsupportedFormatError: If the file extension is not .npy.
    """
    require_supported_extension(
        file_path=file_path,
        extensions=(".npy",),
        message="Embedding preview requires a .npy file.",
    )

    array = _load_embedding(file_path)
    n_samples = array.shape[0]

    if n_samples > max_samples:
        rng = np.random.default_rng(seed)
        indices = rng.choice(n_samples, size=max_samples, replace=False)
        indices.sort()   # keep sample order so the heatmap reads top-to-bottom
        array = array[indices]

    image = _per_column_normalize(array.astype(np.float64))

    if as_array:
        return image
    return to_png_bytes(image)
