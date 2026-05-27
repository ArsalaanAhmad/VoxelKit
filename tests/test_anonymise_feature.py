"""Tests for `voxelkit anonymise` — both library and CLI dispatch.

Covers:
- Output tree mirrors input structure, non-.dcm files skipped
- Every configured PHI tag is scrubbed
- Pixel data + clinical metadata (Modality, dimensions) preserved
- Source directory left untouched
- in == out rejected so users cannot self-overwrite
- Library returns a summary dict with per-tag scrub counts
- Recursive vs. non-recursive traversal
"""

from __future__ import annotations

import importlib
import json
import shutil
from pathlib import Path

import pydicom
import pytest


anonymise_directory = importlib.import_module("voxelkit.dicom").anonymise_directory
cli_main = importlib.import_module("voxelkit.cli").main

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SINGLE_DCM = FIXTURES_DIR / "sample.dcm"
SERIES_DIR = FIXTURES_DIR / "sample_series"


def _build_input_tree(tmp_path: Path) -> Path:
    """Copy the DICOM fixtures into a writable tree and return its root."""
    root = tmp_path / "in"
    nested = root / "study1"
    nested.mkdir(parents=True)
    shutil.copy(SINGLE_DCM, nested / "single.dcm")
    for slice_path in sorted(SERIES_DIR.glob("*.dcm")):
        shutil.copy(slice_path, nested / slice_path.name)
    # Drop in a non-DICOM file the scanner should skip.
    (root / "README.txt").write_text("not a dicom")
    return root


# ---------------------------------------------------------------------------
# Library API
# ---------------------------------------------------------------------------


def test_anonymise_directory_scrubs_every_dcm(tmp_path: Path) -> None:
    """anonymise_directory() processes every .dcm and skips non-DICOM files."""
    in_dir = _build_input_tree(tmp_path)
    out_dir = tmp_path / "out"

    summary = anonymise_directory(input_dir=in_dir, output_dir=out_dir)

    assert summary["total_dcm_files"] == 5  # 1 single + 4 series slices
    assert summary["files_anonymised"] == 5
    assert summary["files_failed"] == 0
    assert summary["failures"] == []

    assert (out_dir / "study1" / "single.dcm").exists()
    assert (out_dir / "study1" / "slice_000.dcm").exists()
    # Non-DICOM file is left out.
    assert not (out_dir / "README.txt").exists()


def test_anonymise_clears_phi_tags(tmp_path: Path) -> None:
    """Every PHI tag listed in voxelkit.dicom.phi gets emptied in the output."""
    in_dir = _build_input_tree(tmp_path)
    out_dir = tmp_path / "out"

    anonymise_directory(input_dir=in_dir, output_dir=out_dir)

    output = pydicom.dcmread(str(out_dir / "study1" / "single.dcm"))
    assert str(output.PatientName) == ""
    assert str(output.PatientID) == ""
    assert str(output.PatientBirthDate) == ""
    assert str(output.AccessionNumber) == ""
    assert str(output.InstitutionName) == ""
    assert str(output.StudyDate) == ""
    assert str(output.StudyTime) == ""


def test_anonymise_preserves_pixel_and_clinical_metadata(tmp_path: Path) -> None:
    """Pixel data and non-PHI clinical fields survive anonymisation untouched."""
    in_dir = _build_input_tree(tmp_path)
    out_dir = tmp_path / "out"

    anonymise_directory(input_dir=in_dir, output_dir=out_dir)

    output = pydicom.dcmread(str(out_dir / "study1" / "single.dcm"))
    assert output.Modality == "CT"
    assert output.Rows == 8
    assert output.Columns == 8
    assert int(output.pixel_array[0, 0]) == 100


def test_anonymise_leaves_source_untouched(tmp_path: Path) -> None:
    """Source files are not mutated by the anonymise run."""
    in_dir = _build_input_tree(tmp_path)
    out_dir = tmp_path / "out"

    anonymise_directory(input_dir=in_dir, output_dir=out_dir)

    source = pydicom.dcmread(str(in_dir / "study1" / "single.dcm"))
    assert str(source.PatientName) == "Test^Patient"


def test_anonymise_summary_scrubbed_tag_counts(tmp_path: Path) -> None:
    """Summary scrubbed_tag_counts reflects how many files carried each tag."""
    in_dir = _build_input_tree(tmp_path)
    out_dir = tmp_path / "out"

    summary = anonymise_directory(input_dir=in_dir, output_dir=out_dir)

    counts = summary["scrubbed_tag_counts"]
    # PatientName was set on every fixture, so all 5 .dcm files should have it.
    assert counts["PatientName"] == 5
    assert counts["PatientID"] == 5
    assert counts["StudyDate"] == 5


def test_anonymise_refuses_in_equals_out(tmp_path: Path) -> None:
    """Refuse to scrub a directory back into itself — would corrupt the source."""
    in_dir = _build_input_tree(tmp_path)
    with pytest.raises(Exception, match="refuses to overwrite"):
        anonymise_directory(input_dir=in_dir, output_dir=in_dir)


def test_anonymise_non_recursive_only_top_level(tmp_path: Path) -> None:
    """recursive=False skips files inside subdirectories."""
    in_dir = _build_input_tree(tmp_path)
    out_dir = tmp_path / "out"

    summary = anonymise_directory(input_dir=in_dir, output_dir=out_dir, recursive=False)
    # All fixtures live one level deep under study1/, so non-recursive sees nothing.
    assert summary["total_dcm_files"] == 0
    assert summary["files_anonymised"] == 0


# ---------------------------------------------------------------------------
# CLI dispatch
# ---------------------------------------------------------------------------


def test_cli_anonymise_emits_summary_and_creates_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`voxelkit anonymise <in> --output <out>` prints summary JSON to stdout."""
    in_dir = _build_input_tree(tmp_path)
    out_dir = tmp_path / "out"

    rc = cli_main(["anonymise", str(in_dir), "--output", str(out_dir)])
    assert rc == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["files_anonymised"] == 5
    assert (out_dir / "study1" / "single.dcm").exists()


def test_cli_anonymise_in_equals_out_exits_nonzero(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """CLI surfaces the in==out validation error with a non-zero exit code."""
    in_dir = _build_input_tree(tmp_path)
    rc = cli_main(["anonymise", str(in_dir), "--output", str(in_dir)])
    assert rc != 0
    assert "refuses to overwrite" in capsys.readouterr().err
