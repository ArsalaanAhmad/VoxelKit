"""Shared DICOM loading for single files and series directories.

Distinguishes two input shapes:

- **Single file** (`scan.dcm`): one slice, returned as a 2-D pixel array
  plus its `Dataset`. Multi-frame DICOMs (`NumberOfFrames > 1`) are still
  loaded from a single file and may produce 3-D arrays.

- **Series directory** (`./series/`): a folder of per-slice `.dcm` files
  that form a single 3-D volume. Slices are sorted by
  `ImagePositionPatient[2]` when present (the patient-relative Z axis),
  falling back to `InstanceNumber`, then filename. The first slice's
  `Dataset` is treated as the canonical header for series-level metadata.

Both code paths return a `LoadedDicom` dataclass so callers don't have
to branch on input shape themselves.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import pydicom
from pydicom.errors import InvalidDicomError

from voxelkit.core.errors import ValidationError

if TYPE_CHECKING:
    from pydicom.dataset import Dataset


@dataclass(frozen=True)
class LoadedDicom:
    """Pixel data plus header for a single .dcm or a sorted series directory.

    `pixel_array` is always at least 2-D. For a single-frame .dcm it's
    2-D (rows, cols); for a multi-frame .dcm or a sorted directory it's
    3-D (slices, rows, cols).

    `representative_dataset` is the header used for series-level metadata
    (modality, voxel size, PHI fields). For a directory load this is the
    first slice after sorting.
    """

    pixel_array: np.ndarray
    representative_dataset: "Dataset"
    source: str  # "file" or "series"
    slice_count: int


def load_dicom(path: str | Path) -> LoadedDicom:
    """Load a single .dcm file or a series directory into a unified result.

    Raises:
        ValidationError: when the path does not exist, the file is not a
            valid DICOM dataset, or a directory contains no .dcm files /
            no readable pixel data.
    """
    resolved = Path(path)
    if not resolved.exists():
        raise ValidationError(f"DICOM path does not exist: {path}")

    if resolved.is_dir():
        return _load_series_directory(resolved)
    return _load_single_file(resolved)


def _load_single_file(file_path: Path) -> LoadedDicom:
    try:
        dataset = pydicom.dcmread(str(file_path))
    except InvalidDicomError as exc:
        raise ValidationError("Invalid or unreadable DICOM file.") from exc
    except (OSError, ValueError) as exc:
        raise ValidationError("Could not open DICOM file.") from exc

    pixel_array = _extract_pixel_array(dataset, source=str(file_path))
    # A multi-frame .dcm reports its slice count via NumberOfFrames; a
    # single-frame file is 1.
    slice_count = int(getattr(dataset, "NumberOfFrames", 1) or 1)

    return LoadedDicom(
        pixel_array=pixel_array,
        representative_dataset=dataset,
        source="file",
        slice_count=slice_count,
    )


def _load_series_directory(directory: Path) -> LoadedDicom:
    dcm_paths = sorted(
        entry
        for entry in directory.iterdir()
        if entry.is_file() and entry.suffix.lower() == ".dcm"
    )
    if not dcm_paths:
        raise ValidationError(f"Directory contains no .dcm files: {directory}")

    datasets: list["Dataset"] = []
    for slice_path in dcm_paths:
        try:
            datasets.append(pydicom.dcmread(str(slice_path)))
        except InvalidDicomError as exc:
            raise ValidationError(
                f"Invalid DICOM file in series directory: {slice_path.name}"
            ) from exc
        except (OSError, ValueError) as exc:
            raise ValidationError(
                f"Could not open DICOM file in series directory: {slice_path.name}"
            ) from exc

    sorted_datasets = _sort_series(datasets, dcm_paths)
    slice_arrays = [_extract_pixel_array(ds, source=str(p)) for ds, p in sorted_datasets]

    # Every slice in a well-formed series shares the same in-plane shape and
    # dtype. Mismatched series are surfaced as a ValidationError so users
    # know their directory contains more than one acquisition.
    first_shape = slice_arrays[0].shape
    for index, slice_array in enumerate(slice_arrays):
        if slice_array.shape != first_shape:
            raise ValidationError(
                "Series directory contains slices with mismatched shapes "
                f"(slice 0 is {first_shape}, slice {index} is {slice_array.shape}). "
                "The directory likely mixes multiple acquisitions."
            )

    volume = np.stack(slice_arrays, axis=0)
    return LoadedDicom(
        pixel_array=volume,
        representative_dataset=sorted_datasets[0][0],
        source="series",
        slice_count=len(slice_arrays),
    )


def _sort_series(
    datasets: list["Dataset"], paths: list[Path]
) -> list[tuple["Dataset", Path]]:
    """Sort a series of slice datasets into Z-axis order.

    Preference order:
      1. `ImagePositionPatient[2]` (patient-relative Z, the DICOM standard).
      2. `InstanceNumber` (vendor convention; less reliable on cine series).
      3. Filename (alphabetical fallback for stripped-down test fixtures).

    Only one strategy is applied — picking the most precise key available
    across the whole series. This avoids subtle mixing where some slices
    have a Z position and others don't.
    """
    pairs = list(zip(datasets, paths))

    if all(_has_image_position(ds) for ds, _ in pairs):
        return sorted(pairs, key=lambda pair: float(pair[0].ImagePositionPatient[2]))

    if all(_has_instance_number(ds) for ds, _ in pairs):
        return sorted(pairs, key=lambda pair: int(pair[0].InstanceNumber))

    return sorted(pairs, key=lambda pair: pair[1].name)


def _has_image_position(dataset: "Dataset") -> bool:
    position = getattr(dataset, "ImagePositionPatient", None)
    return position is not None and len(position) >= 3


def _has_instance_number(dataset: "Dataset") -> bool:
    return getattr(dataset, "InstanceNumber", None) is not None


def _extract_pixel_array(dataset: "Dataset", *, source: str) -> np.ndarray:
    """Pull pixel data off a Dataset with a helpful error on common failures."""
    try:
        array = dataset.pixel_array
    except AttributeError as exc:
        raise ValidationError(
            f"DICOM file has no pixel data: {source}"
        ) from exc
    except Exception as exc:  # pydicom raises many internal types here
        raise ValidationError(
            f"Could not decode DICOM pixel data ({type(exc).__name__}): {source}"
        ) from exc

    return np.asarray(array)
