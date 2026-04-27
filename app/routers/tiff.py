"""FastAPI router for TIFF file operations.

Mirrors the structure of the nifti and h5 routers: each endpoint accepts a
multipart file upload, writes it to a temporary path, calls the corresponding
voxelkit.tiff function, then removes the temp file in a finally block.
"""

import os
from importlib import import_module

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import Response

from app.utils.files import infer_temp_suffix, require_upload_extension, save_upload_to_temp
from voxelkit.core.formats import TIFF_EXTENSIONS

router = APIRouter(prefix="/tiff", tags=["tiff"])


def _tiff_temp_suffix(filename: str | None) -> str:
    """Choose a temp-file suffix that preserves the original TIFF extension.

    tifffile uses the file extension to decide how to interpret the file, so
    the suffix must be .tif or .tiff — never a generic .tmp.
    """
    return infer_temp_suffix(filename, extensions=TIFF_EXTENSIONS, default_suffix=".tif")


def _validate_tiff_upload(filename: str | None) -> None:
    require_upload_extension(
        filename=filename,
        extensions=TIFF_EXTENSIONS,
        message="Unsupported file type. Please upload a .tif or .tiff file.",
    )


async def _save_upload_to_temp(file: UploadFile) -> str:
    """Persist an uploaded TIFF file to a temporary path for library processing."""
    return await save_upload_to_temp(file, suffix=_tiff_temp_suffix(file.filename))


@router.post("/metadata")
async def tiff_metadata(file: UploadFile = File(...)) -> dict:
    """Extract metadata from an uploaded TIFF file via the voxelkit library.

    Returns shape, ndim, dtype, page_count, and axes string without loading
    pixel data (only the file header is read).
    """
    temp_path = ""
    try:
        inspect = import_module("voxelkit.tiff.inspect").inspect
        _validate_tiff_upload(file.filename)
        temp_path = await _save_upload_to_temp(file)

        metadata = inspect(temp_path)
        # Restore the original client filename so the response reflects what
        # was uploaded rather than the server-side temp path.
        metadata["filename"] = file.filename
        return metadata
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to process TIFF file.") from exc
    finally:
        await file.close()
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@router.post(
    "/preview",
    response_class=Response,
    responses={
        200: {
            "description": "PNG preview image",
            "content": {"image/png": {}},
        }
    },
)
async def tiff_preview(
    file: UploadFile = File(...),
    axis: int = Query(default=0, description="Slice axis for 3D z-stacks (0=Z, 1=Y, 2=X)."),
    slice_index: int | None = Query(default=None, description="Slice index; defaults to centre."),
) -> Response:
    """Generate a PNG slice preview from an uploaded TIFF file via voxelkit.

    For 2D TIFFs the full image is returned. For 3D z-stacks a single plane
    is extracted along `axis` at `slice_index` (defaulting to centre).
    """
    temp_path = ""
    try:
        preview = import_module("voxelkit.tiff.preview").preview
        _validate_tiff_upload(file.filename)
        temp_path = await _save_upload_to_temp(file)

        png_bytes = preview(
            file_path=temp_path,
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
        raise HTTPException(status_code=500, detail="Failed to generate TIFF preview.") from exc
    finally:
        await file.close()
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


@router.post("/report")
async def tiff_report(file: UploadFile = File(...)) -> dict:
    """Generate a QA report for an uploaded TIFF file via the voxelkit library.

    Returns shape, dtype, min/max/mean/std statistics, NaN/Inf counts,
    zero fraction, and any quality warnings.
    """
    temp_path = ""
    try:
        report = import_module("voxelkit.tiff.report").report
        _validate_tiff_upload(file.filename)
        temp_path = await _save_upload_to_temp(file)

        result = report(temp_path)
        result["filename"] = file.filename
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to generate TIFF report.") from exc
    finally:
        await file.close()
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
