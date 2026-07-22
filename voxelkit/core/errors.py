class UnsupportedFormatError(ValueError):
    """Raised when an input file extension does not match expected format(s)."""


class ValidationError(ValueError):
    """Raised when user-provided inputs fail validation checks."""


class ThresholdViolationError(Exception):
    """Raised when a QA report violates user-defined threshold constraints.

    Separated from ValidationError so the CLI can exit with a distinct code
    (3) that scripts can distinguish from a hard error (2).
    """
