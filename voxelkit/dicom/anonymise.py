"""Batch DICOM anonymisation: scrub PHI tags and write to an output tree.

This is a deliberately conservative implementation:

- Only emits files for inputs that pydicom can actually parse. Non-DICOM
  files (READMEs, segmentation masks, mixed datasets) are skipped and
  reported in the summary.
- Mirrors the input directory structure under the output directory, so
  callers can keep their existing per-study / per-series folder layout.
- Scrubs only the PHI tags enumerated in `voxelkit.dicom.phi` — does not
  regenerate UIDs. Series and study grouping is preserved so anonymised
  datasets remain navigable.
- Overwrites destination files. Anonymise is an explicit user-initiated
  rewrite; refusing to overwrite would make repeated runs noisy without
  meaningful safety.

The function returns a JSON-serialisable summary that the CLI prints to
stdout. Failures are collected, not raised — partial success on a big
dataset is more useful than a hard abort on the first bad file.
"""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

import pydicom
from pydicom.errors import InvalidDicomError

from voxelkit.core.errors import ValidationError
from voxelkit.dicom.phi import scrub_phi_in_place


class AnonymiseFailure(TypedDict):
    """Single-file failure record from a batch anonymisation run."""

    file_path: str
    error: str


class AnonymiseSummary(TypedDict):
    """Top-level return value of `anonymise_directory`.

    `scrubbed_tag_counts` maps each PHI tag keyword to the number of files
    in which it was actually present and scrubbed. Useful both as
    confirmation that anonymisation ran and as a heads-up on which tags
    your dataset actually carried.
    """

    input_dir: str
    output_dir: str
    total_dcm_files: int
    files_anonymised: int
    files_failed: int
    failures: list[AnonymiseFailure]
    scrubbed_tag_counts: dict[str, int]


def anonymise_directory(
    input_dir: str | Path,
    output_dir: str | Path,
    *,
    recursive: bool = True,
) -> AnonymiseSummary:
    """Scrub PHI from every .dcm under `input_dir` and write to `output_dir`.

    Args:
        input_dir: Root path to scan for `.dcm` files.
        output_dir: Where to write the scrubbed copies. Created if needed.
            Mirrors the relative directory structure under `input_dir`.
        recursive: Walk subdirectories. Defaults to True.

    Returns:
        An `AnonymiseSummary` describing what was processed, skipped, and
        scrubbed. Failures are collected per file; the function never
        raises mid-run.

    Raises:
        ValidationError: when `input_dir` does not exist or is not a
            directory, or when `output_dir` is the same path as
            `input_dir` (in-place rewrites would corrupt the source).
    """
    input_root = Path(input_dir)
    output_root = Path(output_dir)

    if not input_root.exists():
        raise ValidationError(f"Input directory does not exist: {input_dir}")
    if not input_root.is_dir():
        raise ValidationError(f"Input path is not a directory: {input_dir}")
    if input_root.resolve() == output_root.resolve():
        raise ValidationError(
            "Input and output directories must be different — anonymise refuses to overwrite the source tree."
        )

    output_root.mkdir(parents=True, exist_ok=True)

    iterator = input_root.rglob("*.dcm") if recursive else input_root.glob("*.dcm")
    dcm_paths = sorted(path for path in iterator if path.is_file())

    failures: list[AnonymiseFailure] = []
    scrubbed_counts: dict[str, int] = {}
    files_anonymised = 0

    for source_path in dcm_paths:
        relative = source_path.relative_to(input_root)
        destination = output_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)

        try:
            dataset = pydicom.dcmread(str(source_path))
            scrubbed = scrub_phi_in_place(dataset)
            dataset.save_as(str(destination))
        except InvalidDicomError as exc:
            failures.append({"file_path": str(source_path), "error": f"Invalid DICOM: {exc}"})
            continue
        except (OSError, ValueError) as exc:
            failures.append(
                {"file_path": str(source_path), "error": f"{type(exc).__name__}: {exc}"}
            )
            continue

        files_anonymised += 1
        for keyword in scrubbed:
            scrubbed_counts[keyword] = scrubbed_counts.get(keyword, 0) + 1

    return {
        "input_dir": str(input_root.resolve()),
        "output_dir": str(output_root.resolve()),
        "total_dcm_files": len(dcm_paths),
        "files_anonymised": files_anonymised,
        "files_failed": len(failures),
        "failures": failures,
        "scrubbed_tag_counts": dict(sorted(scrubbed_counts.items())),
    }
