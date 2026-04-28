---
description: VoxelKit REST API embedding endpoints — POST /embedding/report and POST /embedding/preview.
---

# Embedding endpoints

Two endpoints for 2D embedding matrices (`.npy` files with shape `(N_samples, D_dims)`).

---

## POST /embedding/report

Generate an embedding-aware QA report for an uploaded `.npy` matrix.

**Request:** `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `file` | file | A `.npy` file containing a 2D float array |

**Response:** `application/json`

```json
{
  "filename": "features.npy",
  "format": "numpy",
  "n_samples": 10000,
  "n_dims": 512,
  "dtype": "float32",
  "total_nan_count": 0,
  "total_inf_count": 0,
  "dead_dim_count": 3,
  "nan_dim_count": 0,
  "inf_dim_count": 0,
  "norm_mean": 14.2,
  "norm_std": 1.8,
  "outlier_sample_count": 12,
  "warnings": [
    "3/512 dimensions are dead (std ≈ 0).",
    "12 sample(s) have anomalous L2 norm (>3σ from mean)."
  ]
}
```

**Example:**

```bash
curl -X POST http://127.0.0.1:8000/embedding/report \
  -F "file=@features.npy"
```

```python
import httpx

with open("features.npy", "rb") as f:
    response = httpx.post(
        "http://127.0.0.1:8000/embedding/report",
        files={"file": f},
    )

report = response.json()
print(f"Dead dims: {report['dead_dim_count']}")
print(f"Outliers: {report['outlier_sample_count']}")
```

---

## POST /embedding/preview

Render an uploaded `.npy` embedding matrix as a per-column-normalised PNG heatmap.

Each pixel row is one sample, each pixel column is one embedding dimension. Dead dimensions appear as uniform mid-grey stripes. Large matrices are randomly subsampled.

**Request:** `multipart/form-data` + query parameters

| Field | Type | Description |
|---|---|---|
| `file` | file | A `.npy` file containing a 2D float array |

| Query param | Type | Required | Default | Description |
|---|---|---|---|---|
| `max_samples` | integer | No | `256` | Maximum rows to render. Large matrices are randomly subsampled |

**Response:** `image/png`

**Example:**

```bash
curl -X POST "http://127.0.0.1:8000/embedding/preview?max_samples=512" \
  -F "file=@features.npy" \
  --output heatmap.png
```

```python
import httpx

with open("features.npy", "rb") as f:
    response = httpx.post(
        "http://127.0.0.1:8000/embedding/preview",
        params={"max_samples": 512},
        files={"file": f},
    )

with open("heatmap.png", "wb") as out:
    out.write(response.content)
```
