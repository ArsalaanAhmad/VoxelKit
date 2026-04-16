"""NIfTI QA report generation."""

import os

import nibabel as nib
import numpy as np
from nibabel.filebasedimages import ImageFileError

from voxelkit.core.errors import ValidationError
from voxelkit.core.report import build_array_report
from voxelkit.core.types import FileReportResult
from voxelkit.core.validation import require_supported_extension


def report(file_path: str) -> FileReportResult:
    """Generate a QA report for a NIfTI file."""
    require_supported_extension(
        file_path=file_path,
        extensions=(".nii", ".nii.gz"),
        message="Unsupported file type. Please provide a .nii or .nii.gz file.",
    )

    filename = os.path.basename(file_path)

    try:
        image = nib.load(file_path)
        data = np.asanyarray(image.dataobj)
    except ImageFileError as exc:
        raise ValidationError("Invalid or corrupted NIfTI file.") from exc

    return build_array_report(
        array=data,
        filename=filename,
        format_name="nifti",
        preview_supported=data.ndim >= 3,
    )
