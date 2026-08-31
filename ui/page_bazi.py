# -*- coding: utf-8 -*-
"""
八字详盘页
==========
四柱（干支/十神/藏干/纳音）、日主强弱、格局、胎元命宫身宫、大运流年表。
"""
from __future__ import annotations

from typing import Any

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (QHBoxLayout, QHeaderView, QLabel, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)

from ui import theme
from ui.widgets import Card, KeyValue, PageTitle, SectionTitle


class BaziPage(QWidget):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self._result: dict | None = None
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)
        root.addWidget(PageTitle("八字详盘（子平法）"))
        self._empty = QLabel("请先在「基础信息」页输入出生信息并点击开始排盘。")
        self._empty.setObjectName("muted")
        self._empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty.setMinimumHeight(240)
        root.addWidget(self._empty)

        self._body = QWidget()
        root.addWidget(self._body)
        self._body.setVisible(False)
        self._build_body(self._body)

    # ---------- UI ----------
    def _build_body(self, body: QWidget):
        lay = QVBoxLayout(body)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(14)

        # 四柱卡片
        self.pillar_cards: list[Card] = []
        row = QHBoxLayout()
        row.setSpacing(12)
        for i, name in enumerate(["年柱", "月柱", "日柱", "时柱"]):
            c = Card(padding=14)
            c._pname = QLabel(name)
            c._pname.setAlignment(Qt.AlignmentFlag.AlignCenter)
            c._pname.setStyleSheet(f"font-size: 14px; color: {theme.INK_SOFT};")
            c._gan = QLabel("—")
            c._gan.setAlignment(Qt.AlignmentFlag.AlignCenter)
            c._gan.setStyleSheet(f"font-size: 30px; font-weight: bold; color: {theme.ACCENT};")
            c._zhi = QLabel("—")
            c._zhi.setAlignment(Qt.AlignmentFlag.AlignCenter)
            c._zhi.setStyleSheet(f"font-size: 30px; font-weight: bold; color: {theme.INK};")
            c._ss = QLabel("")
            c._ss.setAlignment(Qt.AlignmentFlag.AlignCenter)
            c._ss.setObjectName("muted")
            c._cang = QLabel("")
            c._cang.setAlignment(Qt.AlignmentFlag.AlignCenter)
            c._cang.setWordWrap(True)
            c._cang.setObjectName("muted")
            c._nayin = QLabel("")
            c._nayin.setAlignment(Qt.AlignmentFlag.AlignCenter)
            c._nayin.setStyleSheet(f"font-size: 13px; color: {theme.GOLD};")
            for w in (c._pname, c._gan, c._ss, c._zhi, c._cang, c._nayin):
                c.body().addWidget(w)
            self.pillar_cards.append(c)
            row.addWidget(c, 1)
        lay.addLayout(row)

        # 概要
        card = Card()
        self.kv_strength = KeyValue("日主强弱")
        self.kv_geju = KeyValue("格局")
        self.kv_zhu = KeyValue("胎元 / 命宫 / 身宫")
        self.kv_dayun = KeyValue("起运")
        self.kv_lunar = KeyValue("农历")
        for w in (self.kv_lunar, self.kv_strength, self.kv_geju, self.kv_zhu, self.kv_dayun):
            card.body().addWidget(w)
        lay.addWidget(card)

        # 大运表
        lay.addWidget(SectionTitle("大运流年"))
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["大运", "十神", "纳音", "起止年龄", "起止年份", "流年（前五）"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        lay.addWidget(self.table)

    # ---------- 数据 ----------
    def set_result(self, result: dict, profile: dict):
        self._result = result
        self._empty.setVisible(False)
        self._body.setVisible(True)
        b = result["bazi"]
        p = b["pillars"]

        for i, col in enumerate(p):
            c = self.pillar_cards[i]
            c._gan.setText(col["gan"] + f"\n{col['shishen']}")
            c._gan.setStyleSheet(
                f"font-size: 24px; font-weight: bold; {theme.wuxing_qss(col['gan_wuxing'])}")
            c._zhi.setText(col["zhi"])
            c._zhi.setStyleSheet(
                f"font-size: 26px; font-weight: bold; {theme.wuxing_qss(col['zhi_wuxing'])}")
            c._cang.setText("藏干 " + "、".join(
                f"{x['gan']}({x['shishen']})" for x in col["canggan"]))
            c._nayin.setText(col["nayin"])

        self.kv_lunar.set_value(result["lunar"]["year_ganzhi"] + "年 " + result["lunar"]["month_cn"]
                                + result["lunar"]["day_cn"] + " " + result["lunar"]["hour_branch"] + "时")
        self.kv_strength.set_value(
            f"{b['strength']}（得分 {b['strength_score']}），日主 {b['day_master']}（{b['day_master_wuxing']}）")
        self.kv_geju.set_value(b["geju"])
        self.kv_zhu.set_value(f"{b['tai_yuan']} / {b['ming_gong']} / {b['shen_gong']}")
        self.kv_dayun.set_value(
            f"{b['dayun_start']['year']} 岁 {b['dayun_start']['month']} 个月 "
            f"{b['dayun_start']['day']} 天起运，{b['dayun_forward']}")

        self.table.setRowCount(len(b["dayun"]))
        for r, d in enumerate(b["dayun"]):
            for col_i, val in enumerate([
                d["ganzhi"], d["shishen"], d["nayin"],
                f"{d['start_age']}-{d['end_age']}", f"{d['start_year']}-{d['end_year']}",
                "、".join(f"{x['year']}{x['ganzhi']}" for x in d["liunian"][:5]),
            ]):
                item = QTableWidgetItem(val)
                if col_i == 0:
                    item.setForeground(QColor(theme.WUXING_COLOR.get(d["nayin"][-1], theme.INK)))
                self.table.setItem(r, col_i, item)
