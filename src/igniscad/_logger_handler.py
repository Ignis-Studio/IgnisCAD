"""
A simple wrapper for logging.
"""

import logging

logger = {}

def setup(identifier: str) -> None:
    """
    Used in *__init__.py* when the package is imported.
    Initialize the global logger.
    Args:
        identifier (str): __name__ of the package.
    """
    global logger
    package_logger = logging.getLogger(identifier)
    package_logger.addHandler(logging.NullHandler())
    logger[identifier] = package_logger
    return

def init_sub_logger(identifier: str) -> logging.Logger:
    """
    Initialize the logger for a new submodule.
    """
    global logger
    sub = logging.getLogger(identifier)
    logger[identifier] = sub
    return sub

def get_logger(identifier: str) -> logging.Logger:
    """
    Grab logger for a specified identifier.
    """
    global logger
    return logger[identifier]
