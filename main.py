import sys
from pathlib import Path

from src.webview2 import WebView2


if __name__ == '__main__':
    if getattr(sys, "frozen", False):
        main_path = Path(sys.executable).parent.absolute()
    else:
        main_path = (Path(__file__).parent.parent / "dist").absolute()

    webviwe = WebView2(main_path)
    webviwe.start()
