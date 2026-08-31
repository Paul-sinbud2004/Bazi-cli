# -*- coding: utf-8 -*-
"""
主窗口
======
古风布局：顶部标题栏（应用名 + 复制AI提示词按钮），
左侧导航（基础信息/八字/紫微/灵签/六十四卦），右侧页面栈。

职责：
  - 接收 InputPage.profile_changed → 一键排盘（八字+紫微）并分发到对应页；
  - 「复制 AI 提示词」把 档案+八字+紫微+（可选）灵签/卦象 组装为提示词并复制。
"""
from __future__ import annotations

from typing import Any, Optional

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (QButtonGroup, QHBoxLayout, QLabel, QMainWindow,
                             QMessageBox, QPushButton, QStackedWidget, QVBoxLayout,
                             QWidget)

from algorithm import paipan_all
from ui import theme
from ui.page_bazi import BaziPage
from ui.page_input import InputPage
from ui.page_lingqian import LingqianPage
from ui.page_zhouyi import ZhouyiPage
from ui.page_ziwei import ZiweiPage
from ui.widgets import GhostButton
from utils import config as cfg
from utils.ai_prompt import build_prompt
from utils.clipboard import copy_text

_NAV_ITEMS = [
    ("基础信息", 0),
    ("八字详盘", 1),
    ("紫微斗数", 2),
    ("黄大仙灵签", 3),
    ("周易六十四卦", 4),
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("命理精研 · 八字 / 紫微 / 灵签 / 六十四卦")
        self.setMinimumSize(1080, 720)
        self._profile: Optional[dict] = None
        self._bazi: Optional[dict] = None
        self._ziwei: Optional[dict] = None

        central = QWidget()
        central.setObjectName("root")
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())
        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(self._build_nav())
        body.addWidget(self._build_stack(), 1)
        root.addLayout(body, 1)

    # ---------- 构建 ----------
    def _build_header(self) -> QWidget:
        bar = QWidget()
        bar.setStyleSheet(
            f"QWidget {{ background-color: {theme.BG_SOFT}; border-bottom: 2px solid {theme.GOLD}; }}")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(20, 10, 20, 10)
        title = QLabel("命理精研")
        title.setObjectName("appTitle")
        sub = QLabel("八字 · 紫微斗数 · 黄大仙灵签 · 周易六十四卦")
        sub.setObjectName("appSub")
        lay.addWidget(title)
        lay.addWidget(sub)
        lay.addStretch(1)
        self.ai_btn = GhostButton("复制 AI 提示词")
        self.ai_btn.setToolTip("将出生档案、八字、紫微排盘（及最近灵签/卦象）"
                               "组装为一段结构化提示词，供粘贴到任意 AI 助手深度分析")
        self.ai_btn.clicked.connect(self._on_ai_prompt)
        lay.addWidget(self.ai_btn)
        self.ai_status = QLabel("")
        self.ai_status.setObjectName("muted")
        lay.addWidget(self.ai_status)
        return bar

    def _build_nav(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("navPanel")
        panel.setFixedWidth(170)
        panel.setStyleSheet(f"QWidget#navPanel {{ background-color: {theme.BG_SOFT}; }}")
        lay = QVBoxLayout(panel)
        lay.setContentsMargins(0, 12, 0, 12)
        lay.setSpacing(4)

        self._nav_group = QButtonGroup(self)
        self._nav_group.setExclusive(True)
        self._nav_btns: list[QPushButton] = []
        for text, idx in _NAV_ITEMS:
            b = QPushButton(text)
            b.setObjectName("nav")
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _=False, i=idx: self._stack.setCurrentIndex(i))
            self._nav_group.addButton(b)
            self._nav_btns.append(b)
            lay.addWidget(b)
        self._nav_btns[0].setChecked(True)

        lay.addStretch(1)
        ver = QLabel("v0.1 · 古风命理工具")
        ver.setObjectName("muted")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(ver)
        return panel

    def _build_stack(self) -> QStackedWidget:
        self._stack = QStackedWidget()
        self.input_page = InputPage()
        self.bazi_page = BaziPage()
        self.ziwei_page = ZiweiPage()
        self.lingqian_page = LingqianPage()
        self.zhouyi_page = ZhouyiPage()
        for p in (self.input_page, self.bazi_page, self.ziwei_page,
                  self.lingqian_page, self.zhouyi_page):
            self._stack.addWidget(p)
        self.input_page.profile_changed.connect(self._on_profile_changed)
        return self._stack

    # ---------- 排盘 ----------
    def _on_profile_changed(self, profile: dict):
        """基础信息页「开始排盘」→ 一键排盘并分发。"""
        try:
            y, m, d = (int(x) for x in profile["solar_date"].split("-"))
            hh, mm = (int(x) for x in profile["solar_time"].split(":"))
            result = paipan_all(
                y, m, d, hh, mm,
                gender=profile.get("gender", "男"),
                leap_month_mode=profile.get("leap_month_mode", "next"),
            )
        except Exception as e:  # noqa: BLE001
            QMessageBox.critical(self, "排盘失败", f"排盘时发生错误：\n{e}")
            return
        self._profile = profile
        self._bazi = result["bazi"]
        self._ziwei = result["ziwei"]
        self.bazi_page.set_result(result, profile)
        self.ziwei_page.set_result(result, profile)
        self._stack.setCurrentIndex(1)
        self._nav_btns[1].setChecked(True)

    # ---------- AI 提示词 ----------
    def _on_ai_prompt(self):
        if not (self._bazi and self._ziwei):
            QMessageBox.information(
                self, "尚未排盘",
                "请先在「基础信息」页填写出生信息并点击「开始排盘」，"
                "即可一键复制供 AI 分析的完整提示词。")
            return
        profile = self._profile or cfg.load_birth() or {}
        prompt = build_prompt(
            profile, self._bazi, self._ziwei,
            qian=self.lingqian_page.last_result(),
            gua=self.zhouyi_page.last_result(),
        )
        if copy_text(prompt):
            self.ai_status.setText("✓ 已复制 AI 提示词")
            self.ai_status.setStyleSheet(
                f"color: {theme.OK}; font-size: 13px; padding-left: 8px;")
        else:
            self.ai_status.setText("✗ 复制失败（剪贴板不可用）")
            self.ai_status.setStyleSheet(
                f"color: {theme.BAD}; font-size: 13px; padding-left: 8px;")
        QTimer.singleShot(4000, lambda: self.ai_status.setText(""))
