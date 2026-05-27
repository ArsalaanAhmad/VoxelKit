"""Typed Protocol contract for the three callables every format must provide.

Every supported file format in VoxelKit is exposed through three CLI-level
callables: one for `inspect`, one for `preview`, and one for `report`. The
Protocol classes in this module pin down their signatures so that contributors
adding a new format can rely on a single, documented contract — and so the
runtime registration path (`FormatRoute.__post_init__`) can reject mistakes
before they reach end users.

The library-level functions (e.g. `voxelkit.nifti.preview.preview`) have
richer signatures with format-specific keyword arguments. The Protocols below
describe the *CLI adapters* — thin wrappers that translate an
`argparse.Namespace` into the keyword arguments those library functions need.
See `voxelkit/templates/format_template.py` for a worked skeleton.
"""

from __future__ import annotations

import argparse
import inspect
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class InspectFn(Protocol):
    """Signature: `(file_path: str) -> dict[str, Any]`.

    Reads metadata for a single file and returns it as a JSON-serialisable
    dictionary. Must not load pixel data unless the format makes that cheap.
    """

    def __call__(self, file_path: str) -> dict[str, Any]: ...


@runtime_checkable
class PreviewFn(Protocol):
    """Signature: `(file_path: str, args: argparse.Namespace) -> bytes`.

    Returns PNG-encoded preview bytes for the file. The `args` namespace
    carries CLI flags such as `--slice`, `--plane`, `--dataset`; the adapter
    is responsible for translating them into the library function's kwargs
    and for rejecting flags that do not apply to this format.
    """

    def __call__(self, file_path: str, args: argparse.Namespace) -> bytes: ...


@runtime_checkable
class ReportFn(Protocol):
    """Signature: `(file_path: str, args: argparse.Namespace) -> dict[str, Any]`.

    Returns the QA-report dictionary for the file. Same `args`-handling
    contract as `PreviewFn`.
    """

    def __call__(self, file_path: str, args: argparse.Namespace) -> dict[str, Any]: ...


class FormatHandler(Protocol):
    """Composite Protocol: an object that carries one of each callable.

    `FormatRoute` is the canonical concrete implementation. Contributors do
    not subclass this Protocol directly — instead, they construct a
    `FormatRoute` with three callables that conform to `InspectFn`,
    `PreviewFn`, and `ReportFn`, and `FormatRoute.__post_init__` checks the
    structural fit.
    """

    inspect_fn: InspectFn
    preview_fn: PreviewFn
    report_fn: ReportFn


def _count_required_positional(fn: object) -> int | None:
    """Return the number of required positional args, or None if introspection fails.

    Returns None for built-in or C-implemented callables whose signature
    `inspect.signature` cannot parse — those are accepted without validation
    rather than rejected, on the assumption that mismatches will surface at
    call time anyway.
    """
    try:
        sig = inspect.signature(fn)
    except (TypeError, ValueError):
        return None

    required = 0
    for parameter in sig.parameters.values():
        if parameter.kind in (
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        ) and parameter.default is inspect.Parameter.empty:
            required += 1
    return required


def validate_handler_signatures(
    *,
    inspect_fn: object,
    preview_fn: object,
    report_fn: object,
) -> None:
    """Raise TypeError when any callable does not match its Protocol arity.

    This is a lightweight structural check, not a full type check — it
    verifies each value is callable and accepts the expected number of
    required positional arguments. Static type-checkers (mypy/pyright) cover
    the deeper contract via the Protocol classes above.
    """
    _check_callable_arity(inspect_fn, label="inspect_fn", expected_required=1)
    _check_callable_arity(preview_fn, label="preview_fn", expected_required=2)
    _check_callable_arity(report_fn, label="report_fn", expected_required=2)


def _check_callable_arity(fn: object, *, label: str, expected_required: int) -> None:
    if not callable(fn):
        raise TypeError(
            f"FormatRoute {label} must be callable; got {type(fn).__name__}."
        )

    required = _count_required_positional(fn)
    if required is None:
        return

    if required > expected_required:
        raise TypeError(
            f"FormatRoute {label} requires {required} positional arguments, "
            f"but its Protocol expects at most {expected_required}."
        )
