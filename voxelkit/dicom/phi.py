"""DICOM PHI (Protected Health Information) tag definitions and scrubbing.

VoxelKit strips PHI from every public output by default. The exhaustive
DICOM Supplement 142 PS3.15 Annex E "Basic Profile" lists dozens of
identifier categories; this module covers the subset that every consumer
of inspect / report output will care about — direct identifiers, study
timestamps that re-identify trivially, and device-level identifiers used
by re-identification attacks.

A "scrub" replaces a tag's value with an empty string (DICOM-compliant
empty-value encoding) rather than deleting the element, because some
downstream readers fault on missing required tags. The element keeps its
tag and VR so the file structure stays valid.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydicom.dataset import Dataset


# Direct-identifier PHI tags. Names match pydicom's keyword form so callers
# can read them with `dataset.PatientName` etc.
DIRECT_PHI_TAGS: tuple[str, ...] = (
    "PatientName",
    "PatientID",
    "PatientBirthDate",
    "PatientBirthTime",
    "PatientSex",
    "PatientAge",
    "PatientWeight",
    "PatientSize",
    "PatientAddress",
    "PatientMotherBirthName",
    "PatientTelephoneNumbers",
    "OtherPatientIDs",
    "OtherPatientNames",
    "AccessionNumber",
    "ReferringPhysicianName",
    "ReferringPhysicianAddress",
    "ReferringPhysicianTelephoneNumbers",
    "PerformingPhysicianName",
    "OperatorsName",
    "RequestingPhysician",
    "PhysiciansOfRecord",
    "InstitutionName",
    "InstitutionAddress",
    "InstitutionalDepartmentName",
    "StationName",
    "DeviceSerialNumber",
)

# Date / time tags that re-identify a patient when combined with
# institution or modality info.
TEMPORAL_PHI_TAGS: tuple[str, ...] = (
    "StudyDate",
    "SeriesDate",
    "AcquisitionDate",
    "ContentDate",
    "AcquisitionDateTime",
    "StudyTime",
    "SeriesTime",
    "AcquisitionTime",
    "ContentTime",
)

ALL_PHI_TAGS: tuple[str, ...] = DIRECT_PHI_TAGS + TEMPORAL_PHI_TAGS


def scrub_phi_in_place(dataset: "Dataset") -> list[str]:
    """Replace PHI element values in a pydicom Dataset with empty strings.

    Returns the list of keyword names that were actually present and got
    scrubbed. Tags that were not present on this dataset are silently
    ignored — DICOM headers vary widely between vendors and modalities.

    The Dataset is mutated in place. Save to disk with
    `dataset.save_as(path)` afterwards if you want to persist the result.
    """
    scrubbed: list[str] = []
    for keyword in ALL_PHI_TAGS:
        if keyword in dataset:
            element = dataset.data_element(keyword)
            if element is not None:
                element.value = ""
                scrubbed.append(keyword)
    return scrubbed
