# -*- coding: utf-8 -*-
"""
字体设置对话框
==============
选择字体族（含「跟随系统默认」）与字号，带实时预览；
确认后由主窗口持久化并全局应用。
"""
from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QComboBox, QDialog, QHBoxLayout, QLabel, QSpinBox,
                             QVBoxLayout, QWidget)

from ui import theme
from ui.widgets import Divider, GhostButton, PrimaryButton
from utils import fontman

_SAMPLE = ("乾坤有序，命理精研　第卅八签 · 上吉\n"
           "四柱：庚午 辛巳 壬午 丁未　·　紫微命宫在卯，木三局\n"
           "The quick brown fox 0123456789")


class FontDialog(QDialog):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setWindowTitle("字体设置")
        self.setMinimumWidth(460)

        fam, size = fontman.load_font_config()
        families = fontman.chinese_families()
        if fam and fam not in families:
            families = [fam] + families

        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 16, 18, 16)
        lay.setSpacing(12)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("字体"))
        self.family_combo = QComboBox()
        self.family_combo.addItem("跟随系统默认（自动适配）", "")
        for f in families:
            self.family_combo.addItem(f, f)
        idx = self.family_combo.findData(fam)
        self.family_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.family_combo.currentIndexChanged.connect(self._preview)
        row1.addWidget(self.family_combo, 1)
        lay.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("字号"))
        self.size_spin = QSpinBox()
        self.size_spin.setRange(fontman.MIN_SIZE, fontman.MAX_SIZE)
        self.size_spin.setValue(size)
        self.size_spin.setSuffix(" px")
        self.size_spin.valueChanged.connect(self._preview)
        row2.addWidget(self.size_spin)
        row2.addStretch(1)
        lay.addLayout(row2)

        lay.addWidget(Divider())
        tip = QLabel("预览")
        tip.setObjectName("muted")
        lay.addWidget(tip)
        self.preview = QLabel(_SAMPLE)
        self.preview.setWordWrap(True)
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setStyleSheet(
            f"background-color: {theme.CARD}; border: 1px solid {theme.CARD_BORDER};"
            f"border-radius: 6px; padding: 16px;")
        lay.addWidget(self.preview)
        self._preview()

        btns = QHBoxLayout()
        btns.addStretch(1)
        cancel = GhostButton("取消")
        cancel.clicked.connect(self.reject)
        btns.addWidget(cancel)
        ok = PrimaryButton("保存并应用")
        ok.clicked.connect(self.accept)
        btns.addWidget(ok)
        lay.addLayout(btns)

    def _preview(self):
        fam = self.family_combo.currentData() or ""
        size = self.size_spin.value()
        fam_css = f"\"{fam}\"" if fam else theme.font_family_css()
        self.preview.setStyleSheet(
            f"font-family: {fam_css}; font-size: {size}px; color: {theme.INK};"
            f"background-color: {theme.CARD}; border: 1px solid {theme.CARD_BORDER};"
            f"border-radius: 6px; padding: 16px;")

    def result_config(self) -> tuple[str, int]:
        """用户确认的 (family, size)。"""
        return self.family_combo.currentData() or "", self.size_spin.value()
