# -*- coding: utf-8 -*-
"""
基础信息输入页
==============
姓名 / 性别 / 出生日期时间 / 出生地经度 / 真太阳时开关 / 紫微闰月派别。
"开始排盘"后保存档案并发起全量排盘（八字+紫微），由主窗口分发。
"""
from __future__ import annotations

from PyQt6.QtCore import QDate, QTime, pyqtSignal
from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDateEdit, QDoubleSpinBox, QHBoxLayout,
                             QLabel, QLineEdit, QTimeEdit, QVBoxLayout, QWidget)

from ui import theme
from ui.widgets import Card, Divider, KeyValue, MutedLabel, PageTitle, PrimaryButton, SectionTitle
from utils import config as cfg
from utils.suntime import to_true_solar_text


class InputPage(QWidget):
    """基础信息页。发排盘请求：profile_changed(dict)。"""

    profile_changed = pyqtSignal(dict)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        p = cfg.load_profile()
        self._build(p)
        self._refresh_true_solar()

    # ---------- UI ----------
    def _build(self, p: dict):
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)
        root.addWidget(PageTitle("基础信息"))

        card = Card()
        body = card.body()
        body.addWidget(SectionTitle("出生信息"))

        # 姓名 + 性别
        row1 = QHBoxLayout()
        row1.setSpacing(12)
        row1.addWidget(QLabel("称呼 / 姓名"))
        self.name_edit = QLineEdit(p.get("name", ""))
        self.name_edit.setPlaceholderText("可选")
        row1.addWidget(self.name_edit, 1)
        row1.addWidget(QLabel("性别"))
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["男", "女"])
        self.gender_combo.setCurrentText(p.get("gender", "男"))
        row1.addWidget(self.gender_combo)
        body.addLayout(row1)

        # 出生日期 + 时间
        row2 = QHBoxLayout()
        row2.setSpacing(12)
        row2.addWidget(QLabel("公历出生"))
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(QDate.currentDate().addYears(-30))
        d = p.get("solar_date", "")
        if d:
            qd = QDate.fromString(d, "yyyy-MM-dd")
            if qd.isValid():
                self.date_edit.setDate(qd)
        self.date_edit.dateChanged.connect(self._refresh_true_solar)
        row2.addWidget(self.date_edit)
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setTime(QTime.fromString(p.get("solar_time", "12:00"), "HH:mm"))
        self.time_edit.timeChanged.connect(self._refresh_true_solar)
        row2.addWidget(self.time_edit)
        body.addLayout(row2)

        # 经度 + 真太阳时
        row3 = QHBoxLayout()
        row3.setSpacing(12)
        row3.addWidget(QLabel("出生地经度(°E)"))
        self.lon_spin = QDoubleSpinBox()
        self.lon_spin.setRange(73.0, 135.0)
        self.lon_spin.setDecimals(2)
        self.lon_spin.setSingleStep(0.5)
        self.lon_spin.setValue(float(p.get("longitude", 120.0)))
        self.lon_spin.valueChanged.connect(self._refresh_true_solar)
        row3.addWidget(self.lon_spin)
        self.ts_check = QCheckBox("使用真太阳时校正")
        self.ts_check.setToolTip("真太阳时 = 地方平太阳时 + 均时差。\n"
                                 "出生时辰以当地真太阳时为准更精确（默认北京时间）。")
        self.ts_check.setChecked(bool(p.get("use_true_solar", False)))
        self.ts_check.toggled.connect(self._refresh_true_solar)
        row3.addWidget(self.ts_check)
        row3.addStretch(1)
        body.addLayout(row3)

        self.ts_preview = MutedLabel("")
        body.addWidget(self.ts_preview)

        body.addWidget(Divider())

        # 闰月派别
        body.addWidget(SectionTitle("紫微斗数闰月派别"))
        row4 = QHBoxLayout()
        row4.setSpacing(12)
        self.leap_combo = QComboBox()
        self.leap_combo.addItem("按下月（默认，依《紫微斗数全书》）", "next")
        self.leap_combo.addItem("十五分界（王亭之中州派）", "half")
        self.leap_combo.addItem("按当月（了无居士等）", "same")
        idx = self.leap_combo.findData(p.get("leap_month_mode", "next"))
        self.leap_combo.setCurrentIndex(idx if idx >= 0 else 0)
        row4.addWidget(self.leap_combo, 1)
        body.addLayout(row4)
        body.addWidget(MutedLabel(
            "《紫微斗数全书》卷二·安命身例：“凡有闰月具要依此为例”，闰月一律作下月推排；"
            "十五分界（初一至十五归上月、十六后归下月）多用于流月。"))

        # 排盘按钮
        btn = PrimaryButton("开始排盘")
        btn.clicked.connect(self._on_paipan)
        root.addWidget(card)
        root.addWidget(btn)

        # 说明
        note = Card(padding=12)
        note.body().addWidget(MutedLabel(
            "说明：八字按节气换月换年（子平法）；紫微斗数按农历，不依节气。"
            "晚子时（23:00-24:00）日数按当天、时柱按次日（主流派别）。"))
        root.addWidget(note)
        root.addStretch(1)

    # ---------- 逻辑 ----------
    def _refresh_true_solar(self):
        """根据当前输入刷新真太阳时预览。"""
        qd = self.date_edit.date()
        qt = self.time_edit.time()
        lon = self.lon_spin.value()
        ts = to_true_solar_text(qd.year(), qd.month(), qd.day(), qt.hour(), qt.minute(), lon)
        bj = f"{qt.hour():02d}:{qt.minute():02d}"
        self._ts = ts
        self.ts_preview.setText(f"北京时间 {bj} → 真太阳时 ≈ {ts}（经度 {lon:.2f}°E）")

    def _on_paipan(self):
        """校验并保存档案，发起排盘。"""
        qd = self.date_edit.date()
        qt = self.time_edit.time()
        profile = {
            "name": self.name_edit.text().strip(),
            "gender": self.gender_combo.currentText(),
            "solar_date": qd.toString("yyyy-MM-dd"),
            "solar_time": qt.toString("HH:mm"),
            "longitude": self.lon_spin.value(),
            "use_true_solar": self.ts_check.isChecked(),
            "true_solar_display": self._ts if self.ts_check.isChecked() else "",
            "leap_month_mode": self.leap_combo.currentData(),
        }
        cfg.save_profile(profile)
        self.profile_changed.emit(profile)
