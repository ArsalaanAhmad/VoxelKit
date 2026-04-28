---
description: report_embedding and preview_embedding — specialized QA for 2D feature matrices and embedding spaces.
---

# Embedding Analysis

Standard QA tools (like `report_file`) treat your array as a flat collection of numbers. That's fine for most imaging data, but it misses the failure modes that matter for embedding spaces — things like dead dimensions, collapsed outputs, and outlier sample vectors.

These two functions go deeper.

---

## report_embedding

```python
from voxelkit import report_embedding

report = report_embedding("features.npy")
print(report["dead_dim_count"])    # how many dimensions carry no signal
print(report["outlier_sample_count"])  # how many samples are anomalous
```

### Signature

```python
def report_embedding(file_path: str) -> dict
```

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `file_path` | `str` | Path to a `.npy` file containing a 2D `(N_samples, D_dims)` float array |

!!! info "Only .npy is supported"
    `.npz` is not accepted here because embedding matrices are expected to be a single flat array. If your matrix is inside an `.npz`, extract it first: `np.save("out.npy", np.load("data.npz")["X"])`.

### Return value

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
    "3/512 dimensions are dead (std ≈ 0). This may indicate a collapsed or undertrained embedding space.",
    "12 sample(s) have anomalous L2 norm (>3σ from mean). These may be corrupted or out-of-distribution embedding vectors."
  ]
}
```

### What gets checked

**Per-dimension (column-wise):**

- **Dead dimensions** — columns whose std across all samples is near zero (`< 1e-8`). These carry no signal and will silently corrupt downstream distance computations. A warning fires when more than 5% of dimensions are dead.
- **NaN dimensions** — columns with any `NaN` value. These corrupt any dot product or cosine similarity that uses them.
- **Inf dimensions** — same for `Inf` values.

**Per-sample (row-wise):**

- **Outlier samples** — rows whose L2 norm is more than 3σ from the mean norm. These are likely corrupted or out-of-distribution embedding vectors.
- **Collapsed embedding space** — if all sample L2 norms are identical (std = 0), the model has collapsed to producing the same output for every input.

---

## preview_embedding

```python
from voxelkit import preview_embedding

png = preview_embedding("features.npy", max_samples=256)

with open("heatmap.png", "wb") as f:
    f.write(png)
```

Renders the embedding matrix as a **per-column-normalised heatmap** PNG. Each row is one sample, each column is one dimension. Dead dimensions (no variance) appear as uniform mid-grey stripes — they stand out immediately.

### Signature

```python
def preview_embedding(
    file_path: str,
    max_samples: int = 256,
) -> bytes
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `file_path` | `str` | — | Path to a `.npy` 2D embedding file |
| `max_samples` | `int` | `256` | Maximum rows to render. Large matrices are randomly subsampled |

### Return value

Raw PNG bytes. Each pixel column is independently normalised so structure within dimensions is visible regardless of overall scale differences.

---

## Full example

```python
from voxelkit import report_embedding, preview_embedding

# Check for quality issues
report = report_embedding("model_outputs.npy")

print(f"Shape: {report['n_samples']} samples × {report['n_dims']} dims")
print(f"Dead dimensions: {report['dead_dim_count']}")
print(f"Outlier samples: {report['outlier_sample_count']}")

if report["warnings"]:
    print("\nWarnings:")
    for w in report["warnings"]:
        print(" •", w)

# Visualise it
png = preview_embedding("model_outputs.npy", max_samples=512)
with open("heatmap.png", "wb") as f:
    f.write(png)
```
