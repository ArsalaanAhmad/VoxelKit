import importlib
import json
from pathlib import Path

import pytest


voxelkit_module = importlib.import_module("voxelkit")
cli_main = importlib.import_module("voxelkit.cli").main
preview_npy = importlib.import_module("voxelkit.npy").preview


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_npy_inspect_has_expected_shape_and_dtype() -> None:
    result = voxelkit_module.inspect_file(str(FIXTURES_DIR / "sample_2d.npy"))

    assert result["format"] == "numpy"
    assert result["shape"] == [10, 14]
    assert result["ndim"] == 2
    assert result["dtype"] == "float32"


def test_npy_report_has_expected_structure() -> None:
    result = voxelkit_module.report_file(str(FIXTURES_DIR / "sample_2d.npy"))

    assert result["format"] == "numpy"
    assert result["shape"] == [10, 14]
    assert result["ndim"] == 2
    assert "warnings" in result


def test_npy_preview_returns_2d_uint8_array() -> None:
    preview_array = preview_npy(str(FIXTURES_DIR / "sample_2d.npy"), as_array=True)

    assert preview_array.shape == (10, 14)
    assert str(preview_array.dtype) == "uint8"


def test_npz_inspect_lists_named_arrays() -> None:
    result = voxelkit_module.inspect_file(str(FIXTURES_DIR / "sample_multi.npz"))

    names = {item["name"] for item in result["arrays"]}
    assert result["format"] == "numpy"
    assert names == {"features", "labels"}


def test_npz_report_with_array_name_succeeds() -> None:
    result = voxelkit_module.report_file(
        str(FIXTURES_DIR / "sample_multi.npz"),
        array_name="features",
    )

    assert result["format"] == "numpy"
    assert result["shape"] == [4, 6, 8]
    assert result["ndim"] == 3


def test_npz_report_without_array_name_fails_for_multi_array_archive() -> None:
    with pytest.raises(ValueError, match="array_name is required"):
        voxelkit_module.report_file(str(FIXTURES_DIR / "sample_multi.npz"))


def test_cli_report_npz_with_array_prints_json(capsys) -> None:
    exit_code = cli_main([
        "report",
        str(FIXTURES_DIR / "sample_multi.npz"),
        "--array",
        "features",
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["format"] == "numpy"
    assert payload["shape"] == [4, 6, 8]
