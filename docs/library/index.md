---
description: VoxelKit Python library overview — four functions, one import, every supported format.
---

# Library Reference

VoxelKit was built library-first. The CLI and REST API are just thin layers on top of these Python functions — which means you get the full power of the library when you use it directly in your code.

One import is all you need:

```python
from voxelkit import inspect_file, preview_file, report_file, report_batch
```

---

## The four main functions

Each function auto-detects the file format from the extension, so you don't have to think about which module handles which format.

| Function | What it returns | Page |
|---|---|---|
| `inspect_file(path)` | Metadata dict — shape, dtype, headers | [→](inspect.md) |
| `preview_file(path, ...)` | PNG image as `bytes` | [→](preview.md) |
| `report_file(path, ...)` | QA stats + warnings dict | [→](report.md) |
| `report_batch(path, ...)` | List of reports for a whole directory | [→](batch.md) |

---

## Embedding-specific functions

If you're working with 2D feature matrices (N samples × D dimensions), these two go deeper than the standard `report_file`:

| Function | What it returns | Page |
|---|---|---|
| `report_embedding(path)` | Per-dimension + per-sample QA | [→](embedding.md) |
| `preview_embedding(path, ...)` | Heatmap PNG as `bytes` | [→](embedding.md) |

---

## A note on format-specific imports

The four main functions cover 95% of use cases. But if you need direct access to a format-specific module — for example, to call NIfTI inspection directly — those are also exported:

```python
from voxelkit import (
    inspect_h5, preview_h5, report_h5,
    inspect_npy, preview_npy, report_npy,
    nifti_metadata, preview_nifti, report_nifti,
    inspect_tiff, preview_tiff, report_tiff,
    report_embedding, preview_embedding,
)
```

For most work, stick with `inspect_file`, `preview_file`, `report_file`, and `report_batch`.
