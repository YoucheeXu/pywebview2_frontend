#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from pathlib import Path
import time
import json
# from threading import Thread
import mimetypes
from typing import cast

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

class WebView2:
    def __init__(self, main_path: Path):
        self._url: str = str(main_path / "index.html")
        # print(f"url = {self._url}")
        self._window: webview.Window | None =  None

    def invoke(self, idmsg: str, **kwargs: object):
        assert self._window is not None
        match idmsg:
            case "minimize":
                self._window.minimize()
            case "quit":
                self._window.destroy()
            case "fullscreen":
                self._window.toggle_fullscreen()
            case "top":
                on_top = cast(bool, kwargs["isTop"])
                self._window.on_top = on_top
            case _:
                # raise ValueError(f"don't konow how to {idmsg}")
                return {"code": 400,
                    "msg": f"unkown command: {idmsg}",
                    "params": kwargs
                }
        return {"code": 200,
            "msg": f"success to {idmsg}",
            "params": kwargs
        }

    def send_command_to_vue(self, command: str, **params: object):
        """ pywebview2主动向Vue3发送命令（带/不带参数）
        :param command: 命令名称（前端要接收的标识）
        :param params: 可选的命令参数
        """
        assert self._window is not None
        try:
            # 1. 构造要执行的JS代码：调用前端全局函数接收命令
            # 将参数序列化为JSON字符串，确保跨语言传递的正确性
            params_json = json.dumps(params)
            
            # 2. 执行前端的全局函数 `handlePythonCommand`（需在Vue3中定义）
            js_code = f"""
                if (window.handlePythonCommand) {{
                    window.handlePythonCommand('{command}', {params_json});
                }} else {{
                    console.error('未找到前端的handlePythonCommand函数');
                }}
            """

            # 3. 执行JS代码，实现主动发消息
            self._window.evaluate_js(js_code)
            print(f"已向Vue3发送命令：{command}，参数={params}")
            
        except Exception as e:
            print(f"向Vue3发送命令失败：{str(e)}")

    # 初始化 pywebview 窗口
    def _create_window(self, url: str, width: int, height: int):
 
        print(f"url = {url}")
        # 修复某些情况下，打包后软件打开白屏的问题
        mimetypes.add_type('application/javascript', '.js')

        # index_html_url = f'file:///{url.replace("\\", "/")}'
        # 3. 创建 WebView2 窗口
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

    def log(self, msg: str, level: str = "log"):
        assert self._window is not None
        self._window.evaluate_js(f"console.{level}({msg})")

    def start(self):
        self._window = self._create_window(self._url, 701+16, 548+36)

        assert self._window is not None

        # 4. 暴露 API 方法给前端（6.1 位置参数传方法对象）
        self._window.expose(self.invoke)

        # 5. 启动线程：Python 主动向前端发消息
        # Thread(target=api.send_message_to_frontend, args=(window,), daemon=True).start()

        # 6. 启动时指定调试模式
        webview.start(debug=True)
