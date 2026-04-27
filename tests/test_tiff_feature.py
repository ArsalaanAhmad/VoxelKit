"""Tests for TIFF inspect, preview, and report functions.

Covers:
- 2D single-page TIFF (grayscale, float32)
- 3D multi-page TIFF (z-stack, float32)
- CLI routing for inspect, preview, and report commands
- Error cases for unsupported operations
"""

import importlib
import json
import tempfile
from pathlib import Path

import pytest


voxelkit_module = importlib.import_module("voxelkit")
cli_main = importlib.import_module("voxelkit.cli").main
preview_tiff = importlib.import_module("voxelkit.tiff").preview

FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# inspect
# ---------------------------------------------------------------------------


def test_tiff_2d_inspect_has_expected_metadata() -> None:
    """inspect() on a 2D TIFF returns correct shape, ndim, dtype, and axes."""
    result = voxelkit_module.inspect_file(str(FIXTURES_DIR / "sample_2d.tif"))

    assert result["format"] == "tiff"
    assert result["shape"] == [12, 16]
    assert result["ndim"] == 2
    assert result["dtype"] == "float32"
    assert result["page_count"] == 1
    # tifffile labels a 2D single-page image as "YX"
    assert result["axes"] == "YX"


def test_tiff_3d_inspect_has_expected_metadata() -> None:
    """inspect() on a 3D z-stack TIFF returns shape (Z, H, W) and page_count == Z."""
    result = voxelkit_module.inspect_file(str(FIXTURES_DIR / "sample_3d.tif"))

    assert result["format"] == "tiff"
    assert result["shape"] == [6, 8, 10]
    assert result["ndim"] == 3
    assert result["dtype"] == "float32"
    # Each Z-slice is stored as one IFD page, so page_count == Z dimension.
    assert result["page_count"] == 6


# ---------------------------------------------------------------------------
# preview
# ---------------------------------------------------------------------------


def test_tiff_2d_preview_returns_uint8_array() -> None:
    """preview() on a 2D TIFF returns a uint8 array with the same spatial shape."""
    array = preview_tiff(str(FIXTURES_DIR / "sample_2d.tif"), as_array=True)

    assert array.shape == (12, 16)
    assert str(array.dtype) == "uint8"


def test_tiff_2d_preview_returns_png_bytes() -> None:
    """preview() without as_array returns non-empty PNG bytes."""
    png_bytes = preview_tiff(str(FIXTURES_DIR / "sample_2d.tif"))

    # PNG files always begin with the 8-byte PNG signature.
    assert isinstance(png_bytes, bytes)
    assert png_bytes[:8] == b"\x89PNG\r\n\x1a\n"


def test_tiff_3d_preview_default_axis_returns_uint8_array() -> None:
    """preview() on a 3D z-stack slices along axis 0 by default and returns uint8."""
    array = preview_tiff(str(FIXTURES_DIR / "sample_3d.tif"), as_array=True)

    # Slicing a (6, 8, 10) array along axis 0 yields a (8, 10) plane.
    assert array.shape == (8, 10)
    assert str(array.dtype) == "uint8"


def test_tiff_3d_preview_explicit_slice_index() -> None:
    """preview() respects an explicit slice_index for 3D z-stacks."""
    array = preview_tiff(
        str(FIXTURES_DIR / "sample_3d.tif"),
        axis=0,
        slice_index=2,
        as_array=True,
    )

    assert array.shape == (8, 10)
    assert str(array.dtype) == "uint8"


def test_tiff_3d_preview_axis_1() -> None:
    """preview() can slice along axis 1 (Y) of a 3D z-stack."""
    array = preview_tiff(
        str(FIXTURES_DIR / "sample_3d.tif"),
        axis=1,
        as_array=True,
    )

    # Slicing a (6, 8, 10) array along axis 1 yields a (6, 10) plane.
    assert array.shape == (6, 10)


# ---------------------------------------------------------------------------
# report
# ---------------------------------------------------------------------------


def test_tiff_2d_report_has_expected_structure() -> None:
    """report() on a 2D TIFF returns all required FileReportResult keys."""
    result = voxelkit_module.report_file(str(FIXTURES_DIR / "sample_2d.tif"))

    assert result["format"] == "tiff"
    assert result["shape"] == [12, 16]
    assert result["ndim"] == 2
    assert "warnings" in result
    assert isinstance(result["warnings"], list)


def test_tiff_3d_report_has_expected_structure() -> None:
    """report() on a 3D z-stack TIFF reports correct shape and statistics."""
    result = voxelkit_module.report_file(str(FIXTURES_DIR / "sample_3d.tif"))

    assert result["format"] == "tiff"
    assert result["shape"] == [6, 8, 10]
    assert result["ndim"] == 3
    assert result["nan_count"] == 0
    assert result["inf_count"] == 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def test_cli_inspect_tiff_prints_json(capsys) -> None:
    """CLI inspect command routes to TIFF and prints valid JSON metadata."""
    exit_code = cli_main(["inspect", str(FIXTURES_DIR / "sample_2d.tif")])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["format"] == "tiff"
    assert payload["shape"] == [12, 16]


def test_cli_report_tiff_prints_json(capsys) -> None:
    """CLI report command routes to TIFF and prints valid JSON QA stats."""
    exit_code = cli_main(["report", str(FIXTURES_DIR / "sample_2d.tif")])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["format"] == "tiff"


def test_cli_preview_tiff_writes_png() -> None:
    """CLI preview command routes to TIFF and writes a valid PNG file."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        output_path = tmp.name

    exit_code = cli_main([
        "preview",
        str(FIXTURES_DIR / "sample_2d.tif"),
        "--output", output_path,
    ])

    assert exit_code == 0
    with open(output_path, "rb") as f:
        header = f.read(8)
    assert header == b"\x89PNG\r\n\x1a\n"


def test_cli_preview_tiff_3d_with_slice(capsys) -> None:
    """CLI preview command accepts --axis and --slice for 3D z-stack TIFFs."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        output_path = tmp.name

    exit_code = cli_main([
        "preview",
        str(FIXTURES_DIR / "sample_3d.tif"),
        "--axis", "0",
        "--slice", "3",
        "--output", output_path,
    ])

    assert exit_code == 0


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_tiff_report_rejects_dataset_path() -> None:
    """report_file() raises ValidationError when dataset_path is passed for TIFF."""
    with pytest.raises(ValueError, match="dataset_path is only valid for HDF5"):
        voxelkit_module.report_file(
            str(FIXTURES_DIR / "sample_2d.tif"),
            dataset_path="some/path",
        )


def test_tiff_report_rejects_array_name() -> None:
    """report_file() raises ValidationError when array_name is passed for TIFF."""
    with pytest.raises(ValueError, match="array_name is only valid for NumPy"):
        voxelkit_module.report_file(
            str(FIXTURES_DIR / "sample_2d.tif"),
            array_name="arr",
        )
