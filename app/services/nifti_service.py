import os
import tempfile
from io import BytesIO

import nibabel as nib
import numpy as np
from fastapi import UploadFile
from nibabel.filebasedimages import ImageFileError
from PIL import Image


def _is_supported_nifti(filename: str) -> bool:
    lowered = filename.lower()
    return lowered.endswith(".nii") or lowered.endswith(".nii.gz")


async def extract_nifti_metadata(file: UploadFile) -> dict:
    if not file.filename:
        raise ValueError("Missing filename.")

    if not _is_supported_nifti(file.filename):
        raise ValueError("Unsupported file type. Please upload a .nii or .nii.gz file.")

    # Store upload as a temporary file because nibabel expects a filesystem path.
    suffix = ".nii.gz" if file.filename.lower().endswith(".nii.gz") else ".nii"
    temp_path = ""

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            content = await file.read()
            if not content:
                raise ValueError("Uploaded file is empty.")
            temp_file.write(content)
            temp_path = temp_file.name

        image = nib.load(temp_path)
        shape = image.shape
        ndim = len(shape)
        zooms = image.header.get_zooms()

        return {
            "filename": file.filename,
            "shape": list(shape),
            "ndim": ndim,
            "voxel_size": [float(value) for value in zooms[:ndim]],
            "dtype": str(image.get_data_dtype()),
        }
    except ImageFileError as exc:
        raise ValueError("Invalid or corrupted NIfTI file.") from exc
    finally:
        await file.close()
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def _normalize_to_uint8(slice_data: np.ndarray) -> np.ndarray:
    slice_data = np.nan_to_num(slice_data, nan=0.0, posinf=0.0, neginf=0.0)
    min_value = float(np.min(slice_data))
    max_value = float(np.max(slice_data))

    if max_value == min_value:
        return np.zeros(slice_data.shape, dtype=np.uint8)

    normalized = (slice_data - min_value) / (max_value - min_value)
    return (normalized * 255.0).astype(np.uint8)


def _plane_to_axis(plane: str) -> int:
    plane_normalized = plane.strip().lower()
    plane_map = {
        "sagittal": 0,
        "coronal": 1,
        "axial": 2,
    }

    if plane_normalized not in plane_map:
        raise ValueError("Invalid plane. Plane must be one of: axial, coronal, sagittal.")

    return plane_map[plane_normalized]


def _extract_2d_slice(data_proxy, shape: tuple[int, ...], axis: int, slice_index: int) -> np.ndarray:
    indexer = [slice(None), slice(None), slice(None)]
    indexer[axis] = slice_index

    # For 4D+ data, select the first volume/frame in trailing dimensions.
    for _ in shape[3:]:
        indexer.append(0)

    slice_2d = np.asarray(data_proxy[tuple(indexer)], dtype=np.float32)
    slice_2d = np.squeeze(slice_2d)
    if slice_2d.ndim != 2:
        raise ValueError("Unable to extract a 2D slice from the uploaded NIfTI file.")

    return slice_2d


async def generate_nifti_preview(file: UploadFile, plane: str, slice_index: int | None = None) -> bytes:
    if not file.filename:
        raise ValueError("Missing filename.")

    if not _is_supported_nifti(file.filename):
        raise ValueError("Unsupported file type. Please upload a .nii or .nii.gz file.")

    axis = _plane_to_axis(plane)

    temp_path = ""
    suffix = ".nii.gz" if file.filename.lower().endswith(".nii.gz") else ".nii"

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            content = await file.read()
            if not content:
                raise ValueError("Uploaded file is empty.")
            temp_file.write(content)
            temp_path = temp_file.name

        image = nib.load(temp_path)
        shape = image.shape
        data_proxy = image.dataobj

        if len(shape) < 3:
            raise ValueError("NIfTI data must be at least 3-dimensional for slice preview.")

        max_index = shape[axis] - 1
        if slice_index is None:
            slice_index = shape[axis] // 2

        if slice_index < 0 or slice_index > max_index:
            raise ValueError(
                f"slice_index out of bounds for plane '{plane}'. Valid range: 0 to {max_index}."
            )

        # Access only the requested slice through nibabel's proxy object.
        slice_2d = _extract_2d_slice(
            data_proxy=data_proxy,
            shape=shape,
            axis=axis,
            slice_index=slice_index,
        )

        slice_uint8 = _normalize_to_uint8(np.asarray(slice_2d, dtype=np.float32))
        image_pil = Image.fromarray(slice_uint8, mode="L")

        buffer = BytesIO()
        image_pil.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer.getvalue()
    except ImageFileError as exc:
        raise ValueError("Invalid or corrupted NIfTI file.") from exc
    finally:
        await file.close()
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
