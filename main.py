import sys
from pathlib import Path
import multiprocessing

from src.webview2 import WebView2


if __name__ == '__main__':
    if sys.platform == "win32":
        multiprocessing.freeze_support()

    if getattr(sys, "frozen", False):
        main_path = Path(sys.executable).parent.absolute()
    else:
        main_path = (Path(__file__).parent.parent / "dist").absolute()

    webviwe = WebView2(main_path)
    webviwe.start()
