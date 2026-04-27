"""FastAPI application entry point for the VoxelKit REST API."""

from fastapi import FastAPI

from app.routers.embedding import router as embedding_router
from app.routers.h5 import router as h5_router
from app.routers.nifti import router as nifti_router
from app.routers.tiff import router as tiff_router


app = FastAPI(title="VoxelKit")


@app.get("/health")
def health_check() -> dict:
    """Return a simple liveness probe response."""
    return {"status": "ok"}


app.include_router(nifti_router)
app.include_router(h5_router)
app.include_router(tiff_router)
app.include_router(embedding_router)
