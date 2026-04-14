from voxelkit.h5.inspect import inspect_h5
from voxelkit.h5.preview import preview


# Backward-compatible aliases for earlier flat API names.
inspect = inspect_h5
preview_h5 = preview


__all__ = ["inspect_h5", "inspect", "preview", "preview_h5"]
