import json
import importlib
from pathlib import Path

import h5py
import nibabel as nib
import numpy as np

report_file = importlib.import_module("voxelkit").report_file
cli_main = importlib.import_module("voxelkit.cli").main


FIXTURES_DIR = Path(__file__).parent / "fixtures"
REQUIRED_KEYS = {
    "filename",
    "format",
    "shape",
    "ndim",
    "dtype",
    "min",
    "max",
    "mean",
    "std",
    "nan_count",
    "inf_count",
    "zero_fraction",
    "warnings",
}


def _assert_required_keys(report: dict) -> None:
    assert REQUIRED_KEYS.issubset(report.keys())


def _save_npy(path: Path, data: np.ndarray) -> None:
    np.save(path, data.astype(np.float32, copy=False))


def test_report_nifti_fixture_has_expected_structure() -> None:
    report = report_file(str(FIXTURES_DIR / "sample_3d.nii.gz"))

    _assert_required_keys(report)
    assert report["format"] == "nifti"
    assert report["shape"] == [8, 9, 10]
    assert report["ndim"] == 3


def test_report_h5_explicit_dataset_has_expected_structure() -> None:
    report = report_file(
        str(FIXTURES_DIR / "sample_nested.h5"),
        dataset_path="data/subject01/run1/bold",
    )

    _assert_required_keys(report)
    assert report["format"] == "hdf5"
    assert report["shape"] == [5, 7, 9]
    assert report["ndim"] == 3


def test_report_h5_without_dataset_uses_first_dataset() -> None:
    report = report_file(str(FIXTURES_DIR / "sample_nested.h5"))

    _assert_required_keys(report)
    assert report["shape"] == [5, 7, 9]
    assert any("dataset_path not provided" in warning for warning in report["warnings"])


def test_report_warns_for_constant_data(tmp_path: Path) -> None:
    file_path = tmp_path / "constant.npy"
    _save_npy(file_path, np.full((4, 4), 7.0, dtype=np.float32))

    report = report_file(str(file_path))

    assert report["std"] == 0.0
    assert "Array is constant or nearly constant." in report["warnings"]


def test_report_warns_for_mostly_zero_data(tmp_path: Path) -> None:
    file_path = tmp_path / "mostly_zero.npy"
    data = np.zeros((4, 5), dtype=np.float32)
    data.ravel()[-1] = 1.0  # 19/20 zeros -> threshold boundary (0.95)
    _save_npy(file_path, data)

    report = report_file(str(file_path))

    assert report["zero_fraction"] == 0.95
    assert "Array is mostly zeros." in report["warnings"]


def test_report_warns_for_nan_data(tmp_path: Path) -> None:
    file_path = tmp_path / "with_nan.npy"
    data = np.arange(9, dtype=np.float32).reshape(3, 3)
    data[0, 1] = np.nan
    _save_npy(file_path, data)

    report = report_file(str(file_path))

    assert report["nan_count"] == 1
    assert "Contains NaNs." in report["warnings"]


def test_report_warns_for_inf_data(tmp_path: Path) -> None:
    file_path = tmp_path / "with_inf.npy"
    data = np.arange(9, dtype=np.float32).reshape(3, 3)
    data[2, 2] = np.inf
    _save_npy(file_path, data)

    report = report_file(str(file_path))

    assert report["inf_count"] == 1
    assert "Contains Infs." in report["warnings"]


def test_report_warns_for_nan_and_inf_values(tmp_path: Path) -> None:
    data = np.array([[[0.0, np.nan], [np.inf, 2.0]]], dtype=np.float32)
    image = nib.Nifti1Image(data, affine=np.eye(4, dtype=np.float32))
    file_path = tmp_path / "nan_inf.nii.gz"
    nib.save(image, str(file_path))

    report = report_file(str(file_path))

    assert report["nan_count"] == 1
    assert report["inf_count"] == 1
    assert "Contains NaNs." in report["warnings"]
    assert "Contains Infs." in report["warnings"]


def test_report_warns_for_unsupported_preview_ndim(tmp_path: Path) -> None:
    file_path = tmp_path / "oned.h5"
    with h5py.File(file_path, "w") as h5_file:
        h5_file.create_dataset("signal", data=np.arange(10, dtype=np.float32))

    report = report_file(str(file_path), dataset_path="signal")

    assert report["ndim"] == 1
    assert "Unsupported dimensionality for preview." in report["warnings"]


def test_report_warns_for_unsupported_preview_ndim_4d_numpy(tmp_path: Path) -> None:
    file_path = tmp_path / "four_d.npy"
    _save_npy(file_path, np.arange(2 * 2 * 2 * 2, dtype=np.float32).reshape(2, 2, 2, 2))

    report = report_file(str(file_path))

    assert report["ndim"] == 4
    assert "Unsupported dimensionality for preview." in report["warnings"]


def test_cli_report_prints_json(capsys) -> None:
    exit_code = cli_main(["report", str(FIXTURES_DIR / "sample_2d.h5"), "--dataset", "image"])
    captured = capsys.readouterr()

    assert exit_code == 0
    report = json.loads(captured.out)
    _assert_required_keys(report)
    assert report["format"] == "hdf5"
