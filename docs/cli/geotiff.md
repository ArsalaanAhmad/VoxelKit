---
description: GeoTIFF support in VoxelKit — inspect and report on georeferenced raster files.
---

# GeoTIFF Support

VoxelKit automatically detects GeoTIFF files and enriches `inspect` output with geospatial metadata when [`rasterio`](https://rasterio.readthedocs.io/) is installed. No extra commands — the same `voxelkit inspect` and `voxelkit report` work transparently.

---

## Install

```bash
pip install voxelkit[geo]
```

This adds `rasterio` as a dependency. Without it, `.tif`/`.tiff` files are still fully supported — you just won't get the geo fields.

---

## Usage

```bash
voxelkit inspect scene.tif
voxelkit report scene.tif
```

When rasterio is installed and the file carries a CRS, inspect adds these fields:

| Field | Description |
|---|---|
| `is_geotiff` | `true` when geo metadata was found |
| `crs` | Coordinate reference system string, e.g. `"EPSG:4326"` |
| `bounds` | `[left, bottom, right, top]` in the CRS unit |
| `resolution` | `[x_res, y_res]` — pixel size in the CRS unit |
| `band_count` | Number of raster bands |

---

## Example output

```bash
voxelkit inspect scene.tif
```

```json
{
  "filename": "scene.tif",
  "format": "tiff",
  "shape": [4, 1024, 1024],
  "ndim": 3,
  "dtype": "uint16",
  "page_count": 4,
  "axes": "CYX",
  "is_geotiff": true,
  "crs": "EPSG:32633",
  "bounds": [300000.0, 5790000.0, 310240.0, 5800240.0],
  "resolution": [10.0, 10.0],
  "band_count": 4
}
```

```bash
voxelkit inspect scene.tif --format text
```

```
filename    scene.tif
format      tiff
shape       4 x 1024 x 1024
ndim        3
dtype       uint16
page_count  4
axes        CYX
is_geotiff  True
crs         EPSG:32633
bounds      300000.0, 5790000.0, 310240.0, 5800240.0
resolution  10.0, 10.0
band_count  4
```

---

## Notes

- Files without a CRS (plain scientific TIFFs, z-stacks) are returned as normal `TiffInspectResult` — no geo fields, no error.
- `report` statistics (min, max, mean, NaN counts etc.) are computed over the full pixel array regardless of whether the file is a GeoTIFF.
- Multi-band GeoTIFFs are supported. The reported `shape` follows tifffile's axis ordering (bands first for multi-band CYX arrays).
- For batch workflows, `report-batch` picks up `.tif`/`.tiff` files and enriches them with geo fields when rasterio is available.

!!! tip "Earth observation workflows"
    Combine `report-batch --csv` with geo-enriched inspect to build a tabular inventory of a satellite image archive — CRS, bounds, resolution, and QA stats in one pass.
