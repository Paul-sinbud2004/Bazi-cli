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

    from ui import theme
    from ui.main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("命理精研")
    app.setOrganizationName("destiny_cn")
    app.setStyleSheet(theme.QSS)
    win = MainWindow()
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
