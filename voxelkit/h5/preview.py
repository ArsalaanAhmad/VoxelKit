import h5py
import numpy as np

from voxelkit.core.errors import ValidationError
from voxelkit.core.image_utils import to_png_bytes
from voxelkit.core.normalization import normalize_to_uint8
from voxelkit.core.validation import require_min_ndim, require_supported_extension, resolve_slice_index



def _extract_slice_2d(dataset: h5py.Dataset, axis: int, slice_index: int | None) -> np.ndarray:
    require_min_ndim(dataset.ndim, min_ndim=2, message="Dataset must have at least 2 dimensions.")

    if dataset.ndim > 3:
        raise ValidationError("Only 2D or 3D datasets are supported.")

    if dataset.ndim == 2:
        return np.asarray(dataset[:, :], dtype=np.float32)

    if axis not in (0, 1, 2):
        raise ValidationError("Invalid axis for 3D dataset. Axis must be 0, 1, or 2.")

    resolved_index = resolve_slice_index(
        length=dataset.shape[axis],
        slice_index=slice_index,
        context=f"axis {axis}",
    )

    if axis == 0:
        return np.asarray(dataset[resolved_index, :, :], dtype=np.float32)
    if axis == 1:
        return np.asarray(dataset[:, resolved_index, :], dtype=np.float32)
    return np.asarray(dataset[:, :, resolved_index], dtype=np.float32)



def preview(
    file_path: str,
    dataset_path: str,
    axis: int,
    slice_index: int | None = None,
    as_array: bool = False,
) -> bytes | np.ndarray:
    """Generate an HDF5 dataset preview as PNG bytes or uint8 numpy array.

    Inputs:
        file_path: Path to a .h5 or .hdf5 file.
        dataset_path: Internal HDF5 dataset path.
        axis: Slice axis for 3D datasets.
        slice_index: Optional index, defaults to center slice.
        as_array: If True, return uint8 numpy array instead of PNG bytes.

    Output:
        PNG bytes by default, or a 2D uint8 numpy array.

    Extension:
        Add HDF5-specific preview behavior in this module only.
    """
    require_supported_extension(
        file_path=file_path,
        extensions=(".h5", ".hdf5"),
        message="Unsupported file type. Please provide a .h5 or .hdf5 file.",
    )

    if not dataset_path or not dataset_path.strip():
        raise ValidationError("dataset_path is required.")

    try:
        with h5py.File(file_path, "r") as h5_file:
            if dataset_path not in h5_file:
                raise ValidationError(f"dataset_path not found: '{dataset_path}'.")

            node = h5_file[dataset_path]
            if isinstance(node, h5py.Group):
                raise ValidationError(f"dataset_path '{dataset_path}' points to a group, not a dataset.")

            if not isinstance(node, h5py.Dataset):
                raise ValidationError(f"dataset_path '{dataset_path}' is not a valid dataset.")

            slice_2d = _extract_slice_2d(node, axis=axis, slice_index=slice_index)
    except OSError as exc:
        raise ValidationError("Invalid, corrupted, or unreadable HDF5 file.") from exc

    normalized = normalize_to_uint8(slice_2d)
    if as_array:
        return normalized
    return to_png_bytes(normalized)
