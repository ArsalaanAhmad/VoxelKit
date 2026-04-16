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
