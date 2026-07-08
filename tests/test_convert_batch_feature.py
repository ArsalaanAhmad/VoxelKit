"""Tests for batch DICOM -> NIfTI conversion via `voxelkit convert-batch`.

Covers:
- Library: recursive and non-recursive discovery, mixed single + series,
  graceful failure collection, empty directory
- CLI: JSON to stdout, stderr summary line
"""

from __future__ import annotations

import importlib
import json
import shutil
from pathlib import Path

import nibabel as nib
import pytest

convert_batch = importlib.import_module("voxelkit.dicom").convert_batch
cli_main = importlib.import_module("voxelkit.cli").main

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SINGLE_DCM = FIXTURES_DIR / "sample.dcm"
SERIES_DIR = FIXTURES_DIR / "sample_series"


def _build_input_tree(tmp_path: Path) -> Path:
    """Copy the DICOM fixtures into a writable tree and return its root."""
    root = tmp_path / "in"
    root.mkdir()
    shutil.copy(SINGLE_DCM, root / "lone.dcm")
    series = root / "myseries"
    series.mkdir()
    for slice_path in sorted(SERIES_DIR.glob("*.dcm")):
        shutil.copy(slice_path, series / slice_path.name)
    return root


# ---------------------------------------------------------------------------
# Library API
# ---------------------------------------------------------------------------


def test_convert_batch_single_and_series(tmp_path: Path) -> None:
    """Discovers both a lone .dcm and a multi-file series and converts each."""
    input_dir = _build_input_tree(tmp_path)
    output_dir = tmp_path / "output"

    result = convert_batch(input_dir, output_dir)

    assert result["recursive"] is True
    assert result["total_dicom_inputs"] == 2
    assert result["successful_conversions"] == 2
    assert result["failed_conversions"] == 0
    assert len(result["conversions"]) == 2
    assert len(result["failures"]) == 0

    output_files = list(output_dir.rglob("*.nii.gz"))
    assert len(output_files) == 2


def test_convert_batch_non_recursive(tmp_path: Path) -> None:
    """With recursive=False, only top-level .dcm files are discovered."""
    input_dir = _build_input_tree(tmp_path)
    output_dir = tmp_path / "output"

    result = convert_batch(input_dir, output_dir, recursive=False)

    assert result["total_dicom_inputs"] == 1
    assert result["successful_conversions"] == 1


def test_convert_batch_empty_directory(tmp_path: Path) -> None:
    """An empty directory produces zero inputs and no errors."""
    input_dir = tmp_path / "empty"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    result = convert_batch(input_dir, output_dir)

    assert result["total_dicom_inputs"] == 0
    assert result["successful_conversions"] == 0
    assert result["failed_conversions"] == 0


def test_convert_batch_collects_failures(tmp_path: Path) -> None:
    """A corrupt .dcm is recorded as a failure without aborting the run."""
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "output"
    input_dir.mkdir()

    shutil.copy(SINGLE_DCM, input_dir / "good.dcm")

    bad_dir = input_dir / "broken"
    bad_dir.mkdir()
    (bad_dir / "bad.dcm").write_bytes(b"not-dicom-data")

    result = convert_batch(input_dir, output_dir)

    assert result["total_dicom_inputs"] == 2
    assert result["successful_conversions"] == 1
    assert result["failed_conversions"] == 1
    assert len(result["failures"]) == 1


def test_convert_batch_rejects_missing_input(tmp_path: Path) -> None:
    """Raises ValidationError when input_dir does not exist."""
    with pytest.raises(Exception, match="does not exist"):
        convert_batch(tmp_path / "nope", tmp_path / "out")


def test_convert_batch_rejects_same_input_output(tmp_path: Path) -> None:
    """Raises ValidationError when input and output are the same directory."""
    d = tmp_path / "same"
    d.mkdir()
    with pytest.raises(Exception, match="must be different"):
        convert_batch(d, d)


def test_convert_batch_output_files_are_valid_nifti(tmp_path: Path) -> None:
    """Every output .nii.gz is loadable by nibabel with a sane shape."""
    input_dir = _build_input_tree(tmp_path)
    output_dir = tmp_path / "output"

    convert_batch(input_dir, output_dir)

    for nii_path in output_dir.rglob("*.nii.gz"):
        img = nib.load(str(nii_path))
        assert len(img.shape) >= 2


def test_convert_batch_with_fixtures(tmp_path: Path) -> None:
    """Converts the real test fixtures directory directly."""
    output_dir = tmp_path / "output"
    result = convert_batch(FIXTURES_DIR, output_dir)

    assert result["successful_conversions"] >= 1
    assert len(result["conversions"]) >= 1


# ---------------------------------------------------------------------------
# CLI dispatch
# ---------------------------------------------------------------------------


def test_cli_convert_batch(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """CLI emits JSON to stdout and a summary to stderr."""
    input_dir = _build_input_tree(tmp_path)
    output_dir = tmp_path / "output"

    rc = cli_main(["convert-batch", str(input_dir), "--output", str(output_dir)])
    assert rc == 0

    captured = capsys.readouterr()
    result = json.loads(captured.out)
    assert result["successful_conversions"] == 2
    assert "Converted 2 of 2" in captured.err


def test_cli_convert_batch_missing_output_flag(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """CLI exits non-zero when --output is not provided."""
    with pytest.raises(SystemExit) as exc_info:
        cli_main(["convert-batch", str(tmp_path)])
    assert exc_info.value.code != 0
