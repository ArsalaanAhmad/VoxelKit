from voxelkit.nifti.metadata import inspect
from voxelkit.nifti.preview import preview
from voxelkit.nifti.report import report


# Backward-compatible aliases for earlier flat API names.
nifti_metadata = inspect
preview_nifti = preview
report_nifti = report


__all__ = ["inspect", "preview", "report", "nifti_metadata", "preview_nifti", "report_nifti"]
