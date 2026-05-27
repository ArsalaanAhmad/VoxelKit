"""Skeleton for adding a new file format to VoxelKit.

Copy this file into `voxelkit/<your_format>/` and split it into three modules
(`inspect.py`, `preview.py`, `report.py`) following the existing format
packages (`voxelkit/nifti/`, `voxelkit/tiff/`, `voxelkit/h5/`, `voxelkit/npy/`).
This single-file template exists so contributors can read every signature,
return contract, and registration step in one place before diverging into
the three-file layout.

Three callables make a format complete:

    inspect_fn  — reads metadata only, returns a JSON-serialisable dict.
    preview_fn  — reads pixel data, returns PNG bytes for a single 2D slice.
    report_fn   — reads pixel data, returns a QA-statistics dict.

All three must conform to the Protocol classes in `voxelkit.core.handler`
(`InspectFn`, `PreviewFn`, `ReportFn`). The CLI's `FormatRoute` checks the
arity at registration time; static type-checkers verify the deeper contract.

Once your three modules exist, register them in `voxelkit/cli.py` via the
`register_format(FormatRoute(...))` block at the bottom of
`_register_builtin_formats`, then wire library-level dispatch in
`voxelkit/__init__.py` (see `inspect_file`, `preview_file`, `report_file`).
"""

from __future__ import annotations

import argparse
import os
from typing import Any

import numpy as np

from voxelkit.core.errors import ValidationError
from voxelkit.core.image_utils import to_png_bytes
from voxelkit.core.normalization import normalize_to_uint8
from voxelkit.core.report import build_array_report
from voxelkit.core.types import FileReportResult
from voxelkit.core.validation import require_supported_extension, resolve_slice_index


# ─── Step 1. Declare your extensions ─────────────────────────────────────────
#
# Add these to `voxelkit/core/formats.py` so the cross-format helpers
# (`detect_format`, `SUPPORTED_DATA_EXTENSIONS`, the batch-report scanner)
# pick the format up automatically.

EXAMPLE_EXTENSIONS: tuple[str, ...] = (".example",)


# ─── Step 2. inspect ─────────────────────────────────────────────────────────


def inspect(file_path: str) -> dict[str, Any]:
    """Return metadata for a single file.

    Returns:
        A JSON-serialisable dictionary. The minimum useful schema is:

            {
                "filename": str,    # os.path.basename(file_path)
                "format":   str,    # the same name registered in FormatRoute
                "shape":    list[int],
                "ndim":     int,
                "dtype":    str,
            }

        Add format-specific keys (e.g. `voxel_size`, `axes`, `page_count`)
        as siblings — do not nest them under a `metadata` sub-dict.

    Raises:
        ValidationError: when the file cannot be opened or parsed.
        UnsupportedFormatError: when the extension does not match.
    """
    require_supported_extension(
        file_path=file_path,
        extensions=EXAMPLE_EXTENSIONS,
        message="Unsupported file type. Please provide an .example file.",
    )

    # Replace with the real loader for your format. Prefer lazy / metadata-only
    # access — `inspect` is allowed to be slow on weird inputs but is expected
    # to be cheap on healthy files.
    try:
        array = _load_pixel_data(file_path)
    except Exception as exc:  # noqa: BLE001  (narrow this in real implementations)
        raise ValidationError("Invalid or unreadable EXAMPLE file.") from exc

    return {
        "filename": os.path.basename(file_path),
        "format": "example",
        "shape": list(array.shape),
        "ndim": int(array.ndim),
        "dtype": str(array.dtype),
    }


# ─── Step 3. preview ─────────────────────────────────────────────────────────


def preview(
    file_path: str,
    *,
    axis: int = 0,
    slice_index: int | None = None,
    as_array: bool = False,
) -> bytes | np.ndarray:
    """Return a single 2D slice as PNG bytes (or as a uint8 array).

    The library function takes format-specific keyword arguments. The CLI
    adapter (see Step 5) translates `argparse.Namespace` into these kwargs
    and rejects flags that do not apply to this format.

    Returns:
        - PNG-encoded bytes by default.
        - A 2D `uint8` numpy array when `as_array=True`. Used by the GUI and
          the HTML report to embed thumbnails without re-decoding PNGs.

    Raises:
        ValidationError: when the file cannot produce a 2D slice (e.g. the
            data is 1-D, the requested `slice_index` is out of bounds, or
            the requested `axis` is invalid).
    """
    require_supported_extension(
        file_path=file_path,
        extensions=EXAMPLE_EXTENSIONS,
        message="Unsupported file type. Please provide an .example file.",
    )

    array = _load_pixel_data(file_path)

    if array.ndim < 2:
        raise ValidationError("EXAMPLE data must be at least 2-dimensional for preview.")

    if axis < 0 or axis >= array.ndim:
        raise ValidationError(
            f"axis out of bounds for {array.ndim}-D array. Valid range: 0 to {array.ndim - 1}."
        )

    resolved_index = resolve_slice_index(
        length=array.shape[axis],
        slice_index=slice_index,
        context=f"axis {axis}",
    )

    indexer: list[slice | int] = [slice(None)] * array.ndim
    indexer[axis] = resolved_index
    slice_2d = np.asarray(array[tuple(indexer)], dtype=np.float32)
    slice_2d = np.squeeze(slice_2d)

    if slice_2d.ndim != 2:
        raise ValidationError("Unable to extract a 2D slice from the provided EXAMPLE file.")

    normalized = normalize_to_uint8(slice_2d)
    if as_array:
        return normalized
    return to_png_bytes(normalized)


# ─── Step 4. report ──────────────────────────────────────────────────────────


def report(file_path: str) -> FileReportResult:
    """Return a QA-statistics dict for a single file.

    The returned dict always matches `FileReportResult` in
    `voxelkit.core.types`. The standard `build_array_report` helper does all
    the per-pixel work (min/max/mean/std/NaN/Inf/zero-fraction + the warning
    list); your job is to load the array and pass it in.

    Raises:
        ValidationError: when the file cannot be opened or its array is not
            numeric.
    """
    require_supported_extension(
        file_path=file_path,
        extensions=EXAMPLE_EXTENSIONS,
        message="Unsupported file type. Please provide an .example file.",
    )

    array = _load_pixel_data(file_path)
    return build_array_report(
        array=array,
        filename=os.path.basename(file_path),
        format_name="example",
        preview_supported=array.ndim >= 2,
    )


# ─── Step 5. CLI adapters (live in voxelkit/cli.py) ──────────────────────────
#
# These are NOT part of your format module. They live in `voxelkit/cli.py`
# and conform to the InspectFn / PreviewFn / ReportFn Protocols defined in
# `voxelkit.core.handler`. They translate `argparse.Namespace` into kwargs
# for the library functions above and reject flags that do not apply.
#
# Copy these into `voxelkit/cli.py`, renaming `example` → your format:
#
#     def _preview_example(file_path: str, args: argparse.Namespace) -> bytes:
#         if args.plane is not None:
#             raise ValidationError("--plane is only valid for NIfTI preview.")
#         if args.dataset is not None:
#             raise ValidationError("--dataset is only valid for HDF5 preview.")
#         if args.array_name is not None:
#             raise ValidationError("--array is only valid for NumPy NPZ preview.")
#         return preview_example(
#             file_path=file_path,
#             axis=0 if args.axis is None else args.axis,
#             slice_index=args.slice_index,
#         )
#
#     def _report_example(file_path: str, args: argparse.Namespace) -> dict[str, Any]:
#         if args.dataset is not None:
#             raise ValidationError("--dataset is only valid for HDF5 preview/report.")
#         if args.array_name is not None:
#             raise ValidationError("--array is only valid for NumPy NPZ preview/report.")
#         return report_example(file_path)
#
# Then register the route inside `_register_builtin_formats`:
#
#     register_format(
#         FormatRoute(
#             name="example",
#             extensions=EXAMPLE_EXTENSIONS,
#             inspect_fn=inspect_example,
#             preview_fn=_preview_example,
#             report_fn=_report_example,
#         )
#     )
#
# `FormatRoute.__post_init__` validates the three callables against
# InspectFn / PreviewFn / ReportFn at registration time — a wrong arity
# raises TypeError before any user runs the CLI.


# ─── Step 6. Wire library-level dispatch in voxelkit/__init__.py ─────────────
#
# Add a branch to `inspect_file`, `preview_file`, and `report_file`:
#
#     if format_name == "example":
#         return preview_example(str(file_path), axis=axis, slice_index=slice_index)
#
# This lets Python users call the format the same way they call NIfTI:
#
#     from voxelkit import preview_file
#     preview_file("scan.example", axis=0, slice_index=10)


# ─── Step 7. Tests + fixtures ────────────────────────────────────────────────
#
# 1. Add a fixture generator to `tests/create_fixtures.py` that writes a
#    minimal synthetic EXAMPLE file — small enough to keep the suite fast.
# 2. Create `tests/test_example_feature.py` that exercises inspect / preview
#    / report and the CLI dispatch path (`importlib.import_module("voxelkit.cli").main`).
# 3. Never check real patient data, proprietary scans, or large binaries
#    into the repo. Synthetic arrays only.


def _load_pixel_data(file_path: str) -> np.ndarray:
    """Replace with the real loader for your format.

    For inspiration, see:
        - `voxelkit/nifti/metadata.py` — uses `nibabel.load`
        - `voxelkit/tiff/inspect.py`   — uses `tifffile.TiffFile`
        - `voxelkit/h5/inspect.py`     — uses `h5py.File`
        - `voxelkit/npy/inspect.py`    — uses `numpy.load`
    """
    raise NotImplementedError("Replace _load_pixel_data with your format's loader.")
