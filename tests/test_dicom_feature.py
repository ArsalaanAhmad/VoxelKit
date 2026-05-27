"""Tests for DICOM inspect, preview, and report — single file and series directory.

Covers:
- inspect() metadata for single .dcm and series directory
- PHI stripping by default, include_phi=True opt-in
- preview() PNG / array output for 2D and 3D inputs
- report() statistics on synthetic constant + ascending volumes
- CLI dispatch through voxelkit.cli.main for `inspect`, `preview`, `report`
- `--phi` flag prints stderr warning, rejected for non-DICOM
- detect_format directory detection
"""

from __future__ import annotations

import importlib
import io
import json
import sys
import tempfile
from pathlib import Path

import pytest


voxelkit_module = importlib.import_module("voxelkit")
cli_main = importlib.import_module("voxelkit.cli").main
dicom_module = importlib.import_module("voxelkit.dicom")
detect_format = importlib.import_module("voxelkit.core.formats").detect_format

FIXTURES_DIR = Path(__file__).parent / "fixtures"
SINGLE_DCM = FIXTURES_DIR / "sample.dcm"
SERIES_DIR = FIXTURES_DIR / "sample_series"


# ---------------------------------------------------------------------------
# detect_format
# ---------------------------------------------------------------------------


def test_detect_format_recognises_single_dcm() -> None:
    """detect_format() classifies a .dcm extension as 'dicom'."""
    assert detect_format(str(SINGLE_DCM)) == "dicom"


def test_detect_format_recognises_series_directory() -> None:
    """detect_format() peeks inside a directory and returns 'dicom' for a series."""
    assert detect_format(str(SERIES_DIR)) == "dicom"


# ---------------------------------------------------------------------------
# inspect — single file
# ---------------------------------------------------------------------------


def test_dicom_inspect_single_returns_expected_metadata() -> None:
    """inspect() on a single .dcm returns shape/dtype/source/voxel_size."""
    result = dicom_module.inspect(str(SINGLE_DCM))

    assert result["format"] == "dicom"
    assert result["source"] == "file"
    assert result["shape"] == [8, 8]
    assert result["ndim"] == 2
    assert result["dtype"] == "uint16"
    assert result["slice_count"] == 1
    assert result["modality"] == "CT"
    assert result["voxel_size"] == [0.5, 0.5, 1.0]


def test_dicom_inspect_strips_phi_by_default() -> None:
    """inspect() without include_phi must NOT carry patient identifiers."""
    result = dicom_module.inspect(str(SINGLE_DCM))

    for forbidden_key in (
        "patient_name",
        "patient_id",
        "patient_birth_date",
        "patient_sex",
        "accession_number",
        "referring_physician_name",
        "institution_name",
        "study_date",
        "study_time",
    ):
        assert forbidden_key not in result, f"PHI leaked: {forbidden_key}"


def test_dicom_inspect_include_phi_returns_phi_fields() -> None:
    """inspect(include_phi=True) carries the PHI fields populated in the fixture."""
    result = dicom_module.inspect(str(SINGLE_DCM), include_phi=True)

    assert result["patient_name"] == "Test^Patient"
    assert result["patient_id"] == "PID-1234"
    assert result["patient_birth_date"] == "19900101"
    assert result["accession_number"] == "ACC-5678"
    assert result["institution_name"] == "Test Hospital"


# ---------------------------------------------------------------------------
# inspect — series directory
# ---------------------------------------------------------------------------


def test_dicom_inspect_series_returns_3d_shape() -> None:
    """inspect() on a series directory stacks slices into a (Z, H, W) volume."""
    result = dicom_module.inspect(str(SERIES_DIR))

    assert result["source"] == "series"
    assert result["slice_count"] == 4
    assert result["shape"] == [4, 8, 8]
    assert result["ndim"] == 3


def test_dicom_inspect_series_strips_phi_by_default() -> None:
    """Series inspect also defaults to PHI-stripped output."""
    result = dicom_module.inspect(str(SERIES_DIR))
    assert "patient_name" not in result
    assert "patient_id" not in result


# ---------------------------------------------------------------------------
# preview
# ---------------------------------------------------------------------------


def test_dicom_preview_single_returns_png_bytes() -> None:
    """preview() on a 2D .dcm produces a valid PNG."""
    png_bytes = dicom_module.preview(str(SINGLE_DCM))
    assert isinstance(png_bytes, bytes)
    assert png_bytes[:8] == b"\x89PNG\r\n\x1a\n"


def test_dicom_preview_single_as_array_returns_uint8() -> None:
    """preview(as_array=True) returns a 2D uint8 array matching the source shape."""
    array = dicom_module.preview(str(SINGLE_DCM), as_array=True)
    assert array.shape == (8, 8)
    assert str(array.dtype) == "uint8"


def test_dicom_preview_series_default_axis_returns_in_plane_slice() -> None:
    """preview() on a series defaults to axis=0 (axial), centre slice."""
    array = dicom_module.preview(str(SERIES_DIR), as_array=True)
    assert array.shape == (8, 8)
    assert str(array.dtype) == "uint8"


def test_dicom_preview_series_axis_1() -> None:
    """preview() respects axis=1 (coronal) on a series volume."""
    array = dicom_module.preview(str(SERIES_DIR), axis=1, as_array=True)
    # Slicing (4, 8, 8) along axis 1 yields (4, 8).
    assert array.shape == (4, 8)


def test_dicom_preview_series_invalid_axis_raises() -> None:
    """preview() rejects an out-of-range axis."""
    with pytest.raises(Exception):  # noqa: B017 — ValidationError from core
        dicom_module.preview(str(SERIES_DIR), axis=99)


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------


def test_dicom_report_single_emits_constant_warning() -> None:
    """report() on a constant-filled .dcm raises the constant-array warning."""
    result = dicom_module.report(str(SINGLE_DCM))

    assert result["format"] == "dicom"
    assert result["min"] == 100.0
    assert result["max"] == 100.0
    assert any("constant" in message.lower() for message in result["warnings"])


def test_dicom_report_series_has_3d_shape_no_warnings() -> None:
    """report() on the ascending-value series fixture has no warnings."""
    result = dicom_module.report(str(SERIES_DIR))
    assert result["shape"] == [4, 8, 8]
    assert result["ndim"] == 3
    assert result["min"] == 10.0
    assert result["max"] == 13.0
    # Distinct values per slice — no constant/empty/Nan/Inf warnings.
    assert result["warnings"] == []


# ---------------------------------------------------------------------------
# CLI dispatch — inspect / preview / report
# ---------------------------------------------------------------------------


def test_cli_inspect_dicom_strips_phi(capsys: pytest.CaptureFixture[str]) -> None:
    """`voxelkit inspect sample.dcm` prints PHI-stripped JSON to stdout."""
    rc = cli_main(["inspect", str(SINGLE_DCM)])
    assert rc == 0
    out = capsys.readouterr().out
    result = json.loads(out)
    assert "patient_name" not in result
    assert result["format"] == "dicom"


def test_cli_inspect_phi_includes_and_warns(capsys: pytest.CaptureFixture[str]) -> None:
    """`voxelkit inspect sample.dcm --phi` includes PHI AND warns on stderr."""
    rc = cli_main(["inspect", str(SINGLE_DCM), "--phi"])
    assert rc == 0
    captured = capsys.readouterr()
    result = json.loads(captured.out)
    assert result["patient_name"] == "Test^Patient"
    assert "WARNING" in captured.err
    assert "PHI" in captured.err


def test_cli_inspect_phi_rejected_for_non_dicom(capsys: pytest.CaptureFixture[str]) -> None:
    """`--phi` on a non-DICOM input must fail with a clear error."""
    rc = cli_main(["inspect", str(FIXTURES_DIR / "sample_3d.nii.gz"), "--phi"])
    assert rc != 0
    assert "--phi is only valid for DICOM" in capsys.readouterr().err


def test_cli_inspect_series_directory(capsys: pytest.CaptureFixture[str]) -> None:
    """`voxelkit inspect <series_dir>` produces a series-shaped result."""
    rc = cli_main(["inspect", str(SERIES_DIR)])
    assert rc == 0
    result = json.loads(capsys.readouterr().out)
    assert result["source"] == "series"
    assert result["slice_count"] == 4


def test_cli_preview_dicom_writes_png(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`voxelkit preview sample.dcm --output X` writes a valid PNG."""
    out_path = tmp_path / "preview.png"
    rc = cli_main(["preview", str(SINGLE_DCM), "--output", str(out_path)])
    assert rc == 0
    assert out_path.exists()
    assert out_path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_cli_report_dicom_returns_json(capsys: pytest.CaptureFixture[str]) -> None:
    """`voxelkit report sample.dcm` prints a FileReportResult JSON."""
    rc = cli_main(["report", str(SINGLE_DCM)])
    assert rc == 0
    result = json.loads(capsys.readouterr().out)
    assert result["format"] == "dicom"
    assert result["shape"] == [8, 8]


# ---------------------------------------------------------------------------
# Library dispatch — inspect_file / preview_file / report_file
# ---------------------------------------------------------------------------


def test_inspect_file_routes_to_dicom() -> None:
    """voxelkit.inspect_file() dispatches a .dcm input to the DICOM module."""
    result = voxelkit_module.inspect_file(str(SINGLE_DCM))
    assert result["format"] == "dicom"
    assert "patient_name" not in result


def test_inspect_file_include_phi_only_for_dicom() -> None:
    """include_phi=True is rejected for non-DICOM inputs."""
    with pytest.raises(Exception):  # noqa: B017
        voxelkit_module.inspect_file(
            str(FIXTURES_DIR / "sample_3d.nii.gz"), include_phi=True
        )


def test_report_file_routes_to_dicom() -> None:
    """voxelkit.report_file() routes a .dcm to the DICOM report module."""
    result = voxelkit_module.report_file(str(SINGLE_DCM))
    assert result["format"] == "dicom"
    assert any("constant" in message.lower() for message in result["warnings"])


def test_preview_file_routes_to_dicom_series() -> None:
    """voxelkit.preview_file() supports a DICOM series directory."""
    png = voxelkit_module.preview_file(str(SERIES_DIR))
    assert isinstance(png, bytes)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
