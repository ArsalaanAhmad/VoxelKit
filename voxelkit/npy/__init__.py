from voxelkit.npy.inspect import inspect
from voxelkit.npy.preview import preview
from voxelkit.npy.report import report


# Backward-compatible aliases for explicit NumPy naming.
inspect_npy = inspect
preview_npy = preview
report_npy = report


__all__ = ["inspect", "preview", "report", "inspect_npy", "preview_npy", "report_npy"]
