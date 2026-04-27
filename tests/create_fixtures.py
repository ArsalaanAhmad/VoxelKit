"""Generate test fixture files used by the VoxelKit test suite.

Run this script once before running tests to populate the tests/fixtures/
directory. Every fixture is a minimal synthetic array — just large enough to
exercise the code paths being tested, small enough to stay fast.

Usage:
    python tests/create_fixtures.py
"""

from pathlib import Path

import h5py
import nibabel as nib
import numpy as np
import tifffile


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def create_sample_nifti() -> None:
    """Create a small 3D NIfTI volume for NIfTI inspect/preview/report tests."""
    data = np.arange(8 * 9 * 10, dtype=np.float32).reshape(8, 9, 10)
    image = nib.Nifti1Image(data, affine=np.eye(4, dtype=np.float32))
    nib.save(image, str(FIXTURES_DIR / "sample_3d.nii.gz"))


def create_sample_h5_2d() -> None:
    """Create an HDF5 file with a single 2D dataset for 2D slice preview tests."""
    with h5py.File(FIXTURES_DIR / "sample_2d.h5", "w") as h5_file:
        data_2d = np.arange(12 * 16, dtype=np.float32).reshape(12, 16)
        h5_file.create_dataset("image", data=data_2d)


def create_sample_h5_3d() -> None:
    """Create an HDF5 file with a single 3D dataset for axis-slicing preview tests."""
    with h5py.File(FIXTURES_DIR / "sample_3d.h5", "w") as h5_file:
        data_3d = np.arange(6 * 8 * 10, dtype=np.float32).reshape(6, 8, 10)
        h5_file.create_dataset("volume", data=data_3d)


def create_sample_h5_nested() -> None:
    """Create an HDF5 file with a nested group hierarchy for inspect and preview tests."""
    with h5py.File(FIXTURES_DIR / "sample_nested.h5", "w") as h5_file:
        group = h5_file.create_group("data")
        subject = group.create_group("subject01")
        run = subject.create_group("run1")
        bold = np.arange(5 * 7 * 9, dtype=np.float32).reshape(5, 7, 9)
        run.create_dataset("bold", data=bold)


def create_sample_npy_2d() -> None:
    """Create a 2D NumPy .npy file for inspect/preview/report tests."""
    data_2d = np.arange(10 * 14, dtype=np.float32).reshape(10, 14)
    np.save(FIXTURES_DIR / "sample_2d.npy", data_2d)


def create_sample_npz_multi() -> None:
    """Create a multi-array .npz archive for array-selection tests."""
    features = np.arange(4 * 6 * 8, dtype=np.float32).reshape(4, 6, 8)
    labels = np.arange(12, dtype=np.int16)
    np.savez(FIXTURES_DIR / "sample_multi.npz", features=features, labels=labels)


def create_sample_tiff_2d() -> None:
    """Create a single-page 2D grayscale TIFF for TIFF inspect/preview/report tests."""
    data_2d = np.arange(12 * 16, dtype=np.float32).reshape(12, 16)
    tifffile.imwrite(str(FIXTURES_DIR / "sample_2d.tif"), data_2d)


def create_sample_tiff_3d() -> None:
    """Create a multi-page 3D TIFF (z-stack) for TIFF 3D slice preview tests.

    tifffile writes a 3D array (Z, H, W) as a multi-page TIFF where each
    page corresponds to one Z-slice. This is the standard format for
    microscopy z-stacks.
    """
    data_3d = np.arange(6 * 8 * 10, dtype=np.float32).reshape(6, 8, 10)
    tifffile.imwrite(str(FIXTURES_DIR / "sample_3d.tif"), data_3d)


def create_sample_embedding() -> None:
    """Create a clean (N_samples, D_dims) embedding fixture with no anomalies."""
    rng = np.random.default_rng(42)
    embeddings = rng.standard_normal((64, 128)).astype(np.float32)
    np.save(FIXTURES_DIR / "sample_embedding.npy", embeddings)


def create_embedding_with_dead_dims() -> None:
    """Create an embedding where 4 dimensions are constant (dead).

    Dead dimensions have std=0 across all samples and should trigger a warning
    in the embedding report.
    """
    rng = np.random.default_rng(0)
    embeddings = rng.standard_normal((64, 32)).astype(np.float32)
    # Zero out 4 columns entirely to create dead dimensions.
    embeddings[:, [0, 5, 10, 15]] = 0.0
    np.save(FIXTURES_DIR / "sample_embedding_dead_dims.npy", embeddings)


def create_embedding_with_outliers() -> None:
    """Create an embedding where 2 samples have anomalously large L2 norms.

    These outlier rows should be detected by the per-sample norm analysis in
    the embedding report.
    """
    rng = np.random.default_rng(1)
    embeddings = rng.standard_normal((64, 32)).astype(np.float32)
    # Inject two outlier samples with very large values.
    embeddings[0, :] = 100.0
    embeddings[1, :] = -100.0
    np.save(FIXTURES_DIR / "sample_embedding_outliers.npy", embeddings)


def create_embedding_with_nan_dims() -> None:
    """Create an embedding where 2 dimensions contain NaN values."""
    rng = np.random.default_rng(2)
    embeddings = rng.standard_normal((32, 16)).astype(np.float32)
    embeddings[:, 3] = np.nan
    embeddings[:, 7] = np.nan
    np.save(FIXTURES_DIR / "sample_embedding_nan_dims.npy", embeddings)


def create_warning_fixtures() -> None:
    """Create NumPy .npy fixtures that trigger specific QA report warnings.

    These files test that build_array_report emits the expected warning
    messages for pathological array values (constants, NaN, Inf, etc.).
    """
    constant = np.full((4, 4), 7.0, dtype=np.float32)

    mostly_zero = np.zeros((4, 5), dtype=np.float32)
    mostly_zero.ravel()[-1] = 1.0  # 19/20 zeros -> zero_fraction = 0.95

    with_nan = np.arange(9, dtype=np.float32).reshape(3, 3)
    with_nan[0, 1] = np.nan

    with_inf = np.arange(9, dtype=np.float32).reshape(3, 3)
    with_inf[2, 2] = np.inf

    unsupported_ndim = np.arange(2 * 2 * 2 * 2, dtype=np.float32).reshape(2, 2, 2, 2)

    np.save(FIXTURES_DIR / "sample_constant.npy", constant)
    np.save(FIXTURES_DIR / "sample_mostly_zero.npy", mostly_zero)
    np.save(FIXTURES_DIR / "sample_with_nan.npy", with_nan)
    np.save(FIXTURES_DIR / "sample_with_inf.npy", with_inf)
    np.save(FIXTURES_DIR / "sample_4d.npy", unsupported_ndim)


def main() -> None:
    """Create all fixture files under tests/fixtures/."""
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    create_sample_nifti()
    create_sample_h5_2d()
    create_sample_h5_3d()
    create_sample_h5_nested()
    create_sample_npy_2d()
    create_sample_npz_multi()
    create_sample_tiff_2d()
    create_sample_tiff_3d()
    create_sample_embedding()
    create_embedding_with_dead_dims()
    create_embedding_with_outliers()
    create_embedding_with_nan_dims()
    create_warning_fixtures()

    print("Fixtures created in tests/fixtures:")
    print("- sample_3d.nii.gz   : tiny 3D NIfTI volume")
    print("- sample_2d.h5       : 2D dataset 'image'")
    print("- sample_3d.h5       : 3D dataset 'volume'")
    print("- sample_nested.h5   : nested dataset data/subject01/run1/bold")
    print("- sample_2d.npy      : 2D NumPy array (10x14, float32)")
    print("- sample_multi.npz   : NPZ with arrays 'features' and 'labels'")
    print("- sample_2d.tif      : single-page 2D grayscale TIFF (12x16, float32)")
    print("- sample_3d.tif      : multi-page 3D z-stack TIFF (6x8x10, float32)")
    print("- sample_constant.npy: constant values for report warning assertions")
    print("- sample_mostly_zero.npy: mostly zero values for zero-fraction warning")
    print("- sample_with_nan.npy: includes a NaN value for NaN warning")
    print("- sample_with_inf.npy: includes an Inf value for Inf warning")
    print("- sample_4d.npy      : 4D array for unsupported preview dimensionality warning")
    print("- sample_embedding.npy           : clean (64, 128) float32 embedding matrix")
    print("- sample_embedding_dead_dims.npy : embedding with 4 dead (constant) dimensions")
    print("- sample_embedding_outliers.npy  : embedding with 2 outlier samples (norm >> mean)")
    print("- sample_embedding_nan_dims.npy  : embedding with 2 NaN-filled dimensions")


if __name__ == "__main__":
    main()
