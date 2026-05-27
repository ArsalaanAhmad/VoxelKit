# Contributing to VoxelKit

Thanks for your interest in contributing.

The full contributing guide — local setup, workflow, code guidelines, PR checklist, and how to report issues — lives at:

**[arsalaanahmad.github.io/VoxelKit/contributing/](https://arsalaanahmad.github.io/VoxelKit/contributing/)**

## Adding a new file format?

Start from the worked skeleton at [`voxelkit/templates/format_template.py`](voxelkit/templates/format_template.py). It walks through every step — extension declaration, the three `inspect` / `preview` / `report` callables, CLI adapter signatures, library-level dispatch, and the test layout — in one annotated file. The three callables must match the Protocols in [`voxelkit/core/handler.py`](voxelkit/core/handler.py) (`InspectFn`, `PreviewFn`, `ReportFn`); `FormatRoute` arity-checks them at registration time.
