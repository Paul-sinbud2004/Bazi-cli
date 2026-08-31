# -*- coding: utf-8 -*-
"""
公共 UI 控件（卡片 / 标题 / 分隔线 / 宫位卡片等）
=================================================
全部基于 Qt 内建控件定制，遵循古风主题。
"""
from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from ui import theme


class Card(QFrame):
    """卡片容器：米白底 + 竹简黄描边 + 圆角。"""

    def __init__(self, parent: Optional[QWidget] = None, padding: int = 16):
        super().__init__(parent)
        self.setObjectName("card")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(padding, padding, padding, padding)
        self._layout.setSpacing(10)

    def body(self) -> QVBoxLayout:
        return self._layout

    def add_widget(self, w: QWidget):
        self._layout.addWidget(w)


class SectionTitle(QLabel):
    """章节标题：暗黄竖线 + 墨黑加粗。"""

    def __init__(self, text: str, parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.setObjectName("sectionTitle")


class PageTitle(QLabel):
    """页面标题：赭石红 + 暗黄竖线。"""

    def __init__(self, text: str, parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.setObjectName("pageTitle")


class MutedLabel(QLabel):
    def __init__(self, text: str = "", parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.setObjectName("muted")
        self.setWordWrap(True)


class Divider(QFrame):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("divider")


class PrimaryButton(QPushButton):
    def __init__(self, text: str, parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.setObjectName("primary")
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class GhostButton(QPushButton):
    def __init__(self, text: str, parent: Optional[QWidget] = None):
        super().__init__(text, parent)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class KeyValue(QWidget):
    """键值对展示行：label: value"""

    def __init__(self, key: str, value: str = "", parent: Optional[QWidget] = None):
        super().__init__(parent)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)
        self._k = QLabel(key)
        self._k.setObjectName("muted")
        self._v = QLabel(value)
        self._v.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        lay.addWidget(self._k)
        lay.addWidget(self._v, 1)
        lay.addStretch(0)

    def set_value(self, value: str, qss: str = ""):
        self._v.setText(value)
        if qss:
            self._v.setStyleSheet(qss)


class PalaceCell(QFrame):
    """紫微宫位卡片（四字宫名 + 干支 + 主星/辅星/四化 + 大限）。"""

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("card")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(3)
        self.name = QLabel("")
        self.name.setStyleSheet(
            f"font-size: {theme.fs(15)}px; font-weight: bold; color: {theme.ACCENT};")
        self.gz = QLabel("")
        self.gz.setObjectName("muted")
        self.major = QLabel("")
        self.major.setWordWrap(True)
        self.minor = QLabel("")
        self.minor.setObjectName("muted")
        self.minor.setWordWrap(True)
        self.dayun = QLabel("")
        self.dayun.setStyleSheet(f"font-size: {theme.fs(12)}px; color: {theme.GOLD};")
        lay.addWidget(self.name)
        lay.addWidget(self.gz)
        lay.addWidget(self.major)
        lay.addWidget(self.minor)
        lay.addWidget(self.dayun)

    def set_data(self, palace: dict):
        self.name.setText(palace["name"])
        self.gz.setText(palace["ganzhi"] + "宫")
        major = "、".join(palace["major"]) if palace["major"] else "空"
        self.major.setText(f"主星：{major}")
        if palace["minor"]:
            self.minor.setText("辅星：" + "、".join(palace["minor"]))
        else:
            self.minor.setText("")
        hua = "、".join(palace["sihua"]) if palace["sihua"] else ""
        self.dayun.setText(f"大限 {palace['dayun']}  {hua}")
