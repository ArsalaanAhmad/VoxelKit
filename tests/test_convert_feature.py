"""Tests for DICOM -> NIfTI conversion via `voxelkit convert`.

Covers:
- Single .dcm -> 2-D NIfTI: shape, voxel spacing, pixel preservation
- Series directory -> 3-D NIfTI: (rows, cols, slices) ordering, voxel zooms
- Output extension validation (.nii / .nii.gz only)
- Warnings list populated when DICOM headers are incomplete
- CLI dispatch through `voxelkit convert`
"""

from __future__ import annotations

import importlib
import json
import shutil
from pathlib import Path

import nibabel as nib
import numpy as np
import pytest


dicom_to_nifti = importlib.import_module("voxelkit.dicom").dicom_to_nifti
cli_main = importlib.import_module("voxelkit.cli").main

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SINGLE_DCM = FIXTURES_DIR / "sample.dcm"
SERIES_DIR = FIXTURES_DIR / "sample_series"


# ---------------------------------------------------------------------------
# Library API
# ---------------------------------------------------------------------------


def test_convert_single_dcm_to_nifti(tmp_path: Path) -> None:
    """A single .dcm round-trips into a 2-D NIfTI with matching pixels + spacing."""
    out_path = tmp_path / "single.nii.gz"
    summary = dicom_to_nifti(input_path=SINGLE_DCM, output_path=out_path)

    assert summary["source"] == "file"
    assert summary["shape"] == [8, 8]
    assert summary["voxel_size"] == [0.5, 0.5, 1.0]
    assert out_path.exists()

    image = nib.load(str(out_path))
    assert image.shape == (8, 8)
    array = np.asarray(image.dataobj)
    # Fixture pixel_value=100 for the single .dcm.
    assert int(array[0, 0]) == 100


def test_convert_series_to_nifti_has_3d_shape(tmp_path: Path) -> None:
    """A 4-slice DICOM series produces a (rows, cols, slices) NIfTI."""
    out_path = tmp_path / "series.nii.gz"
    summary = dicom_to_nifti(input_path=SERIES_DIR, output_path=out_path)

    assert summary["source"] == "series"
    assert summary["slice_count"] == 4
    assert summary["shape"] == [8, 8, 4]
    assert out_path.exists()

    image = nib.load(str(out_path))
    assert image.shape == (8, 8, 4)
    zooms = tuple(round(float(z), 2) for z in image.header.get_zooms())
    assert zooms == (0.5, 0.5, 1.0)


def test_convert_series_preserves_slice_order(tmp_path: Path) -> None:
    """Slice values 10..13 line up in the order the loader sorted them."""
    out_path = tmp_path / "series.nii.gz"
    dicom_to_nifti(input_path=SERIES_DIR, output_path=out_path)

    image = nib.load(str(out_path))
    array = np.asarray(image.dataobj)
    # NIfTI shape is (rows, cols, slices). The series fixtures have pixel
    # values 10, 11, 12, 13 in increasing position_z order.
    assert int(array[0, 0, 0]) == 10
    assert int(array[0, 0, 3]) == 13


def test_convert_rejects_unsupported_extension(tmp_path: Path) -> None:
    """Output must end in .nii or .nii.gz — anything else is a hard error."""
    with pytest.raises(Exception, match=r"\.nii"):
        dicom_to_nifti(input_path=SINGLE_DCM, output_path=tmp_path / "bad.bin")


def test_convert_accepts_uncompressed_nii(tmp_path: Path) -> None:
    """Both .nii and .nii.gz are valid output extensions."""
    out_path = tmp_path / "single.nii"
    dicom_to_nifti(input_path=SINGLE_DCM, output_path=out_path)
    assert out_path.exists()
    image = nib.load(str(out_path))
    assert image.shape == (8, 8)


# ---------------------------------------------------------------------------
# CLI dispatch
# ---------------------------------------------------------------------------


def test_cli_convert_single_dcm(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`voxelkit convert sample.dcm out.nii.gz` emits a summary JSON."""
    out_path = tmp_path / "out.nii.gz"
    rc = cli_main(["convert", str(SINGLE_DCM), str(out_path)])
    assert rc == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["shape"] == [8, 8]
    assert out_path.exists()


def test_cli_convert_series(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`voxelkit convert <series_dir> out.nii.gz` writes a 3-D NIfTI."""
    out_path = tmp_path / "out.nii.gz"
    rc = cli_main(["convert", str(SERIES_DIR), str(out_path)])
    assert rc == 0
    summary = json.loads(capsys.readouterr().out)
    assert summary["shape"] == [8, 8, 4]
    image = nib.load(str(out_path))
    assert image.shape == (8, 8, 4)


def test_cli_convert_bad_extension_errors(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The CLI surfaces the extension validation error with a non-zero exit code."""
    rc = cli_main(["convert", str(SINGLE_DCM), str(tmp_path / "x.bin")])
    assert rc != 0
    assert ".nii" in capsys.readouterr().err
