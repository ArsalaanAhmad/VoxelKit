"""Render a `BatchReportResult` as a self-contained HTML document.

Self-contained means: one file, no external CSS/JS/network, thumbnails
embedded as base64 PNG data URIs. The HTML can be emailed, dropped onto
a colleague's machine, or attached to a ticket — no relative paths to
break.

The document layout:

  1. Header with the scanned root path, recursive flag, and run counters.
  2. Aggregate summary: format breakdown, distinct shapes, warning counts.
  3. Per-file grid — one card per successful report with thumbnail,
     statistics table, and warning chips. Warnings are highlighted.
  4. Failures table at the bottom for files that could not be opened.

Thumbnails are best-effort. When `preview_file` raises (unsupported
dimensionality, missing dataset path, etc.) the card renders without a
thumbnail and the rest of the report is unaffected.
"""

from __future__ import annotations

import base64
import html
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from voxelkit.core.types import BatchReportResult


_STYLE = """
:root {
  --bg: #ffffff;
  --fg: #1f2933;
  --muted: #6b7785;
  --card: #f7f9fc;
  --border: #e1e6ee;
  --accent: #00837a;
  --warn-bg: #fff8e1;
  --warn-fg: #6b5400;
  --warn-border: #f0d97a;
  --fail-bg: #fdecea;
  --fail-fg: #8b1c14;
  --fail-border: #f3b9b3;
  --ok-bg: #e7f4ef;
  --ok-fg: #115e4a;
}
* { box-sizing: border-box; }
body {
  margin: 0; padding: 2rem;
  font: 14px/1.5 -apple-system, "Segoe UI", Roboto, sans-serif;
  color: var(--fg); background: var(--bg);
}
h1 { font-size: 1.5rem; margin: 0 0 .25rem; }
h2 { font-size: 1.15rem; margin: 2rem 0 .75rem; }
.subtle { color: var(--muted); }
.meta { display: flex; flex-wrap: wrap; gap: 1.5rem; margin-bottom: 1.5rem; }
.meta-item { font-size: 13px; }
.meta-item .label { display: block; color: var(--muted); font-size: 11px; text-transform: uppercase; letter-spacing: .04em; }
.meta-item .value { font-weight: 600; }
table.summary { border-collapse: collapse; width: 100%; max-width: 600px; }
table.summary td { padding: 6px 12px; border-bottom: 1px solid var(--border); }
table.summary td.k { color: var(--muted); width: 50%; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
.card { background: var(--card); border: 1px solid var(--border); border-radius: 8px; padding: 12px; }
.card.has-warn { border-left: 4px solid var(--warn-border); }
.card .title { font-weight: 600; word-break: break-all; }
.card .path { font-size: 11px; color: var(--muted); word-break: break-all; margin-bottom: 8px; }
.card img.thumb { width: 100%; max-height: 220px; object-fit: contain; background: #000; border-radius: 4px; margin-bottom: 8px; image-rendering: pixelated; }
.card .no-thumb { display: flex; align-items: center; justify-content: center; height: 100px; background: #eef1f5; color: var(--muted); border-radius: 4px; margin-bottom: 8px; font-size: 12px; }
.stats { width: 100%; font-size: 12px; border-collapse: collapse; }
.stats td { padding: 2px 4px; }
.stats td.k { color: var(--muted); width: 45%; }
.warn-list { margin-top: 8px; display: flex; flex-wrap: wrap; gap: 4px; }
.chip { display: inline-block; padding: 2px 8px; font-size: 11px; border-radius: 999px; background: var(--warn-bg); color: var(--warn-fg); border: 1px solid var(--warn-border); }
.chip.ok { background: var(--ok-bg); color: var(--ok-fg); border-color: transparent; }
table.fails { width: 100%; border-collapse: collapse; font-size: 12px; }
table.fails th, table.fails td { text-align: left; padding: 8px; border-bottom: 1px solid var(--border); vertical-align: top; }
table.fails td.path { font-family: ui-monospace, monospace; word-break: break-all; }
.empty { color: var(--muted); font-style: italic; padding: 16px; background: var(--card); border-radius: 6px; border: 1px solid var(--border); }
""".strip()


def render_batch_report_html(batch_result: "BatchReportResult") -> str:
    """Render a BatchReportResult into a complete, standalone HTML string."""
    aggregate = batch_result["aggregate"]
    files = batch_result["files"]
    failures = batch_result["failures"]

    parts: list[str] = []
    parts.append("<!DOCTYPE html>")
    parts.append("<html lang=\"en\"><head><meta charset=\"utf-8\">")
    parts.append("<title>VoxelKit Batch QA Report</title>")
    parts.append(f"<style>{_STYLE}</style>")
    parts.append("</head><body>")

    parts.append("<h1>VoxelKit Batch QA Report</h1>")
    parts.append(f"<p class=\"subtle\">{html.escape(batch_result['root_path'])}</p>")

    parts.append("<div class=\"meta\">")
    parts.append(_meta_item("Recursive", "yes" if batch_result["recursive"] else "no"))
    parts.append(_meta_item("Files found", str(batch_result["total_files_found"])))
    parts.append(_meta_item("Supported", str(batch_result["supported_files_found"])))
    parts.append(_meta_item("Successful", str(batch_result["successful_reports"])))
    parts.append(_meta_item("Failed", str(batch_result["failed_reports"])))
    parts.append(_meta_item("With warnings", str(aggregate["files_with_warnings"])))
    parts.append("</div>")

    parts.append("<h2>Aggregate</h2>")
    parts.append("<table class=\"summary\">")
    parts.append(_summary_row("Formats", _render_counts(aggregate["count_by_format"])))
    parts.append(
        _summary_row(
            "Distinct shapes",
            ", ".join(html.escape(shape) for shape in aggregate["unique_shapes"]) or "—",
        )
    )
    parts.append(
        _summary_row(
            "Warning counts",
            _render_counts(aggregate["warning_counts"]) or "—",
        )
    )
    parts.append("</table>")

    parts.append("<h2>Per-file reports</h2>")
    if not files:
        parts.append("<div class=\"empty\">No successful reports.</div>")
    else:
        parts.append("<div class=\"grid\">")
        for record in files:
            parts.append(_render_file_card(record))
        parts.append("</div>")

    parts.append("<h2>Failures</h2>")
    if not failures:
        parts.append("<div class=\"empty\">No failures.</div>")
    else:
        parts.append("<table class=\"fails\">")
        parts.append("<tr><th>Path</th><th>Error</th></tr>")
        for failure in failures:
            parts.append(
                f"<tr><td class=\"path\">{html.escape(failure['file_path'])}</td>"
                f"<td>{html.escape(failure['error'])}</td></tr>"
            )
        parts.append("</table>")

    parts.append("</body></html>")
    return "\n".join(parts)


def _meta_item(label: str, value: str) -> str:
    return (
        f"<div class=\"meta-item\"><span class=\"label\">{html.escape(label)}</span>"
        f"<span class=\"value\">{html.escape(value)}</span></div>"
    )


def _summary_row(key: str, value_html: str) -> str:
    return f"<tr><td class=\"k\">{html.escape(key)}</td><td>{value_html}</td></tr>"


def _render_counts(counts: dict[str, int]) -> str:
    if not counts:
        return ""
    return ", ".join(f"{html.escape(key)} ({value})" for key, value in counts.items())


def _render_file_card(record) -> str:
    warnings = record.get("warnings") or []
    has_warn = "has-warn" if warnings else ""
    title = html.escape(record["filename"])
    path = html.escape(record["file_path"])
    thumbnail_html = _render_thumbnail(record["file_path"])

    stats_rows: list[str] = []
    for label, key in (
        ("format", "format"),
        ("shape", "shape"),
        ("dtype", "dtype"),
        ("min", "min"),
        ("max", "max"),
        ("mean", "mean"),
        ("std", "std"),
        ("nan", "nan_count"),
        ("inf", "inf_count"),
        ("zero %", "zero_fraction"),
    ):
        raw = record.get(key)
        if raw is None:
            value = "—"
        elif key == "zero_fraction":
            value = f"{raw * 100:.1f}%"
        elif key == "shape":
            value = "x".join(str(dim) for dim in raw) if raw else "scalar"
        elif isinstance(raw, float):
            value = f"{raw:.4g}"
        else:
            value = str(raw)
        stats_rows.append(
            f"<tr><td class=\"k\">{label}</td><td>{html.escape(value)}</td></tr>"
        )

    if warnings:
        chips = "".join(
            f"<span class=\"chip\">{html.escape(message)}</span>" for message in warnings
        )
    else:
        chips = "<span class=\"chip ok\">no warnings</span>"

    return (
        f"<div class=\"card {has_warn}\">"
        f"<div class=\"title\">{title}</div>"
        f"<div class=\"path\">{path}</div>"
        f"{thumbnail_html}"
        f"<table class=\"stats\">{''.join(stats_rows)}</table>"
        f"<div class=\"warn-list\">{chips}</div>"
        f"</div>"
    )


def _render_thumbnail(file_path: str) -> str:
    """Render a base64-embedded PNG thumbnail, or a placeholder on failure.

    The local import avoids a circular dependency between
    `voxelkit/__init__.py` (which imports this module's caller in the
    batch-report flow) and the format-specific preview modules.
    """
    try:
        from voxelkit import preview_file
        from voxelkit.core.formats import detect_format

        format_name = detect_format(file_path)
        # H5 previews need a dataset path that's not on the report record;
        # skip thumbnails for h5 to avoid surprising failures.
        if format_name == "hdf5":
            return "<div class=\"no-thumb\">no thumbnail (HDF5)</div>"

        png_bytes = preview_file(file_path)
        encoded = base64.b64encode(png_bytes).decode("ascii")
        return f"<img class=\"thumb\" alt=\"preview\" src=\"data:image/png;base64,{encoded}\">"
    except Exception:  # noqa: BLE001  — thumbnail failures must never break the report
        return "<div class=\"no-thumb\">no thumbnail</div>"
