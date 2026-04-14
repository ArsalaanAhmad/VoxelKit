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
