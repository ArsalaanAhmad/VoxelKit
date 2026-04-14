from voxelkit.core.errors import UnsupportedFormatError, ValidationError


def has_supported_extension(file_path: str, extensions: tuple[str, ...]) -> bool:
    """Return True when file_path ends with one of the provided extensions."""
    return file_path.lower().endswith(extensions)


def require_supported_extension(
    file_path: str,
    extensions: tuple[str, ...],
    message: str,
) -> None:
    """Validate file extension and raise UnsupportedFormatError when invalid."""
    if not has_supported_extension(file_path, extensions):
        raise UnsupportedFormatError(message)


def require_min_ndim(ndim: int, min_ndim: int, message: str) -> None:
    """Validate minimum dimensionality and raise ValidationError when invalid."""
    if ndim < min_ndim:
        raise ValidationError(message)


def resolve_slice_index(length: int, slice_index: int | None, context: str) -> int:
    """Resolve optional slice index and validate bounds for the given axis context."""
    if length <= 0:
        raise ValidationError(f"No data available for {context}.")

    resolved = length // 2 if slice_index is None else slice_index
    max_index = length - 1

    if resolved < 0 or resolved > max_index:
        raise ValidationError(
            f"slice_index out of bounds for {context}. Valid range: 0 to {max_index}."
        )

    return resolved
