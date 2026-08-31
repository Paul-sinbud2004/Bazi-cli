# -*- coding: utf-8 -*-
"""
命理精研 · 应用入口
===================
运行：python main.py（或打包后的可执行文件）
"""
from __future__ import annotations

import sys


def main() -> int:
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    app.setApplicationName("命理精研")
    app.setOrganizationName("destiny_cn")

    # 以下导入需在 QApplication 之后（字体探测依赖 QFontDatabase）
    from ui import theme
    from ui.main_window import MainWindow
    from utils.fontman import app_font

    # 字体初始化：探测系统优质中文字体（或用户自定义），全局应用
    theme.rebuild_qss()
    app.setStyleSheet(theme.QSS)
    f = app_font(theme.FONT_FAMILY, theme.FONT_SIZE)
    if f is not None:
        app.setFont(f)

    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
