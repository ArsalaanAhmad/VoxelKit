---
description: voxelkit gui — launch the optional local Streamlit interface for point-and-click workflows.
---

# voxelkit gui

```bash
voxelkit gui
```

Launches a local Streamlit app in your browser — a point-and-click interface for inspecting, previewing, and reporting on imaging files without any command-line flags.

---

## Requirements

The GUI is an **optional extra**. Install it with:

```bash
pip install voxelkit[gui]
```

If you try to run `voxelkit gui` without the extra installed, you'll get a clear error message telling you what to install.

---

## Usage

```bash
voxelkit gui
```

That's it. Streamlit will open the app in your default browser automatically (usually at `http://localhost:8501`).

---

## What it does

The GUI wraps the same library functions as the CLI — inspect, preview, report — in a drag-and-drop interface. It's useful for:

- Quickly exploring a new dataset without writing any code
- Sharing a tool with colleagues who aren't comfortable with the CLI
- Teaching or demo environments

It runs entirely locally — no files are sent anywhere.

---

## Notes

- The GUI is a prototype. For production use or scripting, prefer the CLI or Python library.
- To stop the server, hit `Ctrl+C` in the terminal where you ran `voxelkit gui`.
