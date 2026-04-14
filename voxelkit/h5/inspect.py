import os

import h5py
from voxelkit.core.errors import ValidationError
from voxelkit.core.types import H5InspectResult, InspectItem
from voxelkit.core.validation import require_supported_extension



def inspect_h5(file_path: str) -> H5InspectResult:
    """Inspect an HDF5 file and return recursive groups/datasets metadata.

    Inputs:
        file_path: Path to a .h5 or .hdf5 file.

    Output:
        Dict with filename and discovered item metadata.

    Extension:
        Add format-specific inspect behavior in this module only.
    """
    require_supported_extension(
        file_path=file_path,
        extensions=(".h5", ".hdf5"),
        message="Unsupported file type. Please provide a .h5 or .hdf5 file.",
    )

    filename = os.path.basename(file_path)
    items: list[InspectItem] = [{"path": "/", "type": "group"}]

    try:
        with h5py.File(file_path, "r") as h5_file:
            def _visitor(path: str, obj) -> None:
                if isinstance(obj, h5py.Group):
                    items.append({"path": path, "type": "group"})
                elif isinstance(obj, h5py.Dataset):
                    items.append(
                        {
                            "path": path,
                            "type": "dataset",
                            "shape": list(obj.shape),
                            "dtype": str(obj.dtype),
                        }
                    )

            h5_file.visititems(_visitor)
    except OSError as exc:
        raise ValidationError("Invalid, corrupted, or unreadable HDF5 file.") from exc

    return {"filename": filename, "items": items}


# Backward-compatible alias while callers migrate to inspect_h5.
inspect = inspect_h5
