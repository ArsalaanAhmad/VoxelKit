"""Tests for voxelkit.embedding report and preview functions.

Covers:
- Clean embedding: correct shape/dim metadata, zero anomaly counts
- Dead dimensions: detected and warned
- Outlier samples: detected and warned
- NaN dimensions: detected and warned
- Preview: correct output shape and PNG encoding
- CLI: embed-report and embed-preview subcommands
- Error cases: wrong ndim, wrong extension
"""

import importlib
import json
import tempfile
from pathlib import Path

import numpy as np
import pytest


cli_main = importlib.import_module("voxelkit.cli").main
embedding_module = importlib.import_module("voxelkit.embedding")

FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# report — clean embedding
# ---------------------------------------------------------------------------


def test_embedding_report_clean_has_correct_dimensions() -> None:
    """report() on a clean (64, 128) matrix returns correct n_samples and n_dims."""
    result = embedding_module.report(str(FIXTURES_DIR / "sample_embedding.npy"))

    assert result["n_samples"] == 64
    assert result["n_dims"] == 128
    assert result["dtype"] == "float32"
    assert result["format"] == "numpy"


def test_embedding_report_clean_has_no_anomalies() -> None:
    """report() on a clean matrix produces zero structural anomaly counts.

    Note: outlier_sample_count may be non-zero for a random normal distribution
    — a few samples exceeding 3σ in norm is statistically expected and is not
    a bug. We only assert on counts that must be exactly zero for clean data.
    """
    result = embedding_module.report(str(FIXTURES_DIR / "sample_embedding.npy"))

    assert result["total_nan_count"] == 0
    assert result["total_inf_count"] == 0
    assert result["dead_dim_count"] == 0
    assert result["nan_dim_count"] == 0
    assert result["inf_dim_count"] == 0


def test_embedding_report_clean_has_finite_norm_stats() -> None:
    """report() on a clean matrix reports finite norm_mean and norm_std."""
    result = embedding_module.report(str(FIXTURES_DIR / "sample_embedding.npy"))

    assert result["norm_mean"] is not None
    assert result["norm_std"] is not None
    assert result["norm_mean"] > 0


# ---------------------------------------------------------------------------
# report — dead dimensions
# ---------------------------------------------------------------------------


def test_embedding_report_detects_dead_dims() -> None:
    """report() detects the 4 zeroed-out dead dimensions in the fixture."""
    result = embedding_module.report(str(FIXTURES_DIR / "sample_embedding_dead_dims.npy"))

    assert result["dead_dim_count"] == 4


def test_embedding_report_warns_on_dead_dims() -> None:
    """report() emits a warning when a significant fraction of dims are dead."""
    result = embedding_module.report(str(FIXTURES_DIR / "sample_embedding_dead_dims.npy"))

    # 4/32 = 12.5% dead dims, above the 5% threshold — should warn.
    assert any("dead" in w.lower() for w in result["warnings"])


# ---------------------------------------------------------------------------
# report — outlier samples
# ---------------------------------------------------------------------------


def test_embedding_report_detects_outlier_samples() -> None:
    """report() detects the 2 injected outlier samples (norm >> mean)."""
    result = embedding_module.report(str(FIXTURES_DIR / "sample_embedding_outliers.npy"))

    assert result["outlier_sample_count"] == 2


def test_embedding_report_warns_on_outliers() -> None:
    """report() emits a warning when outlier samples are present."""
    result = embedding_module.report(str(FIXTURES_DIR / "sample_embedding_outliers.npy"))

    assert any("outlier" in w.lower() or "anomalous" in w.lower() for w in result["warnings"])


# ---------------------------------------------------------------------------
# report — NaN dimensions
# ---------------------------------------------------------------------------


def test_embedding_report_detects_nan_dims() -> None:
    """report() detects the 2 NaN-filled dimensions in the fixture."""
    result = embedding_module.report(str(FIXTURES_DIR / "sample_embedding_nan_dims.npy"))

    assert result["nan_dim_count"] == 2
    assert result["total_nan_count"] > 0


def test_embedding_report_warns_on_nan_dims() -> None:
    """report() emits a NaN-specific dimension warning."""
    result = embedding_module.report(str(FIXTURES_DIR / "sample_embedding_nan_dims.npy"))

    assert any("nan" in w.lower() for w in result["warnings"])


# ---------------------------------------------------------------------------
# preview
# ---------------------------------------------------------------------------


def test_embedding_preview_returns_png_bytes() -> None:
    """preview() returns valid PNG bytes for a clean embedding."""
    png_bytes = embedding_module.preview(str(FIXTURES_DIR / "sample_embedding.npy"))

    assert isinstance(png_bytes, bytes)
    assert png_bytes[:8] == b"\x89PNG\r\n\x1a\n"


def test_embedding_preview_as_array_returns_uint8() -> None:
    """preview() with as_array=True returns a uint8 array shaped (samples, dims)."""
    array = embedding_module.preview(
        str(FIXTURES_DIR / "sample_embedding.npy"),
        as_array=True,
    )

    assert isinstance(array, np.ndarray)
    assert array.shape == (64, 128)
    assert str(array.dtype) == "uint8"


def test_embedding_preview_subsamples_large_matrix() -> None:
    """preview() subsamples to max_samples rows when N > max_samples."""
    array = embedding_module.preview(
        str(FIXTURES_DIR / "sample_embedding.npy"),
        max_samples=16,
        as_array=True,
    )

    # 64 samples in fixture, max_samples=16 → output has 16 rows.
    assert array.shape[0] == 16
    assert array.shape[1] == 128


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def test_cli_embed_report_prints_json(capsys) -> None:
    """CLI embed-report command prints valid embedding QA JSON."""
    exit_code = cli_main(["embed-report", str(FIXTURES_DIR / "sample_embedding.npy")])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["n_samples"] == 64
    assert payload["n_dims"] == 128


def test_cli_embed_report_detects_dead_dims(capsys) -> None:
    """CLI embed-report reports dead_dim_count > 0 for the dead-dims fixture."""
    exit_code = cli_main([
        "embed-report",
        str(FIXTURES_DIR / "sample_embedding_dead_dims.npy"),
    ])
    captured = capsys.readouterr()

    assert exit_code == 0
    payload = json.loads(captured.out)
    assert payload["dead_dim_count"] == 4


def test_cli_embed_preview_writes_png() -> None:
    """CLI embed-preview writes a valid PNG heatmap to disk."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        output_path = tmp.name

    exit_code = cli_main([
        "embed-preview",
        str(FIXTURES_DIR / "sample_embedding.npy"),
        "--output", output_path,
        "--max-samples", "32",
    ])

    assert exit_code == 0
    with open(output_path, "rb") as f:
        header = f.read(8)
    assert header == b"\x89PNG\r\n\x1a\n"


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_embedding_report_rejects_non_npy(tmp_path) -> None:
    """report() raises an error for non-.npy file extensions."""
    fake = tmp_path / "embeddings.npz"
    fake.write_bytes(b"")
    with pytest.raises(ValueError):
        embedding_module.report(str(fake))


def test_embedding_report_rejects_3d_array(tmp_path) -> None:
    """report() raises ValidationError for a 3D array (wrong shape for embeddings)."""
    path = tmp_path / "bad.npy"
    np.save(str(path), np.zeros((4, 8, 16), dtype=np.float32))
    with pytest.raises(ValueError, match="2D array"):
        embedding_module.report(str(path))
