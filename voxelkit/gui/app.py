"""Minimal local/offline Streamlit GUI for VoxelKit."""

from __future__ import annotations

import importlib
import tempfile
from pathlib import Path
from typing import Any

from voxelkit import inspect as inspect_file
from voxelkit import report_file
from voxelkit.core.formats import HDF5_EXTENSIONS, NIFTI_EXTENSIONS, has_extension
from voxelkit.h5 import preview as preview_h5
from voxelkit.nifti import preview as preview_nifti


SUPPORTED_UPLOAD_TYPES = ["nii", "gz", "h5", "hdf5", "npy", "tif", "tiff"]

st = importlib.import_module("streamlit")


def _is_nifti(path: str) -> bool:
    """Return True when a label/path represents a NIfTI file."""
    return has_extension(path, NIFTI_EXTENSIONS)


def _is_h5(path: str) -> bool:
    """Return True when a label/path represents an HDF5 file."""
    return has_extension(path, HDF5_EXTENSIONS)


def _save_uploaded_file(uploaded_file: Any) -> str:
    """Persist a Streamlit upload to a temporary file while preserving suffix."""
    suffix = Path(uploaded_file.name).suffix
    if has_extension(uploaded_file.name, (".nii.gz",)):
        suffix = ".nii.gz"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        return temp_file.name


def _get_input_path() -> tuple[str | None, str | None]:
    source = st.radio("Input source", ["Upload file", "Local file path"], horizontal=True)

    if source == "Upload file":
        uploaded = st.file_uploader(
            "Upload a file",
            type=SUPPORTED_UPLOAD_TYPES,
            help="Files stay local and are processed on your machine.",
        )
        if uploaded is None:
            return None, None
        temp_path = _save_uploaded_file(uploaded)
        return temp_path, uploaded.name

    path_text = st.text_input("Local file path", value="")
    if not path_text.strip():
        return None, None

    resolved = Path(path_text).expanduser()
    if not resolved.exists() or not resolved.is_file():
        st.error("File not found. Provide a valid local file path.")
        return None, None

    return str(resolved), resolved.name


def _render_preview(file_path: str, file_label: str, inspect_result: dict) -> None:
    st.subheader("Preview")

    if _is_nifti(file_label):
        plane = st.selectbox("Plane", ["axial", "coronal", "sagittal"], index=0)
        use_center = st.checkbox("Use center slice", value=True, key="nifti_center")
        slice_index = None
        if not use_center:
            slice_index = int(st.number_input("Slice index", min_value=0, value=0, step=1))

        if st.button("Generate preview", key="preview_nifti"):
            png_bytes = preview_nifti(file_path=file_path, plane=plane, slice_index=slice_index)
            st.image(png_bytes, caption=f"NIfTI preview: {file_label}", use_container_width=True)
        return

    if _is_h5(file_label):
        dataset_paths = [
            item["path"]
            for item in inspect_result.get("items", [])
            if isinstance(item, dict) and item.get("type") == "dataset"
        ]

        if dataset_paths:
            default_dataset = dataset_paths[0]
            selected_dataset = st.selectbox("Dataset path", dataset_paths, index=0)
            dataset_path = st.text_input("Dataset path override", value=selected_dataset)
        else:
            default_dataset = ""
            dataset_path = st.text_input("Dataset path", value=default_dataset)

        axis = int(st.selectbox("Axis (3D datasets)", [0, 1, 2], index=0))
        use_center = st.checkbox("Use center slice", value=True, key="h5_center")
        slice_index = None
        if not use_center:
            slice_index = int(st.number_input("Slice index", min_value=0, value=0, step=1, key="h5_slice"))

        if st.button("Generate preview", key="preview_h5"):
            if not dataset_path.strip():
                st.error("Dataset path is required for HDF5 preview.")
                return
            png_bytes = preview_h5(
                file_path=file_path,
                dataset_path=dataset_path,
                axis=axis,
                slice_index=slice_index,
            )
            st.image(png_bytes, caption=f"HDF5 preview: {file_label}", use_container_width=True)
        return

    st.info("Preview is currently available in this GUI prototype for NIfTI and HDF5 files.")


def render_app() -> None:
    st.set_page_config(page_title="VoxelKit Local GUI", layout="wide")

    st.title("VoxelKit Optional Local GUI")
    st.caption("Local/offline prototype for inspect, report, and quick previews. No upload to external services.")

    file_path, file_label = _get_input_path()
    if file_path is None or file_label is None:
        st.info("Select or upload a file to continue.")
        return

    st.write(f"Selected file: {file_label}")

    try:
        st.subheader("Inspect")
        inspect_result = inspect_file(file_path)
        st.json(inspect_result)

        st.subheader("Report")
        report_result = report_file(file_path)
        st.json(report_result)

        _render_preview(file_path=file_path, file_label=file_label, inspect_result=inspect_result)
    except (ValueError, OSError) as exc:
        st.error(str(exc))


if __name__ == "__main__":
    render_app()
