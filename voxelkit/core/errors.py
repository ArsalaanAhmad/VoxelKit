class UnsupportedFormatError(ValueError):
    """Raised when an input file extension does not match expected format(s)."""


class ValidationError(ValueError):
    """Raised when user-provided inputs fail validation checks."""
