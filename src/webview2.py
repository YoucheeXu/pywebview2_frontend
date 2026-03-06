"""
PyWebView2 window manager for Vue3+TS frontend integration.

This class handles window creation, lifecycle management, and communication with the
Vue3 frontend (e.g., sending commands from Python to Vue). It delegates command
processing to the isolated WindowAPI class.
"""

from pathlib import Path
import json
import mimetypes
import webview
from src.window_api import WindowAPI  # Import the isolated WindowAPI


class WebView2:
    """PyWebView2 window manager for Vue3+TS applications.

    Responsibilities:
        - Create and configure PyWebView2 windows
        - Manage window lifecycle (start, stop)
        - Handle communication from Python to Vue3 frontend
        - Delegate frontend command processing to WindowAPI
    """

    def __init__(self, main_path: Path):
        """Initialize WebView2 manager with the path to the Vue index.html.

        Args:
            main_path: Path to the directory containing index.html (Vue build folder).
        """
        self._url: str = str(main_path / "index.html")
        self._window: webview.Window | None = None
        self._window_api: WindowAPI | None = None  # Isolated API instance

    def send_command_to_vue(self, command: str, **params: object) -> None:
        """Send commands from Python to Vue3 frontend (with optional parameters).

        Args:
            command: Command identifier (frontend's `handlePythonCommand` will receive this).
            **params: Optional key-value parameters to send to the frontend.

        Raises:
            AssertionError: If the window instance is not initialized.
            Exception: If JS evaluation or JSON serialization fails.
        """
        assert self._window is not None, "Window instance is not initialized"

        try:
            # Serialize parameters to JSON (safe cross-language transfer)
            params_json = json.dumps(params)

            # JS code to call frontend's global `handlePythonCommand` function
            js_code = f"""
                if (window.handlePythonCommand) {{
                    window.handlePythonCommand('{command}', {params_json});
                }} else {{
                    console.error('Frontend function handlePythonCommand not found');
                }}
            """

            # Execute JS in the window
            self._window.evaluate_js(js_code)
            print(f"Sent command to Vue3: {command}, params={params}")

        except Exception as e:
            print(f"Failed to send command to Vue3: {str(e)}")

    def log(self, msg: str, level: str = "log") -> None:
        """Log messages to the frontend's browser console.

        Args:
            msg: Message to log.
            level: Console log level (log/error/warn/info).

        Raises:
            AssertionError: If the window instance is not initialized.
        """
        assert self._window is not None, "Window instance is not initialized"
        self._window.evaluate_js(f"console.{level}({msg})")

    def _create_window(self, url: str, width: int, height: int) -> webview.Window:
        """Internal method to create a PyWebView2 window with fixed configuration.

        Fixes white-screen issues in packaged apps and sets window style/behavior.

        Args:
            url: Path/URL to the Vue index.html file.
            width: Initial window width (pixels).
            height: Initial window height (pixels).

        Returns:
            webview.Window: Configured PyWebView2 window instance.
        """
        print(f"Creating window with URL: {url}")

        # Fix white-screen issue in packaged apps (MIME type for JS)
        mimetypes.add_type('application/javascript', '.js')

        # Create window with fixed settings
        window = webview.create_window(
            title='PyWebView 6.1 + Vue3 + TS GUI',
            url=url,
            width=width,
            height=height,
            easy_drag=True,
            frameless=True,
            resizable=False
        )

        return window

    def start(self) -> None:
        """Start the PyWebView2 window and expose the isolated WindowAPI to frontend.

        This method:
            1. Creates the window instance
            2. Initializes the isolated WindowAPI
            3. Exposes the API's `invoke` method to the frontend
            4. Starts the PyWebView2 event loop
        """
        # Create window
        self._window = self._create_window(self._url, 800, 600)

        # Initialize isolated WindowAPI (delegate command handling)
        self._window_api = WindowAPI(self._window)

        # Expose ONLY the WindowAPI's invoke method to the frontend
        self._window.expose(self._window_api.invoke)

        # Start PyWebView2 with debug mode
        webview.start(debug=True)
