"""
Window API for handling frontend command invocations in PyWebView2.

This class encapsulates all logic for processing commands sent from the Vue3 frontend
(e.g., resize, minimize, quit), decoupling command handling from window management.
"""

from typing import cast
import webview


class WindowAPI:
    """API class to process frontend commands for PyWebView2 window manipulation.

    Responsibilities:
        - Handle command invocations from the Vue3 frontend (resize, minimize, etc.)
        - Validate commands and parameters
        - Execute window operations and return standardized responses
    """

    def __init__(self, window: webview.Window):
        """Initialize WindowAPI with a PyWebView2 window instance.

        Args:
            window: Active PyWebView2 window instance to manipulate.
        """
        self._window: webview.Window = window

    def invoke(self, idmsg: str, *args: object):
        """Process frontend commands and execute corresponding window operations.

        Args:
            idmsg: Command identifier (e.g., "resize", "minimize", "quit").
            *args: Variable arguments for the command (e.g., width/height for "resize").

        Returns:
            dict: Standardized response with status code, message, and data:
                - code: 200 (success) / 400 (unknown command)
                - msg: Human-readable status message
                - data: Original command arguments

        Raises:
            AssertionError: If the window instance is None (invalid state).
        """
        # Validate window is initialized
        assert self._window is not None, "Window instance is not initialized"

        # Log command invocation (for debugging)
        print(f"invoke {idmsg}: {args}")

        # Process command
        match idmsg:
            case "resize":
                width = cast(int, args[0])
                height = cast(int, args[1])
                self._window.resize(width, height)

            case "minimize":
                self._window.minimize()

            case "quit":
                self._window.destroy()

            case "fullscreen":
                self._window.toggle_fullscreen()

            case "top":
                on_top = cast(bool, args[0])
                self._window.on_top = on_top

            case _:
                # Return error response for unknown commands
                return {
                    "code": 400,
                    "msg": f"unknown command: {idmsg}",
                    "data": args
                }

        # Return success response for valid commands
        return {
            "code": 200,
            "msg": f"success to {idmsg}",
            "data": args
        }
