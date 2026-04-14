from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import Response

from app.services.h5_service import inspect_h5_file, slice_h5_dataset


router = APIRouter(prefix="/h5", tags=["h5"])


@router.post("/inspect")
async def inspect_h5(file: UploadFile = File(...)) -> dict:
    try:
        return await inspect_h5_file(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Failed to inspect HDF5 file.",
        ) from exc


@router.post("/slice")
async def slice_h5(
    file: UploadFile = File(...),
    dataset_path: str = Query(...),
    axis: int = Query(...),
    slice_index: int | None = Query(default=None),
) -> Response:
    try:
        png_bytes = await slice_h5_dataset(
            file=file,
            dataset_path=dataset_path,
            axis=axis,
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
            detail="Failed to generate HDF5 slice preview.",
        ) from exc
