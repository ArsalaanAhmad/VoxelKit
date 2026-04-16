import json
import importlib
from pathlib import Path

import h5py
import nibabel as nib
import numpy as np

report_batch = importlib.import_module("voxelkit").report_batch
cli_main = importlib.import_module("voxelkit.cli").main


def _create_nifti(path: Path, shape: tuple[int, ...]) -> None:
    data = np.arange(np.prod(shape), dtype=np.float32).reshape(shape)
    image = nib.Nifti1Image(data, affine=np.eye(4, dtype=np.float32))
    nib.save(image, str(path))


def _create_h5(path: Path, dataset_path: str, shape: tuple[int, ...]) -> None:
    data = np.arange(np.prod(shape), dtype=np.float32).reshape(shape)
    with h5py.File(path, "w") as h5_file:
        h5_file.create_dataset(dataset_path, data=data)


def test_report_batch_recursive_collects_reports_and_failures(tmp_path: Path) -> None:
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()

    _create_nifti(tmp_path / "scan.nii.gz", (4, 5, 6))
    _create_h5(tmp_path / "image.h5", "image", (8, 8))
    _create_h5(nested_dir / "volume.hdf5", "volume", (3, 4, 5))
    (nested_dir / "broken.h5").write_bytes(b"not-hdf5")
    (tmp_path / "notes.txt").write_text("ignore", encoding="utf-8")

    result = report_batch(str(tmp_path), recursive=True)

    assert result["root_path"] == str(tmp_path.resolve())
    assert result["recursive"] is True
    assert result["total_files_found"] == 5
    assert result["supported_files_found"] == 4
    assert result["successful_reports"] == 3
    assert result["failed_reports"] == 1
    assert len(result["files"]) == 3
    assert len(result["failures"]) == 1

    aggregate = result["aggregate"]
    assert aggregate["count_by_format"] == {"hdf5": 2, "nifti": 1}
    assert "8x8" in aggregate["unique_shapes"]
    assert "4x5x6" in aggregate["unique_shapes"]
    assert "3x4x5" in aggregate["unique_shapes"]
    assert aggregate["files_with_warnings"] == 2
    assert aggregate["warning_counts"]["dataset_path not provided; using first dataset 'image'."] == 1
    assert aggregate["warning_counts"]["dataset_path not provided; using first dataset 'volume'."] == 1


def test_report_batch_non_recursive_only_scans_top_level(tmp_path: Path) -> None:
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()

    _create_nifti(tmp_path / "top.nii.gz", (2, 3, 4))
    _create_h5(nested_dir / "nested.h5", "image", (6, 6))

    result = report_batch(str(tmp_path), recursive=False)

    assert result["recursive"] is False
    assert result["total_files_found"] == 1
    assert result["supported_files_found"] == 1
    assert result["successful_reports"] == 1
    assert result["failed_reports"] == 0


def test_cli_report_batch_prints_json(capsys, tmp_path: Path) -> None:
    _create_nifti(tmp_path / "scan.nii", (3, 3, 3))

    exit_code = cli_main(["report-batch", str(tmp_path), "--no-recursive"])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["successful_reports"] == 1
    assert payload["supported_files_found"] == 1


def test_cli_report_batch_writes_output_file(tmp_path: Path, capsys) -> None:
    _create_h5(tmp_path / "scan.h5", "image", (5, 5))
    output_path = tmp_path / "batch_report.json"

    exit_code = cli_main([
        "report-batch",
        str(tmp_path),
        "--no-recursive",
        "--output",
        str(output_path),
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    assert output_path.exists()
    assert "Wrote batch report JSON" in captured.out
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["successful_reports"] == 1
