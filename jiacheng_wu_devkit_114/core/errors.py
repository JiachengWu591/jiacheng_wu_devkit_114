# -*- coding: utf-8 -*-
"""
Domain error classes for devkit.

All business logic errors (bad input, incompatible formats, file conflicts, etc.) inherit from
DevkitError and are caught by the CLI layer to produce user-friendly error messages.
"""


class DevkitError(Exception):
    """Base class for all devkit domain errors (user/data issues, not bugs)."""

    pass


class ConversionError(DevkitError):
    """Raised when data format conversion fails (incompatible structures, unsupported formats, etc)."""

    pass


class BatchError(DevkitError):
    """Raised when batch file operations fail (glob conflicts, naming collisions, permission issues, etc)."""

    pass


class LogParseError(DevkitError):
    """Raised when log file parsing or filtering fails (malformed input, bad regex, etc)."""

    pass
