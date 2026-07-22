---
description: GeoTIFF support in the VoxelKit library -- enriched inspect results for georeferenced raster files.
---

# GeoTIFF (Library)

When `rasterio` is installed, `inspect_file` on a `.tif` or `.tiff` automatically checks whether the file carries a coordinate reference system (CRS). If it does, the result gets enriched with geospatial fields. If it doesn't, you get a plain `TiffInspectResult` with no extra keys and no error.

This enrichment happens transparently inside `inspect_file`. There is no separate function to call and no flag to pass.

---

## Install

```bash
pip install voxelkit[geo]
```

Without `rasterio`, `.tif` and `.tiff` files are still fully supported. All the normal inspect, report, and preview functions work fine. You just won't get the geo fields.

---

## Enriched inspect result

```python
from voxelkit import inspect_file

result = inspect_file("scene.tif")

print(result.get("is_geotiff"))  # True if rasterio is installed and a CRS was found
print(result.get("crs"))         # "EPSG:32633"
print(result.get("bounds"))      # [300000.0, 5790000.0, 310240.0, 5800240.0]
print(result.get("resolution"))  # [10.0, 10.0]
print(result.get("band_count"))  # 4
```

The full result for a georeferenced file looks like:

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

### Geo fields

| Field | Type | Description |
|---|---|---|
| `is_geotiff` | `bool` | Present and `True` when geo metadata was found |
| `crs` | `str` | Coordinate reference system string, e.g. `"EPSG:4326"` |
| `bounds` | `list[float]` | `[left, bottom, right, top]` in the CRS unit |
| `resolution` | `list[float]` | Pixel size as `[x_res, y_res]` in the CRS unit |
| `band_count` | `int` | Number of raster bands |

---

## Using report_file with GeoTIFFs

`report_file` works exactly the same as for any TIFF. Stats are computed over the full pixel array and the result is a standard `FileReportResult` without the geo fields. If you need geo metadata alongside QA stats, call both functions and combine:

```python
from voxelkit import inspect_file, report_file

meta = inspect_file("scene.tif")
report = report_file("scene.tif")

geo_keys = ("crs", "bounds", "resolution", "band_count")
combined = {**report, **{k: meta[k] for k in geo_keys if k in meta}}
```

---

## Batch workflows

`report_batch` picks up `.tif` and `.tiff` files and each file gets inspect enrichment when `rasterio` is available. That means CRS, bounds, and resolution appear alongside QA stats in one pass:

```python
from voxelkit import report_batch
import json

results = report_batch("./satellite_archive/")

with open("inventory.json", "w") as f:
    json.dump(results, f, indent=2)

geo_files = [r for r in results if r.get("is_geotiff")]
print(f"{len(geo_files)} GeoTIFF files in archive")
```

---

## Notes

- Files without a CRS (plain scientific TIFFs, z-stacks, microscopy images) come back as a normal `TiffInspectResult`. No geo fields, no error.
- `rasterio` is an optional dependency. If it is not installed, the inspect result is the same as if the file had no geo data.
- Multi-band GeoTIFFs are supported. The `shape` follows tifffile's axis ordering (bands first for CYX arrays).
- The `GeoTiffInspectResult` type is importable from `voxelkit.core.types` if you need type annotations in your own code.
