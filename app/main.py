from fastapi import FastAPI

from app.routers.h5 import router as h5_router
from app.routers.nifti import router as nifti_router


app = FastAPI(title="VoxelKit")


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok"}


app.include_router(nifti_router)
app.include_router(h5_router)




