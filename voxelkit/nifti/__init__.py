from voxelkit.nifti.metadata import inspect
from voxelkit.nifti.preview import preview


# Backward-compatible aliases for earlier flat API names.
nifti_metadata = inspect
preview_nifti = preview


__all__ = ["inspect", "preview", "nifti_metadata", "preview_nifti"]
