---
description: VoxelKit CLI overview — seven commands for inspecting, previewing, and QA-checking imaging files from the terminal.
---

# CLI Reference

The `voxelkit` command gives you everything in the library without writing a line of Python.

```bash
voxelkit --help
```

There are seven commands total:

| Command | What it does |
|---|---|
| [`inspect`](inspect.md) | Print file metadata as JSON |
| [`preview`](preview.md) | Save a PNG slice to disk |
| [`report`](report.md) | Print a QA report as JSON |
| [`report-batch`](batch.md) | QA report for every file in a directory |
| [`embed-report`](embed-report.md) | Per-dimension + per-sample embedding QA |
| [`embed-preview`](embed-preview.md) | Render an embedding matrix as a heatmap PNG |
| [`gui`](gui.md) | Launch the local Streamlit interface |

---

## Quick orientation

Every command that outputs data prints JSON to stdout. You can pipe it, save it, or format it however you like:

```bash
# pipe to jq for pretty inspection
voxelkit inspect myfile.nii.gz | jq '.shape'

# save to a file
voxelkit report myfile.h5 > report.json
```

Commands that generate images always require `--output`:

```bash
voxelkit preview myfile.nii.gz --plane axial --output preview.png
```

---

## Global help

```bash
voxelkit --help            # top-level help
voxelkit inspect --help    # help for a specific command
```

Use the sidebar to jump to any individual command.
