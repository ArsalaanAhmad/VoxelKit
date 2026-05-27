---
description: Install VoxelKit and run your first inspect, preview, and report commands in under five minutes.
---

# Getting Started

Hey — welcome. VoxelKit is a toolkit for inspecting, previewing, and QA-checking multidimensional imaging files (NIfTI, HDF5, NumPy, TIFF, DICOM) without needing to know the details of each format's Python library. DICOM gets PHI-stripping by default, plus dedicated `anonymise` and `convert` commands.

This page gets you from zero to your first result in about five minutes.

---

## Install

```bash
pip install voxelkit
```

That covers everything — the Python library, the CLI, and the REST API server. The only thing not included by default is the optional local GUI:

```bash
pip install voxelkit[gui]
```

**Python 3.9 or later is required.**

??? tip "Installing from source (for contributors)"
    ```bash
    git clone https://github.com/ArsalaanAhmad/VoxelKit.git
    cd VoxelKit
    pip install -e .
    ```

---

## Your first three commands

Once installed, the `voxelkit` command is available in your terminal. Try these on any file you have:

```bash
voxelkit inspect yourfile.nii.gz      # What's in this file?
voxelkit report  yourfile.h5          # Is the data healthy?
voxelkit preview yourfile.npy --output preview.png   # Show me a slice
```

VoxelKit figures out the format from the file extension — no flags needed for that.

For DICOM, you can pass either a single `.dcm` file or a directory of slices (a series):

```bash
voxelkit inspect scan.dcm                                # single slice
voxelkit inspect ./series/                               # auto-detected as a DICOM series
voxelkit anonymise ./incoming/ --output ./anonymised/    # scrub PHI in bulk
voxelkit convert ./series/ volume.nii.gz                 # DICOM → NIfTI
```

Patient identifiers are stripped from `inspect` output by default. Pass `--phi` to include them — VoxelKit will print a stderr warning so you know the result is PHI-bearing.

---

## Don't have a file? Generate the test fixtures

The repo ships with a script that creates small sample files for every supported format:

```bash
python tests/create_fixtures.py
```

Then run against them:

```bash
voxelkit inspect tests/fixtures/sample_3d.nii.gz
voxelkit report  tests/fixtures/sample_nested.h5 --dataset data/subject01/run1/bold
voxelkit preview tests/fixtures/sample_3d.nii.gz --plane axial --slice 4 --output out.png
voxelkit inspect tests/fixtures/sample.dcm
voxelkit inspect tests/fixtures/sample_series/
```

---

## What to read next

Pick the interface that fits your workflow:

<div class="grid cards" markdown>

- :material-language-python: **[Library Reference](library/index.md)**

    Use VoxelKit directly in Python code — four functions, one import.

- :material-console: **[CLI Reference](cli/index.md)**

    Run everything from the terminal. Good for quick one-off checks.

- :material-api: **[REST API](api/index.md)**

    Start a local HTTP server and call VoxelKit over HTTP from any stack.

</div>
