"""
Function to create a (unique) logger
(object to log warnings, errors, etc.) for the `colibri` package.
"""

import logging
import sys

_logger: logging.Logger = None


def initialize_logger() -> logging.Logger:
    """Get the logger to write status messages

    Returns
    -------
    _logger : logging.Logger
        Logger to write status messages

    Raises
    ------
    None

    Examples
    --------
    >>> None
    """
    global _logger
    # Return the logger if it has already been created; otherwise, create it
    if _logger is None:
        # Since no name is given to the logger, it is root by default
        _logger = logging.getLogger(name="colibri_logger")
        # Formatter with template string
        formatter: logging.Formatter = logging.Formatter(
            "[%(asctime)s - %(pathname)s (L%(lineno)d) - %(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        # Specify handler - destination for the logging (standard output, file, network socket, etc.)
        stream_handler: logging.StreamHandler = logging.StreamHandler(
            sys.stdout
        )
        # Select what is shown
        stream_handler.setLevel(logging.DEBUG)
        # Set logger below subloggers
        _logger.setLevel(logging.DEBUG)
        # Add formatter
        stream_handler.setFormatter(formatter)
        # Add stream handler to logger
        _logger.addHandler(stream_handler)
    return _logger
