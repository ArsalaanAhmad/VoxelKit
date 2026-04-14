import os
import tempfile
from importlib import import_module

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import Response

router = APIRouter(prefix="/nifti", tags=["nifti"])


def _is_supported_nifti_filename(filename: str | None) -> bool:
    lowered = (filename or "").lower()
    return lowered.endswith(".nii") or lowered.endswith(".nii.gz")


def _nifti_temp_suffix(filename: str | None) -> str:
    lowered = (filename or "").lower()
    if lowered.endswith(".nii.gz"):
        return ".nii.gz"
    return ".nii"


def _validate_nifti_upload_filename(filename: str | None) -> None:
    if not filename:
        raise ValueError("Missing filename.")

    if not _is_supported_nifti_filename(filename):
        raise ValueError("Unsupported file type. Please upload a .nii or .nii.gz file.")


async def _save_upload_to_temp(file: UploadFile) -> str:
    """Persist an uploaded NIfTI file to a temporary path for library processing."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=_nifti_temp_suffix(file.filename)) as temp_file:
        content = await file.read()
        if not content:
            raise ValueError("Uploaded file is empty.")
        temp_file.write(content)
        return temp_file.name


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
