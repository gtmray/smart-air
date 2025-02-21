import os
import logging


class RelativePathFormatter(logging.Formatter):
    """
    A custom logging formatter that converts absolute file paths to
    relative paths.

    This formatter attempts to convert the absolute file path in the log record
    to a path relative to the current working directory.

    If an error occurs during this conversion,
    the original absolute path is retained.

    Methods:
        format(record):
            Formats the specified log record as text.
            Converts the absolute file path in the log record to a relative
            path if possible.
    """

    def format(self, record):
        try:
            cwd = os.getcwd()
            record.pathname = os.path.relpath(record.pathname, cwd)
        except Exception:
            # If any error occurs, fallback to the original pathname.
            pass
        return super().format(record)
