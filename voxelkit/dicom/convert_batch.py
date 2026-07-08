"""Batch DICOM-to-NIfTI conversion: discover .dcm files and series directories,
convert each to a NIfTI volume, and return a JSON-serialisable summary.

Follows the same resilience pattern as `anonymise_directory` and
`report_batch` - failures are collected per input, never raised mid-run.
A directory with multiple .dcm files is treated as a single series; a
lone .dcm is treated as a standalone file.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import TypedDict

from voxelkit.core.errors import ValidationError
from voxelkit.dicom.convert import DicomConvertResult, dicom_to_nifti


class ConvertBatchFailure(TypedDict):
    """Single-input failure record from a batch conversion run."""

    input_path: str
    error: str


class ConvertBatchResult(TypedDict):
    """Top-level return value of `convert_batch`."""

    input_dir: str
    output_dir: str
    recursive: bool
    total_dicom_inputs: int
    successful_conversions: int
    failed_conversions: int
    conversions: list[DicomConvertResult]
    failures: list[ConvertBatchFailure]


def convert_batch(
    input_dir: str | Path,
    output_dir: str | Path,
    *,
    recursive: bool = True,
) -> ConvertBatchResult:
    """Convert all DICOM files and series under `input_dir` to NIfTI volumes.

    Args:
        input_dir: Root path to scan for `.dcm` files and series directories.
        output_dir: Where to write the converted NIfTI volumes. Created if
            needed. Output filenames mirror the relative directory structure.
        recursive: Walk subdirectories. Defaults to True.

    Returns:
        A `ConvertBatchResult` summarising what was converted and what
        failed. Failures are collected per input; the function never
        raises mid-run.

    Raises:
        ValidationError: when `input_dir` does not exist or is not a
            directory, or when `output_dir` resolves to the same path.
    """
    input_root = Path(input_dir)
    output_root = Path(output_dir)

    if not input_root.exists():
        raise ValidationError(f"Input directory does not exist: {input_dir}")
    if not input_root.is_dir():
        raise ValidationError(f"Input path is not a directory: {input_dir}")
    if input_root.resolve() == output_root.resolve():
        raise ValidationError(
            "Input and output directories must be different."
        )

    output_root.mkdir(parents=True, exist_ok=True)

    inputs = _discover_dicom_inputs(input_root, recursive=recursive)

    conversions: list[DicomConvertResult] = []
    failures: list[ConvertBatchFailure] = []

    for source_path, output_name in inputs:
        relative_parent = source_path.relative_to(input_root).parent if source_path.is_file() else source_path.relative_to(input_root)
        out_path = output_root / relative_parent / output_name

        try:
            result = dicom_to_nifti(input_path=source_path, output_path=out_path)
            conversions.append(result)
        except (ValidationError, OSError, ValueError, Exception) as exc:
            failures.append({"input_path": str(source_path), "error": str(exc)})

    return {
        "input_dir": str(input_root.resolve()),
        "output_dir": str(output_root.resolve()),
        "recursive": recursive,
        "total_dicom_inputs": len(inputs),
        "successful_conversions": len(conversions),
        "failed_conversions": len(failures),
        "conversions": conversions,
        "failures": failures,
    }


def _discover_dicom_inputs(
    root: Path, *, recursive: bool
) -> list[tuple[Path, str]]:
    """Find DICOM inputs under `root` and return (source_path, output_name) pairs.

    Groups .dcm files by parent directory:
    - A directory with multiple .dcm files is a series -> convert the directory
      as one volume, named after the directory.
    - A lone .dcm in a directory is a standalone file -> convert individually.
    """
    iterator = root.rglob("*.dcm") if recursive else root.glob("*.dcm")
    dcm_paths = sorted(path for path in iterator if path.is_file())

    by_parent: defaultdict[Path, list[Path]] = defaultdict(list)
    for p in dcm_paths:
        by_parent[p.parent].append(p)

    inputs: list[tuple[Path, str]] = []
    for parent_dir, files in sorted(by_parent.items()):
        if len(files) > 1:
            inputs.append((parent_dir, f"{parent_dir.name}.nii.gz"))
        else:
            inputs.append((files[0], f"{files[0].stem}.nii.gz"))

    return inputs
