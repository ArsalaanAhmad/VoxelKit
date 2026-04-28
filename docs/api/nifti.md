---
description: VoxelKit REST API NIfTI endpoints — POST /nifti/metadata and POST /nifti/preview.
---

# NIfTI endpoints

Two endpoints for NIfTI files (`.nii`, `.nii.gz`).

---

## POST /nifti/metadata

Extract metadata from an uploaded NIfTI file.

**Request:** `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `file` | file | A `.nii` or `.nii.gz` file |

**Response:** `application/json`

```json
{
  "filename": "scan.nii.gz",
  "format": "nifti",
  "shape": [64, 64, 30],
  "voxel_sizes": [3.0, 3.0, 4.0],
  "data_dtype": "float32",
  "affine": [[...], ...],
  "header": { "...": "..." }
}
```

**Example:**

```bash
curl -X POST http://127.0.0.1:8000/nifti/metadata \
  -F "file=@bold.nii.gz"
```

```python
import httpx

with open("bold.nii.gz", "rb") as f:
    response = httpx.post(
        "http://127.0.0.1:8000/nifti/metadata",
        files={"file": f},
    )
print(response.json()["shape"])
```

---

## POST /nifti/preview

Generate a PNG slice preview from an uploaded NIfTI file.

**Request:** `multipart/form-data` + query parameters

| Field | Type | Description |
|---|---|---|
| `file` | file | A `.nii` or `.nii.gz` file |

| Query param | Type | Required | Description |
|---|---|---|---|
| `plane` | string | Yes | One of `axial`, `coronal`, `sagittal` |
| `slice_index` | integer | No | Slice index; defaults to centre |

**Response:** `image/png`

**Example:**

```bash
curl -X POST "http://127.0.0.1:8000/nifti/preview?plane=axial&slice_index=10" \
  -F "file=@bold.nii.gz" \
  --output preview.png
```

```python
import httpx

with open("bold.nii.gz", "rb") as f:
    response = httpx.post(
        "http://127.0.0.1:8000/nifti/preview",
        params={"plane": "axial", "slice_index": 10},
        files={"file": f},
    )

with open("preview.png", "wb") as out:
    out.write(response.content)
```
