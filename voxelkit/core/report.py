"""Shared report/statistics utilities for imaging arrays."""

import numpy as np

from voxelkit.core.errors import ValidationError
from voxelkit.core.types import FileReportResult


_NEAR_CONSTANT_STD_THRESHOLD = 1e-8
_MOSTLY_ZERO_THRESHOLD = 0.95


def build_array_report(
    *,
    array: np.ndarray,
    filename: str,
    format_name: str,
    preview_supported: bool,
    extra_warnings: list[str] | None = None,
) -> FileReportResult:
    """Build a normalized QA report dictionary from a numeric array."""
    values = np.asarray(array)
    if not np.issubdtype(values.dtype, np.number):
        raise ValidationError("Dataset must contain numeric values for report statistics.")

    warnings: list[str] = []
    if extra_warnings:
        warnings.extend(extra_warnings)

    shape = list(values.shape)
    ndim = int(values.ndim)
    total_count = int(values.size)

    if total_count == 0:
        warnings.append("Dataset is empty.")
        if not preview_supported:
            warnings.append("Unsupported dimensionality for preview.")
        return {
            "filename": filename,
            "format": format_name,
            "shape": shape,
            "ndim": ndim,
            "dtype": str(values.dtype),
            "min": None,
            "max": None,
            "mean": None,
            "std": None,
            "nan_count": 0,
            "inf_count": 0,
            "zero_fraction": 0.0,
            "warnings": warnings,
        }

    nan_count = int(np.isnan(values).sum())
    inf_count = int(np.isinf(values).sum())
    zero_fraction = float(np.count_nonzero(values == 0) / total_count)

    finite_mask = np.isfinite(values)
    finite_values = values[finite_mask]

    min_value: float | None = None
    max_value: float | None = None
    mean_value: float | None = None
    std_value: float | None = None

    if finite_values.size == 0:
        warnings.append("No finite values available for summary statistics.")
    else:
        min_value = float(np.min(finite_values))
        max_value = float(np.max(finite_values))
        mean_value = float(np.mean(finite_values))
        std_value = float(np.std(finite_values))

        if std_value <= _NEAR_CONSTANT_STD_THRESHOLD:
            warnings.append("Array is constant or nearly constant.")

    if nan_count > 0:
        warnings.append("Contains NaNs.")

    if inf_count > 0:
        warnings.append("Contains Infs.")

    if zero_fraction >= _MOSTLY_ZERO_THRESHOLD:
        warnings.append("Array is mostly zeros.")

    if not preview_supported:
        warnings.append("Unsupported dimensionality for preview.")

    return {
        "filename": filename,
        "format": format_name,
        "shape": shape,
        "ndim": ndim,
        "dtype": str(values.dtype),
        "min": min_value,
        "max": max_value,
        "mean": mean_value,
        "std": std_value,
        "nan_count": nan_count,
        "inf_count": inf_count,
        "zero_fraction": zero_fraction,
        "warnings": warnings,
    }
