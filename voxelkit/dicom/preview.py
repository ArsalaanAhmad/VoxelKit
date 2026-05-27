"""DICOM preview — render a single 2-D slice as PNG bytes."""

from __future__ import annotations

import numpy as np

from voxelkit.core.errors import ValidationError
from voxelkit.core.image_utils import to_png_bytes
from voxelkit.core.normalization import normalize_to_uint8
from voxelkit.core.validation import resolve_slice_index
from voxelkit.dicom.loader import load_dicom


def preview(
    file_path: str,
    *,
    axis: int = 0,
    slice_index: int | None = None,
    as_array: bool = False,
) -> bytes | np.ndarray:
    """Render one 2-D slice of a DICOM file or series directory.

    Args:
        file_path: Path to a `.dcm` file or a directory of slices.
        axis: Which array axis to slice along. For a series directory the
            volume axes are `(slice, row, col)`, so `axis=0` is the
            standard axial view, `axis=1` is coronal, `axis=2` is
            sagittal. Single 2-D `.dcm` files ignore this argument.
        slice_index: Index along `axis`. Defaults to the centre of the
            axis (`length // 2`).
        as_array: When True, return the uint8 numpy array instead of
            PNG bytes (used by the HTML report and the GUI to embed
            thumbnails without re-decoding PNG).

    Raises:
        ValidationError: when the data is below 2-D, the axis or
            slice_index is out of range, or the resulting slice is not 2-D
            after squeezing.
    """
    loaded = load_dicom(file_path)
    array = loaded.pixel_array

    if array.ndim < 2:
        raise ValidationError("DICOM data must be at least 2-dimensional for preview.")

    if array.ndim == 2:
        slice_2d = array
    else:
        if axis < 0 or axis >= array.ndim:
            raise ValidationError(
                f"axis out of bounds for {array.ndim}-D DICOM data. "
                f"Valid range: 0 to {array.ndim - 1}."
            )
        resolved_index = resolve_slice_index(
            length=array.shape[axis],
            slice_index=slice_index,
            context=f"axis {axis}",
        )
        indexer: list[slice | int] = [slice(None)] * array.ndim
        indexer[axis] = resolved_index
        slice_2d = np.asarray(array[tuple(indexer)], dtype=np.float32)
        slice_2d = np.squeeze(slice_2d)

    if slice_2d.ndim != 2:
        raise ValidationError("Unable to extract a 2D slice from the provided DICOM data.")

    normalized = normalize_to_uint8(slice_2d.astype(np.float32))
    if as_array:
        return normalized
    return to_png_bytes(normalized)
