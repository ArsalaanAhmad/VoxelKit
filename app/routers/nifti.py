from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import Response

from app.services.nifti_service import extract_nifti_metadata, generate_nifti_preview


router = APIRouter(prefix="/nifti", tags=["nifti"])


@router.post("/metadata")
async def nifti_metadata(file: UploadFile = File(...)) -> dict:
    try:
        metadata = await extract_nifti_metadata(file)
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


@router.post("/preview")
async def nifti_preview(
    file: UploadFile = File(...),
    plane: str = Query(...),
    slice_index: int | None = Query(default=None),
) -> Response:
    try:
        png_bytes = await generate_nifti_preview(
            file=file,
            plane=plane,
            slice_index=slice_index,
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
