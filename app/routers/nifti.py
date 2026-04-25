import os
from importlib import import_module

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import Response
from ..utils.files import infer_temp_suffix, require_upload_extension, save_upload_to_temp
from voxelkit.core.formats import NIFTI_EXTENSIONS

router = APIRouter(prefix="/nifti", tags=["nifti"])


def _nifti_temp_suffix(filename: str | None) -> str:
    return infer_temp_suffix(filename, extensions=NIFTI_EXTENSIONS, default_suffix=".nii")


def _validate_nifti_upload_filename(filename: str | None) -> None:
    require_upload_extension(
        filename=filename,
        extensions=NIFTI_EXTENSIONS,
        message="Unsupported file type. Please upload a .nii or .nii.gz file.",
    )


async def _save_upload_to_temp(file: UploadFile) -> str:
    """Persist an uploaded NIfTI file to a temporary path for library processing."""
    return await save_upload_to_temp(file, suffix=_nifti_temp_suffix(file.filename))


@router.post("/metadata")
async def nifti_metadata(file: UploadFile = File(...)) -> dict:
    """Extract metadata from an uploaded NIfTI file via the voxelkit library."""
    temp_path = ""
    try:
        extract_nifti_metadata = import_module("voxelkit.nifti.metadata").inspect
        _validate_nifti_upload_filename(file.filename)
        temp_path = await _save_upload_to_temp(file)

        metadata = extract_nifti_metadata(temp_path)
        metadata["filename"] = file.filename
        return metadata
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to process NIfTI file.",
        ) from exc
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
async def nifti_preview(
    file: UploadFile = File(...),
    plane: str = Query(...),
    slice_index: int | None = Query(default=None),
) -> Response:
    """Generate a PNG slice preview from an uploaded NIfTI file via voxelkit."""
    temp_path = ""
    try:
        generate_nifti_preview = import_module("voxelkit.nifti.preview").preview
        _validate_nifti_upload_filename(file.filename)
        temp_path = await _save_upload_to_temp(file)

        png_bytes = generate_nifti_preview(
            file_path=temp_path,
            plane=plane,
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
            detail="Failed to generate NIfTI preview.",
        ) from exc
    finally:
        await file.close()
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
