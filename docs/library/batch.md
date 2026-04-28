---
description: report_batch — run QA reports across an entire directory of imaging files at once.
---

# report_batch

```python
from voxelkit import report_batch

results = report_batch("my_dataset/")
```

`report_batch` scans a directory, finds every supported file inside it, runs `report_file` on each one, and hands you back the full list. It's the fastest way to get a health check across a whole dataset — one call, every file, one result.

---

## Signature

```python
def report_batch(
    path: str | Path,
    recursive: bool = True,
) -> list[dict]
```

---

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `path` | `str` or `Path` | — | Directory to scan |
| `recursive` | `bool` | `True` | Whether to descend into subdirectories |

---

## Return value

A list of report dictionaries — one per file found. Each dictionary is the same structure as what `report_file` returns for that format, plus a `warnings` list. Files that fail to process are included with an `error` key instead of stats.

```python
[
  {
    "filename": "subject01_bold.nii.gz",
    "format": "nifti",
    "shape": [64, 64, 30, 200],
    "warnings": [],
    ...
  },
  {
    "filename": "subject02_bold.nii.gz",
    "format": "nifti",
    "warnings": ["Array is mostly zeros."],
    ...
  },
  ...
]
```

---

## Examples

```python
from voxelkit import report_batch

results = report_batch("data/study_01/", recursive=True)

# count files with warnings
flagged = [r for r in results if r.get("warnings")]
print(f"{len(flagged)} of {len(results)} files have warnings")

# print all warnings
for r in flagged:
    print(r["filename"], "→", r["warnings"])
```

Save to JSON for later review:

```python
import json
from voxelkit import report_batch

results = report_batch("data/study_01/")

with open("batch_report.json", "w") as f:
    json.dump(results, f, indent=2)
```

Only scan the top level (no subdirectories):

```python
results = report_batch("data/study_01/", recursive=False)
```

---

!!! tip "What counts as a supported file?"
    VoxelKit scans for `.nii`, `.nii.gz`, `.h5`, `.hdf5`, `.npy`, `.npz`, `.tif`, and `.tiff` files. Other files in the directory are silently skipped.
