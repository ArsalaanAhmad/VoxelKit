# CLI Usage

VoxelKit CLI command groups:

- `inspect`: metadata/structure summary
- `preview`: PNG preview generation
- `report`: per-file QA report
- `report-batch`: directory-level QA summary

## inspect

```bash
voxelkit inspect tests/fixtures/sample_3d.nii.gz
voxelkit inspect tests/fixtures/sample_nested.h5
```

## preview

```bash
voxelkit preview tests/fixtures/sample_3d.nii.gz --plane axial --slice 4 --output nifti_preview.png
voxelkit preview tests/fixtures/sample_nested.h5 --dataset data/subject01/run1/bold --axis 2 --slice 4 --output h5_preview.png
```

## report

```bash
voxelkit report tests/fixtures/sample_3d.nii.gz
voxelkit report tests/fixtures/sample_nested.h5 --dataset data/subject01/run1/bold
```

## report-batch

```bash
voxelkit report-batch tests/fixtures
voxelkit report-batch tests/fixtures --no-recursive
voxelkit report-batch tests/fixtures --output batch_report.json
```
