"""TIFF file inspection for .tif and .tiff inputs.

Uses `tifffile.TiffFile` for lazy metadata access — only the file header and
IFD (Image File Directory) entries are read; pixel data is never loaded here.

When `rasterio` is installed (via `pip install voxelkit[geo]`), GeoTIFF files
are automatically detected and geo fields (crs, bounds, resolution, band_count)
are added to the result. Files without a CRS are returned as plain TIFFs.
"""

from __future__ import annotations

import os
from typing import Any

import tifffile

from voxelkit.core.errors import ValidationError
from voxelkit.core.formats import TIFF_EXTENSIONS
from voxelkit.core.types import GeoTiffInspectResult, TiffInspectResult
from voxelkit.core.validation import require_supported_extension


def _try_read_geo_metadata(file_path: str) -> dict[str, Any]:
    """Return geo metadata dict if rasterio is available and the file has a CRS.

    Returns an empty dict when rasterio is not installed or the file carries
    no coordinate reference system — so the caller can always do `{**result,
    **geo}` safely.
    """
    try:
        import rasterio  # type: ignore[import-untyped]
    except ModuleNotFoundError:
        return {}

    try:
        with rasterio.open(file_path) as ds:
            if ds.crs is None:
                return {}
            return {
                "crs": ds.crs.to_string(),
                "bounds": list(ds.bounds),
                "resolution": list(ds.res),
                "band_count": ds.count,
            }
    except Exception:  # noqa: BLE001 — geo enrichment must never break plain TIFF inspection
        return {}


def inspect(file_path: str) -> TiffInspectResult | GeoTiffInspectResult:
    """Inspect a TIFF file and return metadata without loading pixel data.

    Opens the file with `tifffile.TiffFile` and reads only the first image
    series. A TIFF *series* is a collection of pages that form one logical
    dataset (e.g. a Z-stack or an RGB image). Most scientific TIFFs have
    exactly one series.

    When `rasterio` is installed and the file carries a CRS, the result is
    extended with geo fields: `crs`, `bounds`, `resolution`, `band_count`.

    Args:
        file_path: Path to a .tif or .tiff file.

    Returns:
        TiffInspectResult (or GeoTiffInspectResult when geo metadata is found).

    Raises:
        ValidationError: If the extension is unsupported or the file cannot
            be opened/parsed by tifffile.
    """
    require_supported_extension(
        file_path=file_path,
        extensions=TIFF_EXTENSIONS,
        message="Unsupported file type. Please provide a .tif or .tiff file.",
    )

    try:
        with tifffile.TiffFile(file_path) as tif:
            if not tif.series:
                raise ValidationError("TIFF file contains no image series.")

            series = tif.series[0]
            shape = list(series.shape)
            dtype = str(series.dtype)
            axes = series.axes
            page_count = len(tif.pages)

    except tifffile.TiffFileError as exc:
        raise ValidationError("Invalid or unreadable TIFF file.") from exc
    except (OSError, ValueError) as exc:
        raise ValidationError("Could not open TIFF file.") from exc

    result: dict[str, Any] = {
        "filename": os.path.basename(file_path),
        "format": "tiff",
        "shape": shape,
        "ndim": len(shape),
        "dtype": dtype,
        "page_count": page_count,
        "axes": axes,
    }

    geo = _try_read_geo_metadata(file_path)
    if geo:
        result["is_geotiff"] = True
        result.update(geo)

    return result  # type: ignore[return-value]
