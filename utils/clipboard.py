# -*- coding: utf-8 -*-
"""
剪贴板工具（Qt 剪贴板封装）
============================
供"复制排盘结果 / 复制 AI 提示词"使用。
"""
from __future__ import annotations


def copy_text(text: str) -> bool:
    """
    复制文本到系统剪贴板。需要已存在 QApplication 实例。
    返回是否成功。
    """
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is None:
            return False
        app.clipboard().setText(text)
        return True
    except Exception:
        return False
