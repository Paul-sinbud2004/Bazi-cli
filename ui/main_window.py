# -*- coding: utf-8 -*-
"""
主窗口
======
古风布局：顶部标题栏（应用名 + 字体设置 + 复制AI提示词按钮），
左侧导航（基础信息/八字/紫微/灵签/六十四卦/历史记录），右侧页面栈。

职责：
  - 接收 InputPage.profile_changed → 一键排盘（八字+紫微）并分发到对应页；
  - 排盘 / 求签 / 起卦结果自动保存到本地历史记录，可在「历史记录」页一键复现；
  - 字体设置：全局应用用户自选字体/字号，并持久化（重启自动生效）；
  - 「复制 AI 提示词」把 档案+八字+紫微+（可选）灵签/卦象 组装为提示词并复制。
"""
from __future__ import annotations

from typing import Any, Optional

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (QApplication, QButtonGroup, QHBoxLayout, QLabel,
                             QMainWindow, QMessageBox, QPushButton,
                             QStackedWidget, QVBoxLayout, QWidget)

from algorithm import paipan_all
from ui import theme
from ui.dialog_font import FontDialog
from ui.page_bazi import BaziPage
from ui.page_input import InputPage
from ui.page_lingqian import LingqianPage
from ui.page_records import RecordsPage
from ui.page_zhouyi import ZhouyiPage
from ui.page_ziwei import ZiweiPage
from ui.widgets import GhostButton
from utils import config as cfg
from utils import records
from utils.ai_prompt import build_prompt
from utils.clipboard import copy_text
from utils.fontman import app_font, save_font_config

_NAV_ITEMS = [
    ("基础信息", 0),
    ("八字详盘", 1),
    ("紫微斗数", 2),
    ("黄大仙灵签", 3),
    ("周易六十四卦", 4),
    ("历史记录", 5),
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("命理精研 · 八字 / 紫微 / 灵签 / 六十四卦")
        self.setMinimumSize(1080, 720)
        self._profile: Optional[dict] = None
        self._paipan: Optional[dict] = None      # 最近一次完整排盘结果（含 bazi/ziwei/lunar）
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
        self.font_btn = GhostButton("字体设置")
        self.font_btn.setToolTip("自定义界面字体与字号（自动保存，重启后依然生效）")
        self.font_btn.clicked.connect(self._on_font_dialog)
        lay.addWidget(self.font_btn)
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
            b.clicked.connect(lambda _=False, i=idx: self._goto(i))
            self._nav_group.addButton(b)
            self._nav_btns.append(b)
            lay.addWidget(b)
        self._nav_btns[0].setChecked(True)

        lay.addStretch(1)
        ver = QLabel("v2.1 · 古风命理工具")
        ver.setObjectName("muted")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(ver)
        return panel

    def _goto(self, idx: int):
        """切换页面；进入历史记录页时刷新列表。"""
        if idx == len(_NAV_ITEMS) - 1:
            self.records_page.refresh()
        self._stack.setCurrentIndex(idx)

    def _build_stack(self) -> QStackedWidget:
        self._stack = QStackedWidget()
        self._create_pages()
        return self._stack

    def _create_pages(self):
        """构建全部页面并接线（字体变更重建时复用）。"""
        self.input_page = InputPage()
        self.bazi_page = BaziPage()
        self.ziwei_page = ZiweiPage()
        self.lingqian_page = LingqianPage()
        self.zhouyi_page = ZhouyiPage()
        self.records_page = RecordsPage()
        for p in (self.input_page, self.bazi_page, self.ziwei_page,
                  self.lingqian_page, self.zhouyi_page, self.records_page):
            self._stack.addWidget(p)
        self.input_page.profile_changed.connect(self._on_profile_changed)
        self.records_page.replay_requested.connect(self._on_replay)

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
        self._paipan = result
        self._bazi = result["bazi"]
        self._ziwei = result["ziwei"]
        self.bazi_page.set_result(result, profile)
        self.ziwei_page.set_result(result, profile)
        self._goto(1)
        self._nav_btns[1].setChecked(True)
        # 本地自动保存排盘记录（不上传云端）
        b = result["bazi"]
        pillars = " ".join(col["ganzhi"] for col in b["pillars"])
        name = profile.get("name") or "未命名"
        records.add(
            records.KIND_PAIPAN,
            f"{name}（{profile.get('gender', '男')}）{profile.get('solar_date')} "
            f"{profile.get('solar_time')}",
            f"四柱：{pillars}　日主：{b['day_master']}（{b['day_master_wuxing']}）　"
            f"格局：{b['geju']}",
            {"profile": profile, "result": result},
        )

    # ---------- 历史记录复现 ----------
    def _on_replay(self, rec: dict):
        """点击历史记录条目 → 一键回填 / 复现。"""
        kind = rec.get("kind")
        payload = rec.get("payload") or {}
        try:
            if kind == records.KIND_PAIPAN:
                profile = payload.get("profile") or {}
                result = payload.get("result") or {}
                if not result:
                    return
                self.input_page.fill_profile(profile)
                cfg.save_profile(profile)
                self._profile = profile
                self._paipan = result
                self._bazi = result.get("bazi")
                self._ziwei = result.get("ziwei")
                self.bazi_page.set_result(result, profile)
                self.ziwei_page.set_result(result, profile)
                self._goto(1)
                self._nav_btns[1].setChecked(True)
            elif kind == records.KIND_LINGQIAN:
                self.lingqian_page.replay(payload)
                self._goto(3)
                self._nav_btns[3].setChecked(True)
            elif kind == records.KIND_ZHOUYI:
                self.zhouyi_page.replay(payload)
                self._goto(4)
                self._nav_btns[4].setChecked(True)
        except Exception as e:  # noqa: BLE001
            QMessageBox.warning(self, "复现失败", f"该记录无法复现：\n{e}")

    # ---------- 字体设置 ----------
    def _on_font_dialog(self):
        dlg = FontDialog(self)
        if dlg.exec() == FontDialog.DialogCode.Accepted:
            family, size = dlg.result_config()
            save_font_config(family, size)
            self.apply_font_settings()

    def apply_font_settings(self):
        """全局应用字体设置：重建 QSS + 全局字体 + 重建各页（自适应字号）。"""
        # 保留当前状态，用于重建后恢复
        last_paipan = self._paipan
        last_profile = self._profile
        last_lq = self.lingqian_page.last_result()
        last_zy = self.zhouyi_page.last_result()

        theme.rebuild_qss()
        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(theme.QSS)
            fam, size = theme.FONT_FAMILY, theme.FONT_SIZE
            f = app_font(fam, size)
            if f is not None:
                app.setFont(f)

        # 重建页面栈（内联样式按新字号重算）
        old_pages = [self._stack.widget(i) for i in range(self._stack.count())]
        for w in old_pages:
            self._stack.removeWidget(w)
            w.deleteLater()
        self._create_pages()
        self._nav_btns[0].setChecked(True)

        # 恢复最近结果
        if last_paipan and last_profile:
            self._profile = last_profile
            self._paipan = last_paipan
            self._bazi = last_paipan.get("bazi")
            self._ziwei = last_paipan.get("ziwei")
            self.bazi_page.set_result(last_paipan, last_profile)
            self.ziwei_page.set_result(last_paipan, last_profile)
        if last_lq:
            self.lingqian_page.replay(last_lq)
        if last_zy:
            self.zhouyi_page.replay(last_zy)

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
                f"color: {theme.OK}; font-size: {theme.fs(13)}px; padding-left: 8px;")
        else:
            self.ai_status.setText("✗ 复制失败（剪贴板不可用）")
            self.ai_status.setStyleSheet(
                f"color: {theme.BAD}; font-size: {theme.fs(13)}px; padding-left: 8px;")
        QTimer.singleShot(4000, lambda: self.ai_status.setText(""))
