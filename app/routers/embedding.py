"""FastAPI router for embedding QA operations.

Accepts .npy file uploads containing 2D (N_samples, D_dims) feature matrices
and returns embedding-aware quality reports or heatmap previews.
"""

import os

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import Response

from app.utils.files import require_upload_extension, save_upload_to_temp
from voxelkit.embedding.preview import preview as preview_embedding
from voxelkit.embedding.report import report as report_embedding

router = APIRouter(prefix="/embedding", tags=["embedding"])


def _validate_embedding_upload(filename: str | None) -> None:
    require_upload_extension(
        filename=filename,
        extensions=(".npy",),
        message="Unsupported file type. Please upload a .npy file.",
    )


@router.post("/report")
async def embedding_report(file: UploadFile = File(...)) -> dict:
    """Generate an embedding-aware QA report for an uploaded .npy matrix.

    Returns per-dimension statistics (dead dims, NaN/Inf dims) and per-sample
    statistics (L2 norm distribution, outlier count) alongside global counts.
    """
    temp_path = ""
    try:
        _validate_embedding_upload(file.filename)
        temp_path = await save_upload_to_temp(file, suffix=".npy")

        result = report_embedding(temp_path)
        result["filename"] = file.filename
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to generate embedding report.") from exc
    finally:
        await file.close()
        if temp_path:
            try:
                os.remove(temp_path)
            except FileNotFoundError:
                pass


@router.post(
    "/preview",
    response_class=Response,
    responses={
        200: {
            "description": "PNG heatmap — rows = samples, columns = dimensions",
            "content": {"image/png": {}},
        }
    },
)
async def embedding_preview(
    file: UploadFile = File(...),
    max_samples: int = Query(
        default=256,
        description="Maximum sample rows to render. Large matrices are randomly subsampled.",
    ),
) -> Response:
    """Render an uploaded .npy embedding matrix as a per-column-normalised PNG heatmap.

    Each pixel row is one sample, each pixel column is one embedding dimension.
    Dead dimensions (no variance) appear as uniform mid-grey stripes.
    """
    temp_path = ""
    try:
        _validate_embedding_upload(file.filename)
        temp_path = await save_upload_to_temp(file, suffix=".npy")

        png_bytes = preview_embedding(
            file_path=temp_path,
            max_samples=max_samples,
            as_array=False,
        )
        return Response(content=png_bytes, media_type="image/png")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to generate embedding preview.") from exc
    finally:
        await file.close()
        if temp_path:
            try:
                os.remove(temp_path)
            except FileNotFoundError:
                pass
