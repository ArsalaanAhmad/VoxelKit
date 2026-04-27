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

import h5py

from voxelkit import report_batch as report_batch_library
from voxelkit.core.errors import ValidationError
from voxelkit.core.formats import (
    HDF5_EXTENSIONS,
    NIFTI_EXTENSIONS,
    NUMPY_EXTENSIONS,
    TIFF_EXTENSIONS,
    detect_format,
)
from voxelkit.h5 import inspect_h5, preview as preview_h5
from voxelkit.h5 import report as report_h5
from voxelkit.nifti import inspect as inspect_nifti
from voxelkit.nifti import preview as preview_nifti
from voxelkit.nifti import report as report_nifti
from voxelkit.npy import inspect as inspect_npy
from voxelkit.npy import preview as preview_npy
from voxelkit.npy import report as report_npy
from voxelkit.tiff import inspect as inspect_tiff
from voxelkit.tiff import preview as preview_tiff
from voxelkit.tiff import report as report_tiff
from voxelkit.embedding import report as report_embedding
from voxelkit.embedding import preview as preview_embedding


InspectFn = Callable[[str], dict[str, Any]]
PreviewFn = Callable[[str, argparse.Namespace], bytes]
ReportFn = Callable[[str, argparse.Namespace], dict[str, Any]]


@dataclass(frozen=True)
class FormatRoute:
    """Routing metadata for one supported file format."""

    name: str
    extensions: tuple[str, ...]
    inspect_fn: InspectFn
    preview_fn: PreviewFn
    report_fn: ReportFn


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
    if args.array_name is not None:
        raise ValidationError("--array is only valid for NumPy NPZ preview/report.")
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
    if args.array_name is not None:
        raise ValidationError("--array is only valid for NumPy NPZ preview/report.")
    if args.plane is not None:
        raise ValidationError("--plane is only valid for NIfTI preview.")

    axis = _resolve_h5_axis(file_path=file_path, dataset_path=args.dataset, axis=args.axis)

    return preview_h5(
        file_path=file_path,
        dataset_path=args.dataset,
        axis=axis,
        slice_index=args.slice_index,
    )


def _report_nifti(file_path: str, args: argparse.Namespace) -> dict[str, Any]:
    """Run NIfTI report with CLI arguments."""
    if args.dataset is not None:
        raise ValidationError("--dataset is only valid for HDF5 report.")
    if args.array_name is not None:
        raise ValidationError("--array is only valid for NumPy NPZ preview/report.")
    return report_nifti(file_path)


def _report_h5(file_path: str, args: argparse.Namespace) -> dict[str, Any]:
    """Run HDF5 report with CLI arguments."""
    if args.array_name is not None:
        raise ValidationError("--array is only valid for NumPy NPZ preview/report.")
    return report_h5(file_path, dataset_path=args.dataset)


def _preview_npy(file_path: str, args: argparse.Namespace) -> bytes:
    """Run NumPy preview with CLI arguments."""
    if args.dataset is not None:
        raise ValidationError("--dataset is only valid for HDF5 preview/report.")
    if args.plane is not None:
        raise ValidationError("--plane is only valid for NIfTI preview.")

    axis = 0 if args.axis is None else args.axis
    return preview_npy(
        file_path=file_path,
        array_name=args.array_name,
        axis=axis,
        slice_index=args.slice_index,
    )


def _report_npy(file_path: str, args: argparse.Namespace) -> dict[str, Any]:
    """Run NumPy report with CLI arguments."""
    if args.dataset is not None:
        raise ValidationError("--dataset is only valid for HDF5 preview/report.")
    return report_npy(file_path, array_name=args.array_name)


def _preview_tiff(file_path: str, args: argparse.Namespace) -> bytes:
    """Run TIFF preview with CLI arguments.

    TIFF does not use --plane (NIfTI only), --dataset (HDF5 only), or
    --array (NumPy NPZ only). Both --axis and --slice are accepted for 3D
    z-stack TIFFs; they are silently ignored for 2D single-page images.
    """
    if args.plane is not None:
        raise ValidationError("--plane is only valid for NIfTI preview.")
    if args.dataset is not None:
        raise ValidationError("--dataset is only valid for HDF5 preview.")
    if args.array_name is not None:
        raise ValidationError("--array is only valid for NumPy NPZ preview/report.")

    axis = 0 if args.axis is None else args.axis
    return preview_tiff(
        file_path=file_path,
        axis=axis,
        slice_index=args.slice_index,
    )


def _report_tiff(file_path: str, args: argparse.Namespace) -> dict[str, Any]:
    """Run TIFF report with CLI arguments."""
    if args.dataset is not None:
        raise ValidationError("--dataset is only valid for HDF5 preview/report.")
    if args.array_name is not None:
        raise ValidationError("--array is only valid for NumPy NPZ preview/report.")
    return report_tiff(file_path)


def _resolve_h5_axis(file_path: str, dataset_path: str, axis: int | None) -> int:
    """Resolve HDF5 axis rules: optional for 2D, required for 3D."""
    if axis is not None:
        return axis

    try:
        with h5py.File(file_path, "r") as h5_file:
            if dataset_path not in h5_file:
                raise ValidationError(f"dataset_path not found: '{dataset_path}'.")

            node = h5_file[dataset_path]
            if isinstance(node, h5py.Group):
                raise ValidationError(f"dataset_path '{dataset_path}' points to a group, not a dataset.")

            if not isinstance(node, h5py.Dataset):
                raise ValidationError(f"dataset_path '{dataset_path}' is not a valid dataset.")

            if node.ndim == 2:
                # Axis is ignored for 2D datasets by the library preview path.
                return 0

            if node.ndim == 3:
                raise ValidationError("--axis is required for 3D HDF5 datasets.")
    except OSError as exc:
        raise ValidationError("Invalid, corrupted, or unreadable HDF5 file.") from exc

    # For unsupported ndim cases, forward to the library preview validation path.
    return 0


def _register_builtin_formats() -> None:
    """Register VoxelKit's built-in formats in one place."""
    register_format(
        FormatRoute(
            name="nifti",
            extensions=NIFTI_EXTENSIONS,
            inspect_fn=inspect_nifti,
            preview_fn=_preview_nifti,
            report_fn=_report_nifti,
        )
    )
    register_format(
        FormatRoute(
            name="hdf5",
            extensions=HDF5_EXTENSIONS,
            inspect_fn=inspect_h5,
            preview_fn=_preview_h5,
            report_fn=_report_h5,
        )
    )
    register_format(
        FormatRoute(
            name="numpy",
            extensions=NUMPY_EXTENSIONS,
            inspect_fn=inspect_npy,
            preview_fn=_preview_npy,
            report_fn=_report_npy,
        )
    )
    register_format(
        FormatRoute(
            name="tiff",
            extensions=TIFF_EXTENSIONS,
            inspect_fn=inspect_tiff,
            preview_fn=_preview_tiff,
            report_fn=_report_tiff,
        )
    )


_register_builtin_formats()


def _resolve_route(file_path: str) -> FormatRoute:
    """Return the registered CLI route that matches a file path.

    Raises:
        ValidationError: If no route matches the file extension.
    """
    try:
        detected_format = detect_format(file_path)
    except ValueError:
        supported = ", ".join(ext for route in FORMAT_ROUTES for ext in route.extensions)
        raise ValidationError(f"Unsupported file extension. Supported extensions: {supported}") from None

    for route in FORMAT_ROUTES:
        if route.name == detected_format:
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


def _handle_report(args: argparse.Namespace) -> None:
    """Handle the report command and print JSON."""
    route = _resolve_route(args.file)
    result = route.report_fn(args.file, args)
    print(json.dumps(result, indent=2))


def _handle_report_batch(args: argparse.Namespace) -> None:
    """Handle the report-batch command and emit JSON output."""
    result = report_batch_library(path=args.directory, recursive=args.recursive)
    rendered_json = json.dumps(result, indent=2)

    if args.output is None:
        print(rendered_json)
        return

    output_path = Path(args.output)
    if output_path.parent and not output_path.parent.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(rendered_json, encoding="utf-8")
    print(f"Wrote batch report JSON: {output_path}")


def _handle_embed_report(args: argparse.Namespace) -> None:
    """Handle the embed-report command and print embedding QA JSON."""
    result = report_embedding(args.file)
    print(json.dumps(result, indent=2))


def _handle_embed_preview(args: argparse.Namespace) -> None:
    """Handle the embed-preview command and write a heatmap PNG to disk."""
    png_bytes = preview_embedding(
        file_path=args.file,
        max_samples=args.max_samples,
    )

    output_path = Path(args.output)
    if output_path.parent and not output_path.parent.exists():
        output_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_bytes(png_bytes)
    print(f"Wrote embedding heatmap PNG: {output_path}")


def _handle_gui(_args: argparse.Namespace) -> None:
    """Handle the gui command and launch the optional local Streamlit app."""
    from voxelkit.gui import GUI_MISSING_DEPENDENCY_MESSAGE, run_gui

    try:
        exit_code = run_gui()
    except ModuleNotFoundError as exc:
        raise ValidationError(GUI_MISSING_DEPENDENCY_MESSAGE) from exc

    if exit_code != 0:
        raise ValidationError(f"GUI process exited with code {exit_code}.")


def build_parser() -> argparse.ArgumentParser:
    """Build and return the CLI parser."""
    parser = argparse.ArgumentParser(
        prog="voxelkit",
        description="Inspect, preview, and report on NIfTI/HDF5 imaging files.",
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
        "--array",
        dest="array_name",
        default=None,
        help="NumPy NPZ only. Array name inside the archive.",
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

    report_parser = subparsers.add_parser("report", help="Generate a QA report and print JSON.")
    report_parser.add_argument(
        "file",
        help=f"Path to a supported file ({_supported_extensions_text()}).",
    )
    report_parser.add_argument(
        "--dataset",
        default=None,
        help="HDF5 only. Optional dataset path. If omitted, first dataset is used.",
    )
    report_parser.add_argument(
        "--array",
        dest="array_name",
        default=None,
        help="NumPy NPZ only. Array name inside the archive.",
    )
    report_parser.set_defaults(func=_handle_report)

    report_batch_parser = subparsers.add_parser(
        "report-batch",
        help="Generate QA reports for supported files in a directory.",
    )
    report_batch_parser.add_argument("directory", help="Directory path to scan for supported files.")
    report_batch_parser.add_argument(
        "--no-recursive",
        dest="recursive",
        action="store_false",
        help="Disable recursive directory traversal.",
    )
    report_batch_parser.add_argument(
        "--output",
        default=None,
        help="Optional output JSON file path.",
    )
    report_batch_parser.set_defaults(func=_handle_report_batch, recursive=True)

    embed_report_parser = subparsers.add_parser(
        "embed-report",
        help="Generate an embedding-aware QA report for a .npy feature matrix.",
    )
    embed_report_parser.add_argument(
        "file",
        help="Path to a .npy file containing a 2D (N_samples, D_dims) array.",
    )
    embed_report_parser.set_defaults(func=_handle_embed_report)

    embed_preview_parser = subparsers.add_parser(
        "embed-preview",
        help="Render a .npy embedding matrix as a per-column-normalised PNG heatmap.",
    )
    embed_preview_parser.add_argument(
        "file",
        help="Path to a .npy file containing a 2D (N_samples, D_dims) array.",
    )
    embed_preview_parser.add_argument(
        "--max-samples",
        dest="max_samples",
        type=int,
        default=256,
        help="Maximum number of sample rows to render. Defaults to 256.",
    )
    embed_preview_parser.add_argument(
        "--output",
        required=True,
        help="Output PNG file path.",
    )
    embed_preview_parser.set_defaults(func=_handle_embed_preview)

    gui_parser = subparsers.add_parser(
        "gui",
        help="Launch the optional local/offline Streamlit GUI prototype.",
    )
    gui_parser.set_defaults(func=_handle_gui)

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

