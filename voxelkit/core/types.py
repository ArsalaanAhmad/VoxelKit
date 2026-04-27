"""Shared TypedDict definitions for all VoxelKit return types.

Every public function in the library returns one of these typed dicts so that
callers — whether Python scripts, the CLI, or the REST API — can rely on a
stable, documented schema without importing implementation details.
"""

from typing import Literal, TypeAlias, TypedDict


class TiffInspectResult(TypedDict):
    """Metadata returned by `voxelkit.tiff.inspect` for a .tif/.tiff file.

    `page_count` is the raw number of IFD pages in the file (1 for a single
    2D image, N for a Z-stack with N slices). `axes` is tifffile's dimension
    label string, e.g. "ZYX" for a z-stack, "YX" for a 2D image, "YXS" for
    a 2D colour image with a samples axis.
    """

    filename: str
    format: Literal["tiff"]
    shape: list[int]
    ndim: int
    dtype: str
    page_count: int
    axes: str


class GroupInspectItem(TypedDict):
    """A single HDF5 group entry returned within `H5InspectResult.items`."""

    path: str
    type: Literal["group"]


class DatasetInspectItem(TypedDict):
    """A single HDF5 dataset entry returned within `H5InspectResult.items`."""

    path: str
    type: Literal["dataset"]
    shape: list[int]
    dtype: str


InspectItem: TypeAlias = GroupInspectItem | DatasetInspectItem


class H5InspectResult(TypedDict):
    """Metadata returned by `voxelkit.h5.inspect` for a .h5/.hdf5 file.

    `items` is a flat list of every group and dataset found in the file,
    ordered by the depth-first traversal of the HDF5 hierarchy.
    """

    filename: str
    items: list[InspectItem]


class NiftiMetadataResult(TypedDict):
    """Metadata returned by `voxelkit.nifti.inspect` for a .nii/.nii.gz file."""

    filename: str
    shape: list[int]
    ndim: int
    voxel_size: list[float]
    dtype: str


class NpzArrayInspectItem(TypedDict):
    """Per-array entry inside an `NpzInspectResult.arrays` list."""

    name: str
    shape: list[int]
    ndim: int
    dtype: str


class NpyInspectResult(TypedDict):
    """Metadata returned by `voxelkit.npy.inspect` for a .npy file."""

    filename: str
    format: Literal["numpy"]
    shape: list[int]
    ndim: int
    dtype: str


class NpzInspectResult(TypedDict):
    """Metadata returned by `voxelkit.npy.inspect` for a .npz archive.

    Unlike `NpyInspectResult`, an NPZ file may contain multiple named arrays,
    so the result carries a list of per-array descriptors rather than a single
    shape/dtype pair.
    """

    filename: str
    format: Literal["numpy"]
    arrays: list[NpzArrayInspectItem]


class FileReportResult(TypedDict):
    """QA statistics returned by any `report` function across all formats.

    This is the common schema shared by NIfTI, HDF5, NumPy, and TIFF reports.
    `min`, `max`, `mean`, and `std` are `None` when the array is empty or
    contains only non-finite values. `warnings` is an empty list when the
    array passes all quality checks.
    """

    filename: str
    format: str
    shape: list[int]
    ndim: int
    dtype: str
    min: float | None
    max: float | None
    mean: float | None
    std: float | None
    nan_count: int
    inf_count: int
    zero_fraction: float
    warnings: list[str]


class BatchFailureItem(TypedDict):
    """A record of one file that could not be processed during a batch report."""

    file_path: str
    error: str


class BatchFileReportResult(FileReportResult):
    """A single file's QA report augmented with its absolute path.

    Extends `FileReportResult` so callers can correlate stats back to the
    original file when iterating over a batch result.
    """

    file_path: str


class BatchAggregateSummary(TypedDict):
    """Cross-file summary statistics appended to a `BatchReportResult`.

    `count_by_format` maps each format name (e.g. "nifti", "tiff") to the
    number of files of that format in the batch. `warning_counts` maps each
    distinct warning message to how many files produced it.
    """

    count_by_format: dict[str, int]
    unique_shapes: list[str]
    files_with_warnings: int
    warning_counts: dict[str, int]


class BatchReportResult(TypedDict):
    """Top-level result returned by `voxelkit.report_batch`.

    Contains per-file reports, a list of failures, and aggregate statistics
    for the entire scanned directory tree.
    """

    root_path: str
    recursive: bool
    total_files_found: int
    supported_files_found: int
    successful_reports: int
    failed_reports: int
    files: list[BatchFileReportResult]
    failures: list[BatchFailureItem]
    aggregate: BatchAggregateSummary
