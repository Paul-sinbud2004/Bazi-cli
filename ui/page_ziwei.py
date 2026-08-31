# -*- coding: utf-8 -*-
"""
紫微斗数排盘页
==============
命身宫 / 五行局 / 命主身主 / 四化 / 大限概要 + 十二宫网格（命宫起逆时针）。
"""
from __future__ import annotations

from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from ui import theme
from ui.widgets import Card, KeyValue, PageTitle, PalaceCell, SectionTitle


class ZiweiPage(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._result: dict | None = None
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)
        root.addWidget(PageTitle("紫微斗数排盘"))

        self._empty = QLabel("请先在「基础信息」页输入出生信息并点击开始排盘。")
        self._empty.setObjectName("muted")
        self._empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty.setMinimumHeight(240)
        root.addWidget(self._empty)

        self._body = QWidget()
        root.addWidget(self._body)
        self._body.setVisible(False)
        self._build_body(self._body)

    def _build_body(self, body: QWidget):
        lay = QVBoxLayout(body)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)

        # 概要
        card = Card()
        self.kv_ming = KeyValue("命宫 / 身宫")
        self.kv_ju = KeyValue("五行局")
        self.kv_zhu = KeyValue("命主 / 身主")
        self.kv_zw = KeyValue("紫微 / 天府")
        self.kv_sh = KeyValue("四化（生年干）")
        self.kv_dayun = KeyValue("大限")
        for w in (self.kv_ming, self.kv_ju, self.kv_zhu, self.kv_zw, self.kv_sh, self.kv_dayun):
            card.body().addWidget(w)
        lay.addWidget(card)

        # 十二宫网格
        lay.addWidget(SectionTitle("十二宫（命宫起逆时针布列）"))
        grid_card = Card(padding=12)
        grid = QGridLayout()
        grid.setSpacing(10)
        grid_card.body().addLayout(grid)
        self.cells: list[PalaceCell] = []
        # 4 行 3 列，按 palaces 顺序（逆时针）填充
        for i in range(12):
            cell = PalaceCell()
            self.cells.append(cell)
            grid.addWidget(cell, i // 3, i % 3)
        lay.addWidget(grid_card)

    def set_result(self, result: dict, profile: dict):
        self._result = result
        self._empty.setVisible(False)
        self._body.setVisible(True)
        z = result["ziwei"]
        self.kv_ming.set_value(f"{z['ming_gong']}宫 / {z['shen_gong']}宫（{z['ming_ganzhi']}）")
        self.kv_ju.set_value(z["wuxing_ju"] + f"（{z['dayun_start_age']}岁起限）")
        self.kv_zhu.set_value(f"{z['ming_zhu']} / {z['shen_zhu']}")
        self.kv_zw.set_value(f"{z['ziwei_branch']}宫 / {z['tianfu_branch']}宫")
        self.kv_sh.set_value("、".join(z["sihua_summary"]))
        self.kv_dayun.set_value(f"{z['dayun_forward']}，命宫 {z['palaces'][0]['dayun']}")

        for i, palace in enumerate(z["palaces"]):
            self.cells[i].set_data(palace)
