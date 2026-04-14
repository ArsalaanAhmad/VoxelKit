import os
import tempfile

import h5py
import nibabel as nib
import numpy as np
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _create_temp_nifti_file(shape: tuple[int, ...] = (8, 9, 10)) -> str:
    array = np.random.rand(*shape).astype(np.float32)
    image = nib.Nifti1Image(array, affine=np.eye(4))
    fd, path = tempfile.mkstemp(suffix=".nii.gz")
    os.close(fd)
    nib.save(image, path)
    return path


def _create_temp_h5_file() -> str:
    fd, path = tempfile.mkstemp(suffix=".h5")
    os.close(fd)
    with h5py.File(path, "w") as h5_file:
        group = h5_file.create_group("data")
        subject = group.create_group("subject01")
        run = subject.create_group("run1")
        run.create_dataset("bold", data=np.random.rand(6, 7, 8).astype(np.float32))
    return path


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_nifti_metadata() -> None:
    path = _create_temp_nifti_file()
    try:
        with open(path, "rb") as file_handle:
            response = client.post(
                "/nifti/metadata",
                files={"file": ("sample.nii.gz", file_handle, "application/octet-stream")},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["filename"] == "sample.nii.gz"
        assert body["shape"] == [8, 9, 10]
        assert body["ndim"] == 3
        assert "voxel_size" in body
        assert "dtype" in body
    finally:
        os.remove(path)


def test_nifti_preview() -> None:
    path = _create_temp_nifti_file()
    try:
        with open(path, "rb") as file_handle:
            response = client.post(
                "/nifti/preview",
                params={"plane": "axial", "slice_index": 3},
                files={"file": ("sample.nii.gz", file_handle, "application/octet-stream")},
            )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("image/png")
        assert len(response.content) > 0
    finally:
        os.remove(path)


def test_h5_inspect() -> None:
    path = _create_temp_h5_file()
    try:
        with open(path, "rb") as file_handle:
            response = client.post(
                "/h5/inspect",
                files={"file": ("sample.h5", file_handle, "application/octet-stream")},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["filename"] == "sample.h5"
        assert any(
            item.get("path") == "data/subject01/run1/bold" and item.get("type") == "dataset"
            for item in body.get("items", [])
        )
    finally:
        os.remove(path)


def test_h5_slice() -> None:
    path = _create_temp_h5_file()
    try:
        with open(path, "rb") as file_handle:
            response = client.post(
                "/h5/slice",
                params={"dataset_path": "data/subject01/run1/bold", "axis": 2, "slice_index": 4},
                files={"file": ("sample.h5", file_handle, "application/octet-stream")},
            )

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("image/png")
        assert len(response.content) > 0
    finally:
        os.remove(path)
