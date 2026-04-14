import os
import tempfile
from io import BytesIO

import h5py
import numpy as np
from fastapi import UploadFile
from PIL import Image


def _is_supported_h5(filename: str) -> bool:
    lowered = filename.lower()
    return lowered.endswith(".h5") or lowered.endswith(".hdf5")


def _normalize_to_uint8(slice_data: np.ndarray) -> np.ndarray:
    slice_data = np.nan_to_num(slice_data, nan=0.0, posinf=0.0, neginf=0.0)
    min_value = float(np.min(slice_data))
    max_value = float(np.max(slice_data))

    if max_value == min_value:
        return np.zeros(slice_data.shape, dtype=np.uint8)

    normalized = (slice_data - min_value) / (max_value - min_value)
    return (normalized * 255.0).astype(np.uint8)


async def inspect_h5_file(file: UploadFile) -> dict:
    if not file.filename:
        raise ValueError("Missing filename.")

    if not _is_supported_h5(file.filename):
        raise ValueError("Unsupported file type. Please upload a .h5 or .hdf5 file.")

    temp_path = ""
    suffix = ".hdf5" if file.filename.lower().endswith(".hdf5") else ".h5"

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            content = await file.read()
            if not content:
                raise ValueError("Uploaded file is empty.")
            temp_file.write(content)
            temp_path = temp_file.name

        items: list[dict] = [{"path": "/", "type": "group"}]

        try:
            with h5py.File(temp_path, "r") as h5_file:
                def _visitor(path: str, obj) -> None:
                    if isinstance(obj, h5py.Group):
                        items.append({
                            "path": path,
                            "type": "group",
                        })
                    elif isinstance(obj, h5py.Dataset):
                        items.append({
                            "path": path,
                            "type": "dataset",
                            "shape": list(obj.shape),
                            "dtype": str(obj.dtype),
                        })

                h5_file.visititems(_visitor)
        except OSError as exc:
            raise ValueError("Invalid, corrupted, or unreadable HDF5 file.") from exc

        return {
            "filename": file.filename,
            "items": items,
        }
    finally:
        await file.close()
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def _get_dataset(h5_file: h5py.File, dataset_path: str) -> h5py.Dataset:
    if dataset_path not in h5_file:
        raise ValueError(f"dataset_path not found: '{dataset_path}'.")

    node = h5_file[dataset_path]
    if isinstance(node, h5py.Group):
        raise ValueError(f"dataset_path '{dataset_path}' points to a group, not a dataset.")

    if not isinstance(node, h5py.Dataset):
        raise ValueError(f"dataset_path '{dataset_path}' is not a valid dataset.")

    return node


def _extract_slice_2d(dataset: h5py.Dataset, axis: int, slice_index: int | None) -> np.ndarray:
    if dataset.ndim < 2:
        raise ValueError("Dataset must have at least 2 dimensions.")

    if dataset.ndim > 3:
        raise ValueError("Only 2D or 3D datasets are supported for /h5/slice in this MVP.")

    if dataset.ndim == 2:
        # MVP rule: render full 2D dataset and ignore axis/slice_index.
        return np.asarray(dataset[:, :], dtype=np.float32)

    # dataset.ndim == 3
    if axis not in (0, 1, 2):
        raise ValueError("Invalid axis for 3D dataset. Axis must be 0, 1, or 2.")

    max_index = dataset.shape[axis] - 1
    if slice_index is None:
        slice_index = dataset.shape[axis] // 2

    if slice_index < 0 or slice_index > max_index:
        raise ValueError(f"slice_index out of bounds for axis {axis}. Valid range: 0 to {max_index}.")

    if axis == 0:
        return np.asarray(dataset[slice_index, :, :], dtype=np.float32)
    if axis == 1:
        return np.asarray(dataset[:, slice_index, :], dtype=np.float32)
    return np.asarray(dataset[:, :, slice_index], dtype=np.float32)


async def slice_h5_dataset(
    file: UploadFile,
    dataset_path: str,
    axis: int,
    slice_index: int | None = None,
) -> bytes:
    if not file.filename:
        raise ValueError("Missing filename.")

    if not _is_supported_h5(file.filename):
        raise ValueError("Unsupported file type. Please upload a .h5 or .hdf5 file.")

    if not dataset_path or not dataset_path.strip():
        raise ValueError("dataset_path is required.")

    temp_path = ""
    suffix = ".hdf5" if file.filename.lower().endswith(".hdf5") else ".h5"

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            content = await file.read()
            if not content:
                raise ValueError("Uploaded file is empty.")
            temp_file.write(content)
            temp_path = temp_file.name

        try:
            with h5py.File(temp_path, "r") as h5_file:
                dataset = _get_dataset(h5_file, dataset_path.strip())
                slice_2d = _extract_slice_2d(dataset, axis=axis, slice_index=slice_index)
        except OSError as exc:
            raise ValueError("Invalid, corrupted, or unreadable HDF5 file.") from exc

        slice_uint8 = _normalize_to_uint8(slice_2d)
        image_pil = Image.fromarray(slice_uint8, mode="L")
        buffer = BytesIO()
        image_pil.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer.getvalue()
    finally:
        await file.close()
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
