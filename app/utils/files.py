from __future__ import annotations

import tempfile

from fastapi import UploadFile

from voxelkit.core.formats import first_matching_extension, has_extension


def ensure_filename(filename: str | None) -> str:
    """Return a non-empty filename or raise ValueError with a stable message."""
    if not filename:
        raise ValueError("Missing filename.")
    return filename


def require_upload_extension(
    filename: str | None,
    extensions: tuple[str, ...],
    message: str,
) -> str:
    """Validate upload filename extension and return normalized filename."""
    resolved = ensure_filename(filename)
    if not has_extension(resolved, extensions):
        raise ValueError(message)
    return resolved


def infer_temp_suffix(
    filename: str | None,
    extensions: tuple[str, ...],
    default_suffix: str,
) -> str:
    """Infer temp-file suffix from supported extensions, with fallback default."""
    if not filename:
        return default_suffix
    return first_matching_extension(filename, extensions) or default_suffix


async def save_upload_to_temp(file: UploadFile, suffix: str) -> str:
    """Persist uploaded content to a temporary file path.

    Raises:
        ValueError: If the upload content is empty.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        content = await file.read()
        if not content:
            raise ValueError("Uploaded file is empty.")
        temp_file.write(content)
        return temp_file.name
