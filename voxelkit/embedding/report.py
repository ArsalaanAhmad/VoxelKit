"""Embedding-aware QA report for (N_samples, D_dims) NumPy arrays.

Standard spatial QA (min/max/mean/std across all values) misses embedding-
specific failure modes because it treats the array as a flat collection of
numbers rather than a matrix of per-sample feature vectors. This module adds:

  - Per-dimension analysis: dead dimensions (no variance), NaN/Inf dimensions
  - Per-sample analysis: L2 norm distribution, outlier samples
  - Warnings tailored to embedding quality (collapsed dims, broken samples)

Typical inputs are .npy files exported by embedding pipelines (e.g. rs-embed).
The array must be exactly 2D with shape (N_samples, D_dims).
"""

from __future__ import annotations

import os
import warnings as _warnings_module

import numpy as np

from voxelkit.core.errors import ValidationError
from voxelkit.core.types import EmbeddingReportResult
from voxelkit.core.validation import require_supported_extension


# Dimension whose per-sample std falls below this is considered dead — it
# carries no signal and would be ignored or cause instability downstream.
_DEAD_DIM_STD_THRESHOLD = 1e-8

# Samples whose L2 norm is more than this many standard deviations from the
# mean norm are flagged as outliers. 3σ is the conventional threshold.
_OUTLIER_NORM_SIGMA = 3.0

# Fraction of dimensions that must be dead before a warning fires. A few dead
# dims in a large embedding are normal; a large fraction suggests model failure.
_DEAD_DIM_WARN_FRACTION = 0.05


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
            f"Embedding report requires a 2D array (N_samples, D_dims), "
            f"but got {array.ndim}D array with shape {array.shape}."
        )

    return array


def report(file_path: str) -> EmbeddingReportResult:
    """Generate an embedding-aware QA report for a .npy feature matrix.

    Analyses the array both per-dimension (column-wise) and per-sample
    (row-wise), surfacing quality issues that global statistics miss:

      - Dead dimensions: columns whose std across all samples is near zero,
        meaning the dimension carries no signal.
      - NaN/Inf dimensions: columns that contain any non-finite value, which
        will silently corrupt downstream distance computations.
      - Outlier samples: rows whose L2 norm is more than 3σ from the mean
        norm, indicating a corrupted or anomalous embedding vector.

    Args:
        file_path: Path to a .npy file containing a 2D (N_samples, D_dims)
            float array.

    Returns:
        EmbeddingReportResult with per-dim and per-sample quality statistics.

    Raises:
        ValidationError: If the file is not a 2D numeric .npy array.
        UnsupportedFormatError: If the file extension is not .npy.
    """
    require_supported_extension(
        file_path=file_path,
        # Only .npy is accepted — .npz requires choosing a named array, which
        # would add complexity for a use case where the embedding is always a
        # single flat array.
        extensions=(".npy",),
        message="Embedding report requires a .npy file.",
    )

    array = _load_embedding(file_path)
    n_samples, n_dims = array.shape

    warnings: list[str] = []

    # --- Global NaN / Inf counts ---
    total_nan_count = int(np.isnan(array).sum())
    total_inf_count = int(np.isinf(array).sum())

    if total_nan_count > 0:
        warnings.append(f"Contains {total_nan_count} NaN value(s) across the embedding matrix.")
    if total_inf_count > 0:
        warnings.append(f"Contains {total_inf_count} Inf value(s) across the embedding matrix.")

    # --- Per-dimension analysis ---
    # Work on float64 for numerical precision; the source dtype is preserved
    # in the result for the caller's information.
    arr_f = array.astype(np.float64)

    # Dimensions that contain at least one NaN or Inf corrupt any distance or
    # dot-product computation that uses them.
    nan_dim_mask = np.isnan(arr_f).any(axis=0)   # shape (D,)
    inf_dim_mask = np.isinf(arr_f).any(axis=0)   # shape (D,)
    nan_dim_count = int(nan_dim_mask.sum())
    inf_dim_count = int(inf_dim_mask.sum())

    # Per-dimension std, computed only over finite values to avoid NaN
    # contamination propagating to every dim's std.
    finite_arr = np.where(np.isfinite(arr_f), arr_f, np.nan)
    # nanstd ignores NaN entries; dims that are entirely NaN produce std=nan.
    # Suppress the "degrees of freedom <= 0" RuntimeWarning numpy raises for
    # all-NaN columns — we handle that case explicitly via np.isnan(dim_std).
    with _warnings_module.catch_warnings():
        _warnings_module.simplefilter("ignore", RuntimeWarning)
        dim_std = np.nanstd(finite_arr, axis=0)   # shape (D,)
    # A dim is dead if its std is below threshold OR the dim is entirely NaN.
    dead_dim_mask = (dim_std <= _DEAD_DIM_STD_THRESHOLD) | np.isnan(dim_std)
    dead_dim_count = int(dead_dim_mask.sum())

    if nan_dim_count > 0:
        warnings.append(
            f"{nan_dim_count} dimension(s) contain NaN — these will corrupt "
            "distance and similarity computations."
        )
    if inf_dim_count > 0:
        warnings.append(
            f"{inf_dim_count} dimension(s) contain Inf — these will corrupt "
            "distance and similarity computations."
        )
    if dead_dim_count > 0:
        dead_fraction = dead_dim_count / n_dims
        if dead_fraction >= _DEAD_DIM_WARN_FRACTION:
            warnings.append(
                f"{dead_dim_count}/{n_dims} dimensions are dead (std ≈ 0). "
                "This may indicate a collapsed or undertrained embedding space."
            )

    # --- Per-sample L2 norm analysis ---
    # L2 norm of each sample row; use only finite values so one NaN cell does
    # not suppress all norm information for that sample.
    finite_for_norms = np.where(np.isfinite(arr_f), arr_f, 0.0)
    sample_norms = np.linalg.norm(finite_for_norms, axis=1)   # shape (N,)

    norm_mean: float | None = None
    norm_std: float | None = None
    outlier_sample_count = 0

    if sample_norms.size > 0:
        norm_mean = float(np.mean(sample_norms))
        norm_std_val = float(np.std(sample_norms))
        norm_std = norm_std_val

        if norm_std_val > 0:
            # Flag samples whose norm deviates by more than _OUTLIER_NORM_SIGMA
            # standard deviations from the mean norm.
            z_scores = np.abs(sample_norms - norm_mean) / norm_std_val
            outlier_sample_count = int((z_scores > _OUTLIER_NORM_SIGMA).sum())
            if outlier_sample_count > 0:
                warnings.append(
                    f"{outlier_sample_count} sample(s) have anomalous L2 norm "
                    f"(>{_OUTLIER_NORM_SIGMA}σ from mean). These may be corrupted "
                    "or out-of-distribution embedding vectors."
                )
        elif n_samples > 1:
            # std == 0 with multiple samples means all norms are identical —
            # the embedding space has collapsed to a single point.
            warnings.append(
                "All sample L2 norms are identical. The embedding space may have "
                "collapsed (all outputs are the same vector)."
            )

    return {
        "filename": os.path.basename(file_path),
        "format": "numpy",
        "n_samples": n_samples,
        "n_dims": n_dims,
        "dtype": str(array.dtype),
        "total_nan_count": total_nan_count,
        "total_inf_count": total_inf_count,
        "dead_dim_count": dead_dim_count,
        "nan_dim_count": nan_dim_count,
        "inf_dim_count": inf_dim_count,
        "norm_mean": norm_mean,
        "norm_std": norm_std,
        "outlier_sample_count": outlier_sample_count,
        "warnings": warnings,
    }
