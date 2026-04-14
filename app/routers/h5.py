import os
import tempfile
from importlib import import_module

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import Response

router = APIRouter(prefix="/h5", tags=["h5"])


def _is_supported_h5_filename(filename: str | None) -> bool:
    lowered = (filename or "").lower()
    return lowered.endswith(".h5") or lowered.endswith(".hdf5")


def _h5_temp_suffix(filename: str | None) -> str:
    lowered = (filename or "").lower()
    if lowered.endswith(".hdf5"):
        return ".hdf5"
    return ".h5"


def _validate_h5_upload_filename(filename: str | None) -> None:
    if not filename:
        raise ValueError("Missing filename.")

    if not _is_supported_h5_filename(filename):
        raise ValueError("Unsupported file type. Please upload a .h5 or .hdf5 file.")


async def _save_upload_to_temp(file: UploadFile) -> str:
    """Persist an uploaded HDF5 file to a temporary path for library processing."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=_h5_temp_suffix(file.filename)) as temp_file:
        content = await file.read()
        if not content:
            raise ValueError("Uploaded file is empty.")
        temp_file.write(content)
        return temp_file.name


@router.post("/inspect")
async def inspect_h5(file: UploadFile = File(...)) -> dict:
    """Inspect an uploaded HDF5 file by delegating to the voxelkit library."""
    temp_path = ""
    try:
        inspect_h5_library = import_module("voxelkit.h5.inspect").inspect_h5
        _validate_h5_upload_filename(file.filename)
        temp_path = await _save_upload_to_temp(file)

        result = inspect_h5_library(temp_path)
        result["filename"] = file.filename
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to inspect HDF5 file.",
        ) from exc
    finally:
        await file.close()
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@router.post(
    "/slice",
    response_class=Response,
    responses={
        200: {
            "description": "PNG preview image",
            "content": {"image/png": {}},
        }
    },
)
async def slice_h5(
    file: UploadFile = File(...),
    dataset_path: str = Query(...),
    axis: int = Query(...),
    slice_index: int | None = Query(default=None),
) -> Response:
    """Generate a PNG slice preview by delegating to the voxelkit library."""
    temp_path = ""
    try:
        preview_h5_library = import_module("voxelkit.h5.preview").preview
        _validate_h5_upload_filename(file.filename)
        temp_path = await _save_upload_to_temp(file)

        png_bytes = preview_h5_library(
            file_path=temp_path,
            dataset_path=dataset_path,
            axis=axis,
            slice_index=slice_index,
            as_array=False,
        )
        return Response(content=png_bytes, media_type="image/png")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate HDF5 slice preview.",
        ) from exc
    finally:
        await file.close()
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
