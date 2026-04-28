---
description: VoxelKit REST API TIFF endpoints — POST /tiff/metadata, /tiff/preview, and /tiff/report.
---

# TIFF endpoints

Three endpoints for TIFF files (`.tif`, `.tiff`).

---

## POST /tiff/metadata

Extract metadata from an uploaded TIFF file. Only the file header is read — no pixel data is loaded.

**Request:** `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `file` | file | A `.tif` or `.tiff` file |

**Response:** `application/json`

```json
{
  "filename": "volume.tiff",
  "format": "tiff",
  "shape": [50, 512, 512],
  "ndim": 3,
  "dtype": "uint16",
  "page_count": 50,
  "axes": "ZYX"
}
```

**Example:**

```bash
curl -X POST http://127.0.0.1:8000/tiff/metadata \
  -F "file=@volume.tiff"
```

---

## POST /tiff/preview

Generate a PNG slice from an uploaded TIFF file. For 2D TIFFs the full image is returned. For 3D z-stacks a single plane is extracted.

**Request:** `multipart/form-data` + query parameters

| Field | Type | Description |
|---|---|---|
| `file` | file | A `.tif` or `.tiff` file |

| Query param | Type | Required | Default | Description |
|---|---|---|---|---|
| `axis` | integer | No | `0` | Slice axis for 3D z-stacks (0=Z, 1=Y, 2=X) |
| `slice_index` | integer | No | centre | Slice index |

**Response:** `image/png`

**Example:**

```bash
curl -X POST "http://127.0.0.1:8000/tiff/preview?axis=0&slice_index=25" \
  -F "file=@volume.tiff" \
  --output tiff_preview.png
```

---

## POST /tiff/report

Generate a QA report for an uploaded TIFF file.

**Request:** `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `file` | file | A `.tif` or `.tiff` file |

**Response:** `application/json`

```json
{
  "filename": "volume.tiff",
  "format": "tiff",
  "shape": [50, 512, 512],
  "dtype": "uint16",
  "min": 0,
  "max": 65410,
  "mean": 12043.2,
  "std": 8821.5,
  "nan_count": 0,
  "inf_count": 0,
  "zero_fraction": 0.08,
  "warnings": []
}
```

**Example:**

```bash
curl -X POST http://127.0.0.1:8000/tiff/report \
  -F "file=@volume.tiff"
```
