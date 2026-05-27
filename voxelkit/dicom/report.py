"""DICOM QA report — pixel-array statistics for a .dcm or series directory."""

from __future__ import annotations

import os
from pathlib import Path

import numpy as np

from voxelkit.core.report import build_array_report
from voxelkit.core.types import FileReportResult
from voxelkit.dicom.loader import load_dicom


def report(file_path: str) -> FileReportResult:
    """Generate a QA report for a single .dcm or a series directory.

    The same `FileReportResult` schema as every other format — min/max,
    mean/std, NaN/Inf counts, zero fraction, plus the standard warning
    list. PHI is never included in this output: report() reads pixel data
    only.
    """
    loaded = load_dicom(file_path)
    array = np.asarray(loaded.pixel_array)
    filename = os.path.basename(str(Path(file_path).resolve()))

    return build_array_report(
        array=array,
        filename=filename,
        format_name="dicom",
        preview_supported=array.ndim >= 2,
    )
