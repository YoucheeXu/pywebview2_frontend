import sys
from pathlib import Path
import mimetypes
import time
from threading import Thread

import webview


# 定义 API 类
class Api:
    def hello(self, name: str) -> str:
        """前端调用的方法：接收参数并返回结果"""
        return f'你好 {name}！我是 Python 后端（pywebview 6.1）'

    def send_message_to_frontend(self, window: webview.Window):
        """Python 主动向前端推送消息（6.1 最简方案）"""
        time.sleep(3)  # 模拟延迟
        message = '这是 Python 主动发送的消息（6.1版本）！'
        
        # 关键：直接调用前端定义的全局回调函数 handlePythonMessage
        # 避免使用废弃的 window.pywebview.on 方法
        window.evaluate_js(f"""
            if (window.handlePythonMessage) {{
                window.handlePythonMessage('{message}');
            }}
        """)

# 初始化 pywebview 窗口
def create_window():
    # 1. 实例化 API 类
    api = Api()

    # 2. 判断环境，确定加载的 URL
    is_dev = False  # 开发时设为 True，打包前改为 False
    if is_dev:
        # 开发环境：加载 Vue 开发服务器
        url = 'http://127.0.0.1:5173'
    else:
        # 生产环境：加载打包后的静态文件（绝对路径）
        # current_dir = os.path.dirname(os.path.abspath(__file__))
        # url = os.path.abspath(os.path.join(current_dir, '../dist/index.html'))
        if getattr(sys, "frozen", False):
            proj_path = Path(sys.executable).parent.absolute()
        else:
            proj_path = (Path(__file__).parent.parent / "dist").absolute()
        url = proj_path / "index.html"
        print(f"url = {url}")
        # 修复某些情况下，打包后软件打开白屏的问题
        mimetypes.add_type('application/javascript', '.js')

    # index_html_url = f'file:///{url.replace("\\", "/")}'
    # 3. 创建 WebView2 窗口
    window = webview.create_window(
        title='PyWebView 6.1 + Vue3 + TS GUI',
        url=str(url),
        width=701+16,
        height=548+36,
        easy_drag=True,
        frameless=True,
        resizable=False
    )

    # 4. 暴露 API 方法给前端（6.1 位置参数传方法对象）
    assert window is not None
    window.expose(api.hello)

    # 5. 启动线程：Python 主动向前端发消息
    Thread(target=api.send_message_to_frontend, args=(window,), daemon=True).start()

    # 6. 启动时指定调试模式
    webview.start(debug=True)


if __name__ == '__main__':
    create_window()
