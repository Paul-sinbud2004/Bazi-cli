# -*- coding: utf-8 -*-
"""
黄大仙灵签页
============
随机求签 / 指定签号求签，展示签题、吉凶、签诗与解读。
"""
from __future__ import annotations

import random
from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QHBoxLayout, QLabel, QSpinBox, QVBoxLayout, QWidget)

from algorithm import lingqian
from ui import theme
from ui.widgets import Card, Divider, GhostButton, MutedLabel, PageTitle, PrimaryButton, SectionTitle
from utils.clipboard import copy_text


class LingqianPage(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)
        root.addWidget(PageTitle("黄大仙灵签（100签）"))

        # 操作行
        ops = QHBoxLayout()
        ops.setSpacing(12)
        self.draw_btn = PrimaryButton("求签")
        self.draw_btn.clicked.connect(lambda: self.draw())
        ops.addWidget(self.draw_btn)
        ops.addWidget(QLabel("或指定签号"))
        self.num_spin = QSpinBox()
        self.num_spin.setRange(1, 100)
        self.num_spin.setValue(random.randint(1, 100))
        ops.addWidget(self.num_spin)
        self.num_btn = GhostButton("求此签")
        self.num_btn.clicked.connect(lambda: self.draw(self.num_spin.value()))
        ops.addWidget(self.num_btn)
        ops.addStretch(1)
        root.addLayout(ops)

        # 结果卡
        self.card = Card()
        body = self.card.body()
        self.title = QLabel("点击「求签」抽取一支灵签")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {theme.ACCENT};")
        body.addWidget(self.title)
        self.grade = QLabel("")
        self.grade.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grade.setStyleSheet(f"font-size: 16px; color: {theme.WARN};")
        body.addWidget(self.grade)
        self.poem = QLabel("")
        self.poem.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.poem.setWordWrap(True)
        self.poem.setStyleSheet(f"font-size: 17px; line-height: 1.7; color: {theme.INK};")
        body.addWidget(self.poem)
        body.addWidget(Divider())
        self.jie = MutedLabel("")
        self.diangu = MutedLabel("")
        self.yunshi = MutedLabel("")
        for w in (self.jie, self.diangu, self.yunshi):
            body.addWidget(w)
        root.addWidget(self.card)

        # 复制按钮
        self.copy_btn = GhostButton("复制签文")
        self.copy_btn.clicked.connect(self._copy)
        root.addWidget(self.copy_btn)
        root.addStretch(1)

        self._result: dict | None = None

    def draw(self, number: int | None = None):
        try:
            self._result = lingqian.qiu_qian(number=number)
        except ValueError as e:
            self.title.setText(str(e))
            return
        r = self._result
        self.title.setText(f"第 {r['number']} 签 · {r['title']}")
        self.grade.setText(f"【{r['grade']}】")
        self.grade.setStyleSheet(f"font-size: 18px; font-weight: bold; {theme.grade_qss(r['grade'])}")
        self.poem.setText("\n".join(r["poem"]))
        self.jie.setText(f"解曰：{r['jie']}")
        self.diangu.setText(f"典故：{r['diangu']}")
        self.yunshi.setText(f"运势：{r['yunshi']}")

    def last_result(self) -> dict | None:
        """最近一次求签结果（供主窗口组装 AI 提示词）。"""
        return self._result

    def _copy(self):
        if self._result:
            copy_text(lingqian.to_text(self._result))
