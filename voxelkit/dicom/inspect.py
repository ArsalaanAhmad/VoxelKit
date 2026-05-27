"""DICOM inspect — metadata for a single .dcm file or a series directory.

PHI is stripped from the returned dict by default. Pass `include_phi=True`
to include patient identifiers; the CLI prints a stderr warning when the
user sets `--phi`. PHI is not transformed inside the loaded `Dataset`
itself (that's the anonymise pipeline's job) — inspect only decides which
fields make it into the returned dict.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from voxelkit.core.types import DicomInspectResult
from voxelkit.dicom.loader import load_dicom


_NON_PHI_FIELD_TAGS = (
    "Modality",
    "SeriesDescription",
    "BodyPartExamined",
    "SeriesInstanceUID",
    "StudyInstanceUID",
)


_PHI_FIELD_TAGS = (
    ("PatientName", "patient_name"),
    ("PatientID", "patient_id"),
    ("PatientBirthDate", "patient_birth_date"),
    ("PatientSex", "patient_sex"),
    ("PatientAge", "patient_age"),
    ("AccessionNumber", "accession_number"),
    ("ReferringPhysicianName", "referring_physician_name"),
    ("InstitutionName", "institution_name"),
    ("StudyDate", "study_date"),
    ("StudyTime", "study_time"),
)


def inspect(file_path: str, *, include_phi: bool = False) -> DicomInspectResult:
    """Inspect a DICOM file or series directory and return metadata.

    Args:
        file_path: Path to a single `.dcm` file or a directory containing
            one DICOM series (folder of per-slice `.dcm` files).
        include_phi: When True, patient-identifying fields are added to
            the result. Defaults to False — never enable this from a
            shared script or a server-side handler without confirming the
            output destination is safe to receive PHI.

    Returns:
        A `DicomInspectResult` dict. Always carries `filename`, `format`,
        `source`, `shape`, `ndim`, `dtype`, `slice_count` and any non-PHI
        clinical metadata (modality, series description, voxel size, UIDs)
        that the file actually has. PHI keys are present only when
        `include_phi=True`.
    """
    loaded = load_dicom(file_path)
    dataset = loaded.representative_dataset
    array = loaded.pixel_array

    filename = os.path.basename(str(Path(file_path).resolve()))

    result: dict[str, Any] = {
        "filename": filename,
        "format": "dicom",
        "source": loaded.source,
        "shape": list(array.shape),
        "ndim": int(array.ndim),
        "dtype": str(array.dtype),
        "slice_count": loaded.slice_count,
    }

    for keyword in _NON_PHI_FIELD_TAGS:
        value = getattr(dataset, keyword, None)
        if value is not None and str(value) != "":
            result[_keyword_to_snake(keyword)] = str(value)

    voxel_size = _extract_voxel_size(dataset)
    if voxel_size is not None:
        result["voxel_size"] = voxel_size

    if include_phi:
        for keyword, snake_key in _PHI_FIELD_TAGS:
            value = getattr(dataset, keyword, None)
            if value is not None:
                rendered = str(value)
                # An empty string survives `hasattr` but is uninformative —
                # only emit fields that carry actual content.
                if rendered != "":
                    result[snake_key] = rendered

    return result  # type: ignore[return-value]  # TypedDict allows extra keys via total=False


def _keyword_to_snake(keyword: str) -> str:
    """Convert pydicom CamelCase keyword to snake_case for our output."""
    converted: list[str] = []
    for index, char in enumerate(keyword):
        if char.isupper() and index > 0 and not keyword[index - 1].isupper():
            converted.append("_")
        converted.append(char.lower())
    return "".join(converted)


def _extract_voxel_size(dataset) -> list[float] | None:
    """Return [row_mm, col_mm, slice_mm] when the header carries spacing data.

    `PixelSpacing` is a 2-element list (row, col) and `SliceThickness` is a
    scalar — together they describe one voxel. Returns None when either is
    missing rather than fabricating a default, so callers can distinguish
    "spacing unknown" from "spacing is 1×1×1".
    """
    pixel_spacing = getattr(dataset, "PixelSpacing", None)
    slice_thickness = getattr(dataset, "SliceThickness", None)
    if pixel_spacing is None or slice_thickness is None:
        return None
    try:
        return [float(pixel_spacing[0]), float(pixel_spacing[1]), float(slice_thickness)]
    except (TypeError, ValueError, IndexError):
        return None
