"""
Window API for handling frontend command invocations in PyWebView2.

This class encapsulates all logic for processing commands sent from the Vue3 frontend
(e.g., resize, minimize, quit), decoupling command handling from window management.
"""
import os
import sys
from typing import cast
import webview


class WindowAPI:
    """API class to process frontend commands for PyWebView2 window manipulation.

    Responsibilities:
        - Handle command invocations from the Vue3 frontend (resize, minimize, move, etc.)
        - Validate commands and parameters
        - Execute window operations and return standardized responses
        - Track window position for drag-to-move functionality
    """

    def __init__(self, window: webview.Window):
        """Initialize WindowAPI with a PyWebView2 window instance.

        Args:
            window: Active PyWebView2 window instance to manipulate.
        """
        self._window: webview.Window = window

    def invoke(self, idmsg: str, *args: object):
        """Process frontend commands and execute corresponding window operations.

        Supported commands:
            - resize (width: int, height: int): Resize window
            - minimize: Minimize window
            - quit: Close window
            - fullscreen: Toggle fullscreen
            - top (on_top: bool): Toggle always-on-top
            - moveWindow (delta_x: int, delta_y: int): Move window by offset (drag-to-move)
            - restart: Restart the entire application

        Args:
            idmsg: Command identifier (e.g., "resize", "minimize", "quit").
            *args: Variable arguments for the command:
                - moveWindow: (delta_x: int, delta_y: int) - relative offset from current position
                - resize: (width: int, height: int)
                - top: (on_top: bool)

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

            case "moveWindow":
                # Handle window drag-to-move (delta_x: relative X offset, delta_y: relative Y offset)
                delta_x = cast(int, args[0])
                delta_y = cast(int, args[1])

                # Calculate new absolute position
                target_x = self._window.x + delta_x
                target_y = self._window.y + delta_y

                # Move window to new position
                self._window.move(target_x, target_y)
                print(f"Moved window to: X={self._window.x}, Y={self._window.y}")

            case "minimize":
                self._window.minimize()

            case "quit":
                self._window.destroy()

            case "fullscreen":
                self._window.toggle_fullscreen()

            case "top":
                on_top = cast(bool, args[0])
                self._window.on_top = on_top

            case "restart":
                print("Initiating application restart...")
                # 1. Close ALL pywebview windows (stops the GUI loop)
                for window in webview.windows:
                    window.destroy()
                # 2. Atomic restart: replace current process with a fresh instance
                try:
                    os.execv(sys.executable, [sys.executable] + sys.argv)
                except Exception as e:
                    print(f"Restart failed: {str(e)}")
                    sys.exit(1)

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
