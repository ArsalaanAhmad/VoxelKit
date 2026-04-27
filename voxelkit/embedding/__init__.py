"""Embedding-aware QA tools for (N_samples, D_dims) feature matrices.

This submodule treats 2D NumPy arrays as embedding matrices rather than
spatial images. Unlike the spatial QA in the core report module, it analyses
data column-wise (per embedding dimension) and row-wise (per sample), surfacing
failure modes that global statistics miss — dead dimensions, corrupted samples,
and collapsed embedding spaces.

Typical use:

    from voxelkit.embedding import report, preview

    result = report("embeddings.npy")
    print(result["dead_dim_count"], result["outlier_sample_count"])

    png = preview("embeddings.npy")
    Path("heatmap.png").write_bytes(png)
"""

from voxelkit.embedding.preview import preview
from voxelkit.embedding.report import report


__all__ = ["report", "preview"]
