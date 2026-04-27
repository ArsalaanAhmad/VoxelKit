# QA Warnings

VoxelKit reports warning signals for problematic data patterns.

## Current warning types

- `Array is constant or nearly constant.`
- `Array is mostly zeros.`
- `Contains NaNs.`
- `Contains Infs.`
- `Unsupported dimensionality for preview.`

## Why these matter

These warnings help catch data quality issues early, before training, visualization, or downstream analysis.

## Batch visibility

`report-batch` aggregates warning counts across files so you can quickly identify dataset-level risks.

```bash
voxelkit report-batch tests/fixtures --output batch_report.json
```
