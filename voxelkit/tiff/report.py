"""TIFF QA report generation for .tif and .tiff images."""

from __future__ import annotations

import os

import tifffile

from voxelkit.core.errors import ValidationError
from voxelkit.core.formats import TIFF_EXTENSIONS
from voxelkit.core.report import build_array_report
from voxelkit.core.types import FileReportResult
from voxelkit.core.validation import require_supported_extension


def report(file_path: str) -> FileReportResult:
    """Generate a QA report for a TIFF image file.

    Loads the full pixel array with `tifffile.imread`, then delegates all
    statistics (min, max, mean, std, NaN/Inf counts, zero fraction, warnings)
    to `build_array_report` in the shared core layer.

    Preview support is declared for 2D and 3D arrays (the shapes that
    `voxelkit.tiff.preview` can render). 4D or higher-dimensional arrays
    (e.g. time-series volumes) will have `preview_supported=False` in the
    report and no preview warning will be emitted.

    Args:
        file_path: Path to a .tif or .tiff file.

    Returns:
        FileReportResult dictionary with shape, dtype, statistics, and warnings.

    Raises:
        ValidationError: If the extension is unsupported or the file is
            unreadable.
    """
    require_supported_extension(
        file_path=file_path,
        extensions=TIFF_EXTENSIONS,
        message="Unsupported file type. Please provide a .tif or .tiff file.",
    )

    try:
        array = tifffile.imread(file_path)
    except tifffile.TiffFileError as exc:
        raise ValidationError("Invalid or unreadable TIFF file.") from exc
    except (OSError, ValueError) as exc:
        raise ValidationError("Could not open TIFF file.") from exc

    preview_supported = array.ndim in (2, 3)

    return build_array_report(
        array=array,
        filename=os.path.basename(file_path),
        format_name="tiff",
        preview_supported=preview_supported,
    )
