"""TIFF file inspection for .tif and .tiff inputs.

Uses `tifffile.TiffFile` for lazy metadata access — only the file header and
IFD (Image File Directory) entries are read; pixel data is never loaded here.
"""

from __future__ import annotations

import os

import tifffile

from voxelkit.core.errors import ValidationError
from voxelkit.core.formats import TIFF_EXTENSIONS
from voxelkit.core.types import TiffInspectResult
from voxelkit.core.validation import require_supported_extension


def inspect(file_path: str) -> TiffInspectResult:
    """Inspect a TIFF file and return metadata without loading pixel data.

    Opens the file with `tifffile.TiffFile` and reads only the first image
    series. A TIFF *series* is a collection of pages that form one logical
    dataset (e.g. a Z-stack or an RGB image). Most scientific TIFFs have
    exactly one series.

    Args:
        file_path: Path to a .tif or .tiff file.

    Returns:
        TiffInspectResult with filename, shape, ndim, dtype, page_count, and
        axes string (e.g. "ZYX", "YX", "YXS").

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
            # series[0] covers the primary image; every compliant TIFF has at
            # least one series. Multi-series files (rare in practice) expose
            # subsequent series as series[1], series[2], etc. — we report only
            # the first for simplicity.
            if not tif.series:
                raise ValidationError("TIFF file contains no image series.")

            series = tif.series[0]
            shape = list(series.shape)
            dtype = str(series.dtype)
            axes = series.axes     # tifffile dimension labels, e.g. "ZYX"
            page_count = len(tif.pages)

    except tifffile.TiffFileError as exc:
        raise ValidationError("Invalid or unreadable TIFF file.") from exc
    except (OSError, ValueError) as exc:
        raise ValidationError("Could not open TIFF file.") from exc

    return {
        "filename": os.path.basename(file_path),
        "format": "tiff",
        "shape": shape,
        "ndim": len(shape),
        "dtype": dtype,
        "page_count": page_count,
        "axes": axes,
    }
