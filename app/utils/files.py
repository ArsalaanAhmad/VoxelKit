from __future__ import annotations

import os
import tempfile

from fastapi import UploadFile

from app.middleware import MAX_UPLOAD_BYTES, MAX_UPLOAD_MB
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


_CHUNK = 1024 * 1024  # 1 MB read chunks


async def save_upload_to_temp(file: UploadFile, suffix: str) -> str:
    """Stream uploaded content to a temporary file, enforcing the size cap.

    Raises:
        ValueError: If the upload is empty or exceeds MAX_UPLOAD_BYTES.
    """
    temp_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_path = tmp.name
            total = 0
            while True:
                chunk = await file.read(_CHUNK)
                if not chunk:
                    break
                total += len(chunk)
                if total > MAX_UPLOAD_BYTES:
                    raise ValueError(
                        f"Upload exceeds the {MAX_UPLOAD_MB} MB limit."
                    )
                tmp.write(chunk)
        if total == 0:
            raise ValueError("Uploaded file is empty.")
        return temp_path
    except Exception:
        if temp_path:
            try:
                os.remove(temp_path)
            except FileNotFoundError:
                pass
        raise
