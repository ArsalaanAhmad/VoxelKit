---
description: voxelkit embed-preview — render a 2D embedding matrix as a per-column-normalised heatmap PNG.
---

# voxelkit embed-preview

```bash
voxelkit embed-preview features.npy --output heatmap.png
```

Renders your embedding matrix as a PNG heatmap and saves it to disk. Each row is one sample, each column is one dimension. Dead dimensions (no variance) show up as flat mid-grey stripes — they're immediately obvious in the image.

---

## Usage

```
voxelkit embed-preview FILE --output OUTPUT [options]
```

### Arguments

| Argument | Description |
|---|---|
| `FILE` | Path to a `.npy` 2D `(N_samples, D_dims)` float array |

### Flags

| Flag | Default | Description |
|---|---|---|
| `--output PATH` | — | **Required.** Output `.png` file path |
| `--max-samples INT` | `256` | Maximum number of sample rows to render. Large matrices are randomly subsampled |

---

## Examples

```bash
# basic — renders up to 256 samples
voxelkit embed-preview features.npy --output heatmap.png

# render more rows for a denser view
voxelkit embed-preview features.npy --max-samples 1024 --output heatmap_full.png
```

---

## What the image shows

The heatmap is **per-column-normalised**: each dimension (column) is independently scaled to 0–255, so you can see internal structure in dimensions regardless of their absolute scale.

- Bright/dark variation in a column → that dimension carries signal
- Flat uniform colour in a column → **dead dimension** (no variance)
- Isolated extremely bright or dark rows → potential outlier samples

Use this alongside `voxelkit embed-report` — the report gives you the numbers, the heatmap gives you the picture.
