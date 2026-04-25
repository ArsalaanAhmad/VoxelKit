from typing import Literal, TypeAlias, TypedDict


class GroupInspectItem(TypedDict):
    path: str
    type: Literal["group"]


class DatasetInspectItem(TypedDict):
    path: str
    type: Literal["dataset"]
    shape: list[int]
    dtype: str


InspectItem: TypeAlias = GroupInspectItem | DatasetInspectItem


class H5InspectResult(TypedDict):
    filename: str
    items: list[InspectItem]


class NiftiMetadataResult(TypedDict):
    filename: str
    shape: list[int]
    ndim: int
    voxel_size: list[float]
    dtype: str


class NpzArrayInspectItem(TypedDict):
    name: str
    shape: list[int]
    ndim: int
    dtype: str


class NpyInspectResult(TypedDict):
    filename: str
    format: Literal["numpy"]
    shape: list[int]
    ndim: int
    dtype: str


class NpzInspectResult(TypedDict):
    filename: str
    format: Literal["numpy"]
    arrays: list[NpzArrayInspectItem]


class FileReportResult(TypedDict):
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
    file_path: str
    error: str


class BatchFileReportResult(FileReportResult):
    file_path: str


class BatchAggregateSummary(TypedDict):
    count_by_format: dict[str, int]
    unique_shapes: list[str]
    files_with_warnings: int
    warning_counts: dict[str, int]


class BatchReportResult(TypedDict):
    root_path: str
    recursive: bool
    total_files_found: int
    supported_files_found: int
    successful_reports: int
    failed_reports: int
    files: list[BatchFileReportResult]
    failures: list[BatchFailureItem]
    aggregate: BatchAggregateSummary
