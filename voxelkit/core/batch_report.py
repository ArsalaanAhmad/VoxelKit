"""Directory-level batch reporting built on top of report_file()."""

from collections import Counter
from pathlib import Path

from voxelkit.core.errors import ValidationError
from voxelkit.core.types import (
    BatchAggregateSummary,
    BatchFailureItem,
    BatchFileReportResult,
    BatchReportResult,
)


SUPPORTED_BATCH_EXTENSIONS = (".nii", ".nii.gz", ".h5", ".hdf5")


def _discover_files(root_path: Path, recursive: bool) -> list[Path]:
    """Return discovered regular files under root_path."""
    iterator = root_path.rglob("*") if recursive else root_path.glob("*")
    return sorted(path for path in iterator if path.is_file())


def _is_supported_file(path: Path) -> bool:
    """Return True when path extension is supported for reporting."""
    lowered = path.name.lower()
    return lowered.endswith(SUPPORTED_BATCH_EXTENSIONS)


def _shape_to_string(shape: list[int]) -> str:
    """Convert shape list to compact JSON-friendly string."""
    if not shape:
        return "scalar"
    return "x".join(str(dimension) for dimension in shape)


def _build_aggregate_summary(file_reports: list[BatchFileReportResult]) -> BatchAggregateSummary:
    """Build aggregate summary metrics from successful file reports."""
    count_by_format: Counter[str] = Counter()
    warning_counts: Counter[str] = Counter()
    unique_shapes: set[str] = set()
    files_with_warnings = 0

    for report in file_reports:
        count_by_format[report["format"]] += 1
        unique_shapes.add(_shape_to_string(report["shape"]))

        warnings = report["warnings"]
        if warnings:
            files_with_warnings += 1
            for warning in warnings:
                warning_counts[warning] += 1

    return {
        "count_by_format": dict(sorted(count_by_format.items())),
        "unique_shapes": sorted(unique_shapes),
        "files_with_warnings": files_with_warnings,
        "warning_counts": dict(sorted(warning_counts.items())),
    }


def report_batch(path: str, recursive: bool = True) -> BatchReportResult:
    """Run report_file() over supported files in a directory and aggregate results."""
    root_path = Path(path)
    if not root_path.exists():
        raise ValidationError(f"Path does not exist: {path}")
    if not root_path.is_dir():
        raise ValidationError(f"Path is not a directory: {path}")

    all_files = _discover_files(root_path, recursive=recursive)
    supported_files = [file_path for file_path in all_files if _is_supported_file(file_path)]

    # Local import avoids circular import while still using the public dispatcher.
    from voxelkit import report_file

    file_reports: list[BatchFileReportResult] = []
    failures: list[BatchFailureItem] = []

    for file_path in supported_files:
        normalized_path = str(file_path)
        try:
            single_report = report_file(normalized_path)
            file_reports.append({"file_path": normalized_path, **single_report})
        except (ValidationError, ValueError, OSError) as exc:
            failures.append(
                {
                    "file_path": normalized_path,
                    "error": str(exc),
                }
            )

    return {
        "root_path": str(root_path.resolve()),
        "recursive": recursive,
        "total_files_found": len(all_files),
        "supported_files_found": len(supported_files),
        "successful_reports": len(file_reports),
        "failed_reports": len(failures),
        "files": file_reports,
        "failures": failures,
        "aggregate": _build_aggregate_summary(file_reports),
    }
