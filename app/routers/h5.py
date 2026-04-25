import os
from importlib import import_module

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from ..utils.files import infer_temp_suffix, require_upload_extension, save_upload_to_temp
from voxelkit.core.formats import HDF5_EXTENSIONS

router = APIRouter(prefix="/h5", tags=["h5"])


def _h5_temp_suffix(filename: str | None) -> str:
    return infer_temp_suffix(filename, extensions=HDF5_EXTENSIONS, default_suffix=".h5")


def _validate_h5_upload_filename(filename: str | None) -> None:
    require_upload_extension(
        filename=filename,
        extensions=HDF5_EXTENSIONS,
        message="Unsupported file type. Please upload a .h5 or .hdf5 file.",
    )


async def _save_upload_to_temp(file: UploadFile) -> str:
    """Persist an uploaded HDF5 file to a temporary path for library processing."""
    return await save_upload_to_temp(file, suffix=_h5_temp_suffix(file.filename))


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
