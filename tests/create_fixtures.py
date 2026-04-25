from pathlib import Path

import h5py
import nibabel as nib
import numpy as np


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def create_sample_nifti() -> None:
    data = np.arange(8 * 9 * 10, dtype=np.float32).reshape(8, 9, 10)
    image = nib.Nifti1Image(data, affine=np.eye(4, dtype=np.float32))
    nib.save(image, str(FIXTURES_DIR / "sample_3d.nii.gz"))


def create_sample_h5_2d() -> None:
    with h5py.File(FIXTURES_DIR / "sample_2d.h5", "w") as h5_file:
        data_2d = np.arange(12 * 16, dtype=np.float32).reshape(12, 16)
        h5_file.create_dataset("image", data=data_2d)


def create_sample_h5_3d() -> None:
    with h5py.File(FIXTURES_DIR / "sample_3d.h5", "w") as h5_file:
        data_3d = np.arange(6 * 8 * 10, dtype=np.float32).reshape(6, 8, 10)
        h5_file.create_dataset("volume", data=data_3d)


def create_sample_h5_nested() -> None:
    with h5py.File(FIXTURES_DIR / "sample_nested.h5", "w") as h5_file:
        group = h5_file.create_group("data")
        subject = group.create_group("subject01")
        run = subject.create_group("run1")
        bold = np.arange(5 * 7 * 9, dtype=np.float32).reshape(5, 7, 9)
        run.create_dataset("bold", data=bold)


def create_sample_npy_2d() -> None:
    data_2d = np.arange(10 * 14, dtype=np.float32).reshape(10, 14)
    np.save(FIXTURES_DIR / "sample_2d.npy", data_2d)


def create_sample_npz_multi() -> None:
    features = np.arange(4 * 6 * 8, dtype=np.float32).reshape(4, 6, 8)
    labels = np.arange(12, dtype=np.int16)
    np.savez(FIXTURES_DIR / "sample_multi.npz", features=features, labels=labels)


def main() -> None:
    FIXTURES_DIR.mkdir(parents=True, exist_ok=True)

    create_sample_nifti()
    create_sample_h5_2d()
    create_sample_h5_3d()
    create_sample_h5_nested()
    create_sample_npy_2d()
    create_sample_npz_multi()

    print("Fixtures created in tests/fixtures:")
    print("- sample_3d.nii.gz: tiny 3D NIfTI volume for /nifti endpoints")
    print("- sample_2d.h5: 2D dataset 'image' for /h5/slice 2D behavior")
    print("- sample_3d.h5: 3D dataset 'volume' for /h5/slice 3D slicing")
    print("- sample_nested.h5: nested dataset data/subject01/run1/bold for /h5/inspect and /h5/slice")
    print("- sample_2d.npy: 2D NumPy array for inspect/report/preview")
    print("- sample_multi.npz: NPZ with arrays 'features' and 'labels' for array selection")


if __name__ == "__main__":
    main()
