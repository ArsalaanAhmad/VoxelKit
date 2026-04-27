# Getting Started

## Installation

```bash
pip install voxelkit
```

For local development:

```bash
pip install -e .
```

Optional GUI extras:

```bash
pip install -e .[gui]
```

## First Commands

```bash
voxelkit -h
voxelkit inspect tests/fixtures/sample_nested.h5
voxelkit report tests/fixtures/sample_3d.nii.gz
```

## Generate Local Fixtures

```bash
python tests/create_fixtures.py
```

## Where To Go Next

- [CLI Usage](cli.md)
- [Python Usage](python-usage.md)
- [QA Warnings](qa-warnings.md)
