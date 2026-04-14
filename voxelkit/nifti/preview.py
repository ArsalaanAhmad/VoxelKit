import nibabel as nib
import numpy as np
from nibabel.filebasedimages import ImageFileError

from voxelkit.core.errors import ValidationError
from voxelkit.core.image_utils import to_png_bytes
from voxelkit.core.normalization import normalize_to_uint8
from voxelkit.core.validation import (
    require_min_ndim,
    require_supported_extension,
    resolve_slice_index,
)



def _plane_to_axis(plane: str) -> int:
    plane_normalized = plane.strip().lower()
    mapping = {"sagittal": 0, "coronal": 1, "axial": 2}

    if plane_normalized not in mapping:
        raise ValidationError("Invalid plane. Plane must be one of: axial, coronal, sagittal.")

    return mapping[plane_normalized]



def _extract_2d_slice(data_proxy, shape: tuple[int, ...], axis: int, slice_index: int) -> np.ndarray:
    indexer = [slice(None), slice(None), slice(None)]
    indexer[axis] = slice_index

    for _ in shape[3:]:
        indexer.append(0)

    slice_2d = np.asarray(data_proxy[tuple(indexer)], dtype=np.float32)
    slice_2d = np.squeeze(slice_2d)

    if slice_2d.ndim != 2:
        raise ValidationError("Unable to extract a 2D slice from the provided NIfTI file.")

    return slice_2d



def preview(
    file_path: str,
    plane: str = "axial",
    slice_index: int | None = None,
    as_array: bool = False,
) -> bytes | np.ndarray:
    """Generate a NIfTI preview as PNG bytes or uint8 numpy array.

    Inputs:
        file_path: Path to a .nii or .nii.gz file.
        plane: One of axial, coronal, or sagittal.
        slice_index: Optional index, defaults to center slice.
        as_array: If True, return uint8 numpy array instead of PNG bytes.

    Output:
        PNG bytes by default, or a 2D uint8 numpy array.

    Extension:
        Add NIfTI-specific preview behavior in this module only.
    """
    require_supported_extension(
        file_path=file_path,
        extensions=(".nii", ".nii.gz"),
        message="Unsupported file type. Please provide a .nii or .nii.gz file.",
    )

    axis = _plane_to_axis(plane)

    try:
        image = nib.load(file_path)
    except ImageFileError as exc:
        raise ValidationError("Invalid or corrupted NIfTI file.") from exc

    shape = image.shape
    require_min_ndim(len(shape), min_ndim=3, message="NIfTI data must be at least 3-dimensional for slice preview.")

    resolved_index = resolve_slice_index(
        length=shape[axis],
        slice_index=slice_index,
        context=f"plane '{plane}'",
    )

    slice_2d = _extract_2d_slice(
        data_proxy=image.dataobj,
        shape=shape,
        axis=axis,
        slice_index=resolved_index,
    )

    normalized = normalize_to_uint8(slice_2d)
    if as_array:
        return normalized
    return to_png_bytes(normalized)
