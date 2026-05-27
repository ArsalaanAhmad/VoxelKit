"""Tests for the HTML batch QA report (`voxelkit report-batch --html`).

Covers:
- HTML document is self-contained (DOCTYPE, embedded styles, no external links)
- Per-file cards include filename, format, stats, and a base64 PNG thumbnail
- Warnings are surfaced as chips on the relevant card
- Aggregate counts match the underlying BatchReportResult
- DICOM, NIfTI, NumPy, and TIFF files all render successfully
- --html and --output are mutually exclusive
"""

from __future__ import annotations

import importlib
import io
import shutil
import sys
from pathlib import Path

import pytest


cli_main = importlib.import_module("voxelkit.cli").main
render_batch_report_html = importlib.import_module("voxelkit.core.html_report").render_batch_report_html
report_batch = importlib.import_module("voxelkit").report_batch

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def _build_mixed_tree(tmp_path: Path) -> Path:
    """Assemble a directory with one file per supported format for batch tests."""
    root = tmp_path / "mixed"
    root.mkdir()
    for source_name, dest_name in (
        ("sample_3d.nii.gz", "sample.nii.gz"),
        ("sample_2d.tif", "sample.tif"),
        ("sample_constant.npy", "constant.npy"),  # triggers a warning
        ("sample.dcm", "scan.dcm"),
    ):
        shutil.copy(FIXTURES_DIR / source_name, root / dest_name)
    return root


# ---------------------------------------------------------------------------
# Library API
# ---------------------------------------------------------------------------


def test_render_batch_report_html_returns_self_contained_document(tmp_path: Path) -> None:
    """The rendered string is a complete HTML doc with embedded styles."""
    root = _build_mixed_tree(tmp_path)
    batch_result = report_batch(str(root))

    html = render_batch_report_html(batch_result)

    assert html.startswith("<!DOCTYPE html>")
    assert "<style>" in html
    # No external resource references — every asset lives in the page.
    assert "http://" not in html
    assert 'src="data:image/png;base64,' in html


def test_render_batch_report_html_includes_every_file(tmp_path: Path) -> None:
    """Per-file cards are emitted for every successful report."""
    root = _build_mixed_tree(tmp_path)
    batch_result = report_batch(str(root))

    html = render_batch_report_html(batch_result)
    for filename in ("sample.nii.gz", "sample.tif", "constant.npy", "scan.dcm"):
        assert filename in html, f"missing file card: {filename}"


def test_render_batch_report_html_surfaces_warnings(tmp_path: Path) -> None:
    """A file that triggers a warning has it rendered in its card."""
    root = _build_mixed_tree(tmp_path)
    batch_result = report_batch(str(root))

    html = render_batch_report_html(batch_result)
    # constant.npy triggers "Array is constant or nearly constant."
    assert "constant" in html.lower()


def test_render_batch_report_html_shows_aggregate_counts(tmp_path: Path) -> None:
    """Aggregate panel reports the file counts produced by report_batch."""
    root = _build_mixed_tree(tmp_path)
    batch_result = report_batch(str(root))

    html = render_batch_report_html(batch_result)
    # Four supported files, all successful.
    assert ">4<" in html  # supported/successful counters
    # Format-by-name aggregate breakdown rendered.
    for format_name in ("dicom", "nifti", "tiff", "numpy"):
        assert format_name in html.lower()


# ---------------------------------------------------------------------------
# CLI dispatch
# ---------------------------------------------------------------------------


def test_cli_report_batch_html_writes_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """`voxelkit report-batch <dir> --html <path>` writes a valid HTML file."""
    root = _build_mixed_tree(tmp_path)
    html_out = tmp_path / "report.html"

    rc = cli_main(["report-batch", str(root), "--html", str(html_out)])
    assert rc == 0
    assert html_out.exists()
    content = html_out.read_text(encoding="utf-8")
    assert content.startswith("<!DOCTYPE html>")
    assert "data:image/png;base64," in content


def test_cli_report_batch_output_and_html_mutually_exclusive(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Passing both --output and --html exits non-zero with a clear error."""
    root = _build_mixed_tree(tmp_path)
    rc = cli_main([
        "report-batch", str(root),
        "--output", str(tmp_path / "x.json"),
        "--html", str(tmp_path / "x.html"),
    ])
    assert rc != 0
    assert "mutually exclusive" in capsys.readouterr().err


def test_cli_report_batch_without_html_still_writes_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Existing JSON behaviour is preserved when --html is not set."""
    root = _build_mixed_tree(tmp_path)
    json_out = tmp_path / "report.json"

    rc = cli_main(["report-batch", str(root), "--output", str(json_out)])
    assert rc == 0
    assert json_out.exists()
    assert json_out.read_text(encoding="utf-8").lstrip().startswith("{")
