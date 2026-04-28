---
description: voxelkit embed-report — per-dimension and per-sample QA for 2D embedding matrices.
---

# voxelkit embed-report

```bash
voxelkit embed-report features.npy
```

Runs embedding-aware QA on a `.npy` feature matrix and prints the result as JSON. This goes deeper than `voxelkit report` — instead of treating the array as a flat collection of numbers, it analyses it as a matrix of sample vectors and catches embedding-specific failures.

---

## Usage

```
voxelkit embed-report FILE
```

### Arguments

| Argument | Description |
|---|---|
| `FILE` | Path to a `.npy` file containing a 2D `(N_samples, D_dims)` float array |

!!! info "`.npy` only"
    Only `.npy` is supported. If your matrix is inside an `.npz` archive, extract it first.

---

## Example

```bash
voxelkit embed-report model_outputs.npy
```

Output:

```json
{
  "filename": "model_outputs.npy",
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
    "12 sample(s) have anomalous L2 norm (>3σ from mean)."
  ]
}
```

---

## What gets checked

- **Dead dimensions** — columns with near-zero std (no signal)
- **NaN / Inf dimensions** — columns that would corrupt similarity computations
- **Outlier samples** — rows with L2 norm more than 3σ from the mean
- **Collapsed embedding space** — all sample norms are identical (model collapsed)

See [Embedding Analysis](../library/embedding.md) for the full explanation.
