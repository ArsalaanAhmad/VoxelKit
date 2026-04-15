"""Minimal command-line interface for VoxelKit.

This module is intentionally thin: it parses arguments, routes by file extension,
and calls format-specific functions from the library layer.
"""

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from voxelkit.core.errors import ValidationError
from voxelkit.h5 import inspect_h5, preview as preview_h5
from voxelkit.nifti import inspect as inspect_nifti
from voxelkit.nifti import preview as preview_nifti


InspectFn = Callable[[str], dict[str, Any]]
PreviewFn = Callable[[str, argparse.Namespace], bytes]


@dataclass(frozen=True)
class FormatRoute:
    """Routing metadata for one supported file format."""

    name: str
    extensions: tuple[str, ...]
    inspect_fn: InspectFn
    preview_fn: PreviewFn


FORMAT_ROUTES: list[FormatRoute] = []


def register_format(route: FormatRoute) -> None:
    """Register a new file-format route for CLI dispatch.

    This keeps extension routing explicit and easy to extend.
    """
    for existing in FORMAT_ROUTES:
        overlap = set(existing.extensions).intersection(route.extensions)
        if overlap:
            overlap_list = ", ".join(sorted(overlap))
            raise ValueError(
                f"Extension(s) already registered by format '{existing.name}': {overlap_list}"
            )
    FORMAT_ROUTES.append(route)


def _preview_nifti(file_path: str, args: argparse.Namespace) -> bytes:
    """Run NIfTI preview with CLI arguments."""
    if args.dataset is not None:
        raise ValidationError("--dataset is only valid for HDF5 preview.")
    if args.axis is not None:
        raise ValidationError("--axis is only valid for HDF5 preview.")

    return preview_nifti(
        file_path=file_path,
        plane=args.plane or "axial",
        slice_index=args.slice_index,
    )


def _preview_h5(file_path: str, args: argparse.Namespace) -> bytes:
    """Run HDF5 preview with CLI arguments."""
    if not args.dataset:
        raise ValidationError("--dataset is required for HDF5 preview.")
    if args.axis is None:
        raise ValidationError("--axis is required for HDF5 preview.")
    if args.plane is not None:
        raise ValidationError("--plane is only valid for NIfTI preview.")

    return preview_h5(
        file_path=file_path,
        dataset_path=args.dataset,
        axis=args.axis,
        slice_index=args.slice_index,
    )


def _register_builtin_formats() -> None:
    """Register VoxelKit's built-in formats in one place."""
    register_format(
        FormatRoute(
            name="nifti",
            extensions=(".nii.gz", ".nii"),
            inspect_fn=inspect_nifti,
            preview_fn=_preview_nifti,
        )
    )
    register_format(
        FormatRoute(
            name="h5",
            extensions=(".h5", ".hdf5"),
            inspect_fn=inspect_h5,
            preview_fn=_preview_h5,
        )
    )


_register_builtin_formats()


def _resolve_route(file_path: str) -> FormatRoute:
    """Find the route for a file based on extension."""
    lowered = file_path.lower()
    for route in FORMAT_ROUTES:
        if any(lowered.endswith(ext) for ext in route.extensions):
            return route

    supported = ", ".join(ext for route in FORMAT_ROUTES for ext in route.extensions)
    raise ValidationError(f"Unsupported file extension. Supported extensions: {supported}")


def _supported_extensions_text() -> str:
    """Return a comma-separated list of registered file extensions."""
    return ", ".join(ext for route in FORMAT_ROUTES for ext in route.extensions)


def _handle_inspect(args: argparse.Namespace) -> None:
    """Handle the inspect command and print JSON."""
    route = _resolve_route(args.file)
    result = route.inspect_fn(args.file)
    print(json.dumps(result, indent=2))


def _handle_preview(args: argparse.Namespace) -> None:
    """Handle the preview command and write PNG bytes to disk."""
    route = _resolve_route(args.file)
    png_bytes = route.preview_fn(args.file, args)

    output_path = Path(args.output)
    if output_path.parent and not output_path.parent.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_bytes(png_bytes)
    print(f"Wrote preview PNG: {output_path}")


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI parser."""
    parser = argparse.ArgumentParser(
        prog="voxelkit",
        description="Inspect and preview NIfTI/HDF5 imaging files.",
    )
    subparsers = parser.add_subparsers(dest="command")

    inspect_parser = subparsers.add_parser("inspect", help="Inspect metadata and print JSON.")
    inspect_parser.add_argument(
        "file",
        help=f"Path to a supported file ({_supported_extensions_text()}).",
    )
    inspect_parser.set_defaults(func=_handle_inspect)

    preview_parser = subparsers.add_parser("preview", help="Generate and save a PNG preview.")
    preview_parser.add_argument(
        "file",
        help=f"Path to a supported file ({_supported_extensions_text()}).",
    )
    preview_parser.add_argument(
        "--plane",
        choices=("axial", "coronal", "sagittal"),
        default=None,
        help="NIfTI only. Defaults to axial when omitted.",
    )
    preview_parser.add_argument(
        "--dataset",
        default=None,
        help="HDF5 only. Dataset path, for example data/subject01/run1/bold.",
    )
    preview_parser.add_argument(
        "--axis",
        type=int,
        default=None,
        help="HDF5 only. Slice axis for 3D datasets (0, 1, or 2).",
    )
    preview_parser.add_argument(
        "--slice",
        dest="slice_index",
        type=int,
        default=None,
        help="Slice index. If omitted, the center slice is used.",
    )
    preview_parser.add_argument(
        "--output",
        required=True,
        help="Output PNG file path.",
    )
    preview_parser.set_defaults(func=_handle_preview)

    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for python -m voxelkit.cli."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 1

    try:
        args.func(args)
        return 0
    except (ValidationError, FileNotFoundError, ValueError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
