---
description: anonymise_directory -- scrub PHI tags from an entire DICOM directory tree.
---

# anonymise_directory

```python
from voxelkit.dicom import anonymise_directory

summary = anonymise_directory(
    input_dir="./incoming_studies/",
    output_dir="./anonymised/",
)
print(summary["files_anonymised"], "files scrubbed")
```

Scrubs PHI tags from every `.dcm` file under `input_dir` and writes clean copies to `output_dir`. The source tree is never touched. Non-DICOM files are skipped, and the directory structure is mirrored exactly.

---

## Signature

```python
def anonymise_directory(
    input_dir: str | Path,
    output_dir: str | Path,
    *,
    recursive: bool = True,
) -> AnonymiseSummary
```

## Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `input_dir` | `str` or `Path` | required | Source directory to read from |
| `output_dir` | `str` or `Path` | required | Destination directory for the cleaned files |
| `recursive` | `bool` | `True` | Whether to descend into subdirectories |

The function raises `ValueError` upfront if `input_dir` and `output_dir` resolve to the same path, to prevent overwriting source data.

---

## Return value

```python
{
    "total_dcm_files": 312,
    "files_anonymised": 310,
    "failures": ["series_b/corrupt.dcm"],
    "scrubbed_tag_counts": {
        "PatientName": 310,
        "PatientID": 310,
        "PatientBirthDate": 305,
    },
    "input_dir": "/abs/path/incoming_studies",
    "output_dir": "/abs/path/anonymised"
}
```

The function never raises mid-run. If a file is corrupt or unreadable it goes into `failures` and the rest of the dataset still gets processed.

---

## Example

```python
from voxelkit.dicom import anonymise_directory

summary = anonymise_directory(
    input_dir="./incoming_studies/",
    output_dir="./anonymised/",
)

print(f"Scrubbed {summary['files_anonymised']} of {summary['total_dcm_files']} files")

if summary["failures"]:
    print("These files could not be processed:")
    for f in summary["failures"]:
        print(" ", f)
```
