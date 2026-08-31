# -*- coding: utf-8 -*-
"""
历史记录页
==========
排盘 / 灵签 / 卦象记录列表（仅本地存储）：
- 按保存时间倒序展示「时间 · 类型 · 标题 · 概要」；
- 双击条目或选中后点「打开记录」→ 发 replay_requested 信号，由主窗口复现；
- 支持删除所选、按类型清空。
"""
from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QListWidget,
                             QListWidgetItem, QMessageBox, QVBoxLayout, QWidget)

from ui.widgets import Card, GhostButton, MutedLabel, PageTitle, PrimaryButton
from utils import records


class RecordsPage(QWidget):
    replay_requested = pyqtSignal(dict)

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._records: list[dict] = []
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)
        root.addWidget(PageTitle("历史记录"))

        # 过滤行
        ops = QHBoxLayout()
        ops.setSpacing(12)
        ops.addWidget(QLabel("类型"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItem("全部", None)
        self.filter_combo.addItem("八字 / 紫微排盘", records.KIND_PAIPAN)
        self.filter_combo.addItem("黄大仙灵签", records.KIND_LINGQIAN)
        self.filter_combo.addItem("周易六十四卦", records.KIND_ZHOUYI)
        self.filter_combo.currentIndexChanged.connect(self.refresh)
        ops.addWidget(self.filter_combo)
        self.count_label = MutedLabel("")
        ops.addWidget(self.count_label)
        ops.addStretch(1)

        self.open_btn = PrimaryButton("打开记录")
        self.open_btn.clicked.connect(self._on_open)
        ops.addWidget(self.open_btn)
        self.del_btn = GhostButton("删除所选")
        self.del_btn.clicked.connect(self._on_delete)
        ops.addWidget(self.del_btn)
        self.clear_btn = GhostButton("清空当前类型")
        self.clear_btn.clicked.connect(self._on_clear)
        ops.addWidget(self.clear_btn)
        root.addLayout(ops)

        # 列表
        self.list = QListWidget()
        self.list.itemDoubleClicked.connect(lambda _: self._on_open())
        root.addWidget(self.list, 1)

        note = MutedLabel("所有记录仅保存在本机（不上传云端、不外发数据）。"
                          "点击记录可一键回填信息并复现完整排盘 / 签文 / 卦象。")
        root.addWidget(note)
        self.refresh()

    # ---------- 数据 ----------
    def refresh(self):
        kind = self.filter_combo.currentData() if hasattr(self, "filter_combo") else None
        self._records = records.all_records(kind)
        self.list.clear()
        for rec in self._records:
            label = records.KIND_LABEL.get(rec.get("kind"), "?")
            item = QListWidgetItem(
                f"{rec.get('time', '')}　【{label}】{rec.get('title', '')}\n"
                f"    {rec.get('summary', '')}")
            item.setData(Qt.ItemDataRole.UserRole, rec.get("id"))
            self.list.addItem(item)
        self.count_label.setText(f"共 {len(self._records)} 条")
        self.open_btn.setEnabled(bool(self._records))
        self.del_btn.setEnabled(bool(self._records))

    def _current_record(self) -> Optional[dict]:
        row = self.list.currentRow()
        if 0 <= row < len(self._records):
            return self._records[row]
        return None

    # ---------- 动作 ----------
    def _on_open(self):
        rec = self._current_record()
        if rec:
            self.replay_requested.emit(rec)

    def _on_delete(self):
        rec = self._current_record()
        if not rec:
            return
        records.remove(rec["id"])
        self.refresh()

    def _on_clear(self):
        kind = self.filter_combo.currentData()
        scope = "全部记录" if kind is None else f"「{records.KIND_LABEL.get(kind)}」记录"
        if QMessageBox.question(
                self, "确认清空", f"确定要清空{scope}吗？此操作不可恢复。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            records.clear(kind)
            self.refresh()
