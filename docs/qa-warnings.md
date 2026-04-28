---
description: VoxelKit QA warnings — what each warning means and what to do about it.
---

# QA Warnings

Whenever `report_file`, `report_batch`, or `voxelkit report` runs, it checks for known data quality issues and appends any problems to the `warnings` list. An empty list means everything looks fine.

Here's what each warning means and what you should do when you see it.

---

## Array is constant or nearly constant

**What it means:** All values in the array are the same (or nearly the same). There's no signal variation in the data.

**What causes it:** A failed scan, a zero-padded placeholder, a corrupted export, or a preprocessing bug that flattened the values.

**What to do:** Double-check the source file. If it's supposed to have variation (e.g. an fMRI BOLD signal), this is a problem. If it's an intentional mask or label file, it may be expected.

---

## Array is mostly zeros

**What it means:** More than 95% of the array's values are exactly zero.

**What causes it:** Over-aggressive masking, a failed normalization step, or the array was never filled properly.

**What to do:** Check whether the zero regions are intentional (brain mask, background). If you expected real signal, investigate the pipeline step that produced the file.

---

## Contains NaNs

**What it means:** The array contains one or more `NaN` (not-a-number) values.

**What causes it:** Division by zero during preprocessing, failed interpolation, or loading from a corrupted source.

**What to do:** This is almost always a bug. NaNs propagate silently through computations — a single NaN can corrupt a model loss or a summary statistic. Track down where it was introduced and fix it before using the data.

---

## Contains Infs

**What it means:** The array contains one or more `Inf` (infinite) values.

**What causes it:** Same causes as NaNs — overflow, division by near-zero values, or a failed normalization.

**What to do:** Same advice as NaNs. Infs are just as dangerous and harder to spot in summary statistics because they affect the mean and std dramatically.

---

## Unsupported dimensionality for preview

**What it means:** VoxelKit can't generate a 2D preview of this array because its dimensionality isn't supported (e.g. a 1D or 5D array).

**What to do:** This only affects `preview_file` / `voxelkit preview`. The inspection and report functions will still work fine. If you need a visual, extract a slice manually before calling preview.

---

## Embedding-specific warnings

These appear in `report_embedding` / `voxelkit embed-report` output only.

### N dimensions are dead (std ≈ 0)

Some embedding dimensions carry no signal — their values are identical across all samples. A warning fires when more than 5% of dimensions are dead.

**What causes it:** A collapsed layer in the model, a bug in the feature extraction pipeline, or an undertrained embedding space.

**What to do:** Investigate the model or pipeline that produced the embeddings. Dead dimensions are wasted capacity and can cause instability in downstream distance computations.

### N dimension(s) contain NaN / Inf

One or more columns have non-finite values that will corrupt any dot product or cosine similarity that uses them.

**What to do:** Same as the global NaN/Inf warnings above — this is a bug, not a data property.

### N sample(s) have anomalous L2 norm (>3σ from mean)

Some samples have embedding vectors whose length is more than 3 standard deviations from the mean. These are likely corrupted or out-of-distribution.

**What to do:** Inspect the flagged samples. They may need to be removed before training or retrieval.

### All sample L2 norms are identical

Every sample has the same L2 norm — the embedding space has collapsed to a single point. No two samples are distinguishable.

**What to do:** Your model almost certainly has a bug. This is a hard failure, not a minor warning.
