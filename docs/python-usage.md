# Python Usage

Use VoxelKit directly as a library.

```python
from voxelkit import inspect_file, preview_file, report_file, report_batch

metadata = inspect_file("tests/fixtures/sample_3d.nii.gz")

png_bytes = preview_file(
    "tests/fixtures/sample_3d.nii.gz",
    plane="axial",
    slice_index=4,
)
with open("preview.png", "wb") as output_file:
    output_file.write(png_bytes)

single_report = report_file(
    "tests/fixtures/sample_nested.h5",
    dataset_path="data/subject01/run1/bold",
)

batch_report = report_batch("tests/fixtures", recursive=True)
```
