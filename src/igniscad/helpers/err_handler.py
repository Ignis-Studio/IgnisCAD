"""
Custom error handler that silences the connection aborted errors.
"""

import socketserver, sys

_original_handle_error = socketserver.BaseServer.handle_error

def wrap_handlers() -> None:
    """
    Bind the custom error handler.
    """
    global _original_handle_error
    socketserver.BaseServer.handle_error = _silent_handle_error


def _silent_handle_error(self, request, client_address) -> None:
    """
    Custom error handler that silences the connection aborted errors.
    """
    exc_type, exc_value, _ = sys.exc_info()

    if isinstance(exc_value, (ConnectionAbortedError, BrokenPipeError)):
        return

    _original_handle_error(self, request, client_address)

    return
