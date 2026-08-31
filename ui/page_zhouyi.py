# -*- coding: utf-8 -*-
"""
周易六十四卦页
==============
时间起卦（梅花易数）/ 铜钱摇卦，或按卦序直接查卦；
展示本卦、动爻爻辞、变卦与吉凶解读（整体运势 / 事业 / 感情 / 财运）。
"""
from __future__ import annotations

import random
from datetime import datetime
from typing import Any, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QComboBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget)

from algorithm import zhouyi
from algorithm.bazi import get_lunar_info
from ui import theme
from ui.widgets import (Card, Divider, GhostButton, MutedLabel, PageTitle, PrimaryButton)
from utils import records
from utils.clipboard import copy_text

# 爻位名称（自下而上，与 gua64.json 的 yaoci 顺序一致）
_YAO_POS = ["初", "二", "三", "四", "五", "上"]
# 铜钱三背/二背/一背/零背 → 卦象描述
_COIN_LABEL = {3: "老阳·动", 2: "少阳", 1: "少阴", 0: "老阴·动"}


class ZhouyiPage(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._result: Optional[dict] = None
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(14)
        root.addWidget(PageTitle("周易六十四卦"))

        # ---------- 操作行 ----------
        ops = QHBoxLayout()
        ops.setSpacing(12)
        self.time_btn = PrimaryButton("时间起卦")
        self.time_btn.setToolTip("以当前公历时间换算农历后按梅花易数起卦")
        self.time_btn.clicked.connect(self.time_cast)
        ops.addWidget(self.time_btn)
        self.coin_btn = PrimaryButton("铜钱摇卦")
        self.coin_btn.setToolTip("模拟三枚铜钱掷六次（三背为老阳动，零背为老阴动）")
        self.coin_btn.clicked.connect(self.coin_cast)
        ops.addWidget(self.coin_btn)
        ops.addWidget(QLabel("或查卦"))
        self.gua_combo = QComboBox()
        for g in zhouyi.list_all():
            self.gua_combo.addItem(f"{g['id']:02d} {g['symbol']} {g['name']}", g["id"])
        self.gua_combo.setMinimumWidth(140)
        ops.addWidget(self.gua_combo)
        self.gua_btn = GhostButton("查卦")
        self.gua_btn.clicked.connect(lambda: self.lookup_gua(self.gua_combo.currentData()))
        ops.addWidget(self.gua_btn)
        ops.addStretch(1)
        root.addLayout(ops)

        # ---------- 结果卡 ----------
        self.card = Card()
        body = self.card.body()
        self.title = QLabel("点击「时间起卦」或「铜钱摇卦」起卦")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setStyleSheet(
            f"font-size: {theme.fs(22)}px; font-weight: bold; color: {theme.ACCENT};")
        body.addWidget(self.title)
        self.subtitle = MutedLabel("也可从右侧列表选择卦象直接查阅")
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body.addWidget(self.subtitle)
        self.ben = QLabel("")
        self.ben.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ben.setWordWrap(True)
        self.ben.setStyleSheet(f"font-size: {theme.fs(18)}px; color: {theme.INK};")
        body.addWidget(self.ben)
        self.guaci = MutedLabel("")
        self.guaci.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body.addWidget(self.guaci)
        self.ji = QLabel("")
        self.ji.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ji.setStyleSheet(
            f"font-size: {theme.fs(17)}px; font-weight: bold; color: {theme.WARN};")
        body.addWidget(self.ji)
        self.dong = MutedLabel("")
        self.bian = MutedLabel("")
        body.addWidget(self.dong)
        body.addWidget(self.bian)
        body.addWidget(Divider())
        self.yun = MutedLabel("")
        self.shiye = MutedLabel("")
        self.ganqing = MutedLabel("")
        self.caiyun = MutedLabel("")
        for w in (self.yun, self.shiye, self.ganqing, self.caiyun):
            body.addWidget(w)
        root.addWidget(self.card)

        # ---------- 复制 ----------
        self.copy_btn = GhostButton("复制卦象")
        self.copy_btn.clicked.connect(self._copy)
        root.addWidget(self.copy_btn)
        root.addStretch(1)

    # ---------- 起卦动作 ----------
    def time_cast(self):
        """时间起卦：以当前时间换算农历，取年支/月/日/时辰起卦。"""
        now = datetime.now()
        info = get_lunar_info(now.year, now.month, now.day, now.hour, now.minute)
        # year_ganzhi 形如「丙午」，地支为第二字
        year_branch = info["year_ganzhi"][1]
        self._result = zhouyi.qigua_by_time(
            year_branch, info["month"], info["day"], info["hour_branch"])
        # 附注起卦时间
        lunar_txt = (f"{info['year_ganzhi']}年 {info['month_cn']}月{info['day_cn']}日 "
                     f"{info['hour_branch']}时")
        self._result["time_note"] = (f"{now.year}年{now.month}月{now.day}日 "
                                     f"{now.hour:02d}:{now.minute:02d}（农历{lunar_txt}）")
        self._render(self._result)
        self._save_record()

    def coin_cast(self):
        """铜钱摇卦：模拟六次掷钱，展示逐爻结果与动爻。"""
        try:
            self._result = zhouyi.qigua_by_coins(seed=random.randrange(1 << 30))
        except RuntimeError as e:
            self.title.setText(f"起卦失败：{e}")
            return
        self._render(self._result)
        self._save_record()

    def lookup_gua(self, gua_id: int):
        """直接查卦：不涉及起卦，仅展示卦辞、爻辞与解读。"""
        g = zhouyi.get_gua(gua_id)
        self._result = g
        self._render(g)
        self._save_record()

    # ---------- 记录 ----------
    def _save_record(self):
        """起卦/查卦结果自动保存到本地记录（不上传云端）。"""
        r = self._result
        if not r:
            return
        if "method" in r:  # 起卦结果
            title = f"{r['ben_symbol']} {r['ben_gua']}卦 · {r['method']}"
        else:              # 查卦结果
            title = f"{r['symbol']} {r['name']}卦（第 {r['id']} 卦）"
        records.add(
            records.KIND_ZHOUYI,
            title,
            f"卦辞：{r['guaci'][:40]}　吉凶：{r['ji']}",
            r,
        )

    def replay(self, r: dict):
        """从历史记录复现卦象（不重复保存记录）。"""
        if not r or "guaci" not in r:
            return
        self._result = r
        self._render(r)

    # ---------- 渲染 ----------
    def _render(self, r: dict):
        if "method" not in r:
            # 查卦结果（get_gua 原始结构）：归一化为起卦渲染结构
            r = dict(r)
            r["ben_symbol"] = r["symbol"]
            r["ben_gua"] = r["name"]
            r["ben_upper"] = r.get("upper", "")
            r["ben_lower"] = r.get("lower", "")
            r["ben_upper_symbol"] = r.get("upper_symbol") or r.get("upper", "")
            r["ben_lower_symbol"] = r.get("lower_symbol") or r.get("lower", "")
            r["ben_wuxing"] = r.get("wuxing", "")
            r["dong_yao"] = None
            r["bian_gua"] = None
            r.setdefault("time_note", "")
            r["method"] = "查卦"

        self.title.setText(f"{r['ben_symbol']} {r['ben_gua']}卦 · {r['method']}")
        self.subtitle.setText(r.get("time_note", ""))
        self.ben.setText(
            f"上{r['ben_upper_symbol']} 下{r['ben_lower_symbol']}"
            f"（{r['ben_upper']}/{r['ben_lower']}） · 五行属{r['ben_wuxing']}")
        self.guaci.setText(f"卦辞：{r['guaci']}")
        self.ji.setText(f"吉凶：{r['ji']}")
        self.ji.setStyleSheet(
            f"font-size: {theme.fs(17)}px; font-weight: bold; {theme.grade_qss(r['ji'])}")

        if "coins" in r:
            # 铜钱法：逐爻展示
            yao_txt = []
            n_move = 0
            for c in r["coins"]:
                i = c["position"] - 1
                yao_name = r["yaoci"][i]["name"]
                yao_txt.append(f"{yao_name} {_COIN_LABEL[c['backs']]}")
                if c["moving"]:
                    n_move += 1
            self.dong.setText("六爻（自下而上）：" + "　".join(yao_txt))
            if r["dong_yao"] is not None:
                suffix = f"（共{n_move}爻动，取此爻为用神爻）" if n_move > 1 else ""
                self.dong.setText(
                    self.dong.text() + f"\n动爻：{r['dong_yao_name']} —— "
                    f"{r['dong_yao_text']}{suffix}")
            else:
                self.dong.setText(self.dong.text() + "\n六爻皆静，无动爻")
        elif r["dong_yao"] is not None:
            self.dong.setText(f"动爻：{r['dong_yao_name']} —— {r['dong_yao_text']}")
        else:
            self.dong.setText("六爻皆静，无动爻")

        if r["bian_gua"]:
            self.bian.setText(f"变卦：{r['bian_symbol']} {r['bian_gua']}卦（{r['bian_guaci']}）")
        else:
            self.bian.setText("")

        self.yun.setText(f"整体运势：{r['yun']}")
        self.shiye.setText(f"事业：{r['shiye']}")
        self.ganqing.setText(f"感情：{r['ganqing']}")
        self.caiyun.setText(f"财运：{r['caiyun']}")

    def last_result(self) -> Optional[dict]:
        """最近一次起卦/查卦结果（供主窗口组装 AI 提示词）。"""
        return self._result

    def _copy(self):
        if self._result:
            copy_text(zhouyi.to_text(self._result))
