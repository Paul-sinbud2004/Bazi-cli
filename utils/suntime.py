# -*- coding: utf-8 -*-
"""
真太阳时计算（天文均时差法）
==============================
真太阳时 = 地方平太阳时 + 均时差(EoT)
  地方平太阳时 = 北京时间 + (经度 - 120°) / 15 小时
  均时差采用 Bryan 公式（精度约 ±30 秒，命理排盘足够）。

说明：真太阳时校正需用户提供出生地经度；本模块纯函数，无 UI 依赖。
"""
from __future__ import annotations

import math
from datetime import datetime


def _day_of_year(dt: datetime) -> int:
    return dt.timetuple().tm_yday


def equation_of_time(dt: datetime) -> float:
    """均时差（分钟）。正值 = 真太阳时快于平太阳时。"""
    n = _day_of_year(dt)
    # 以年为周期的近似（Bryan 公式）
    b = 2.0 * math.pi * (n - 81) / 364.0
    eot = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)
    return eot


def to_true_solar(year: int, month: int, day: int, hour: int, minute: int,
                  longitude: float = 120.0) -> tuple[int, int, float]:
    """
    北京时间(东八区) → 真太阳时。

    返回 (true_hour, true_minute, 精确分钟数)。小时进位按四舍五入到分钟。
    longitude：出生地东经（度），中国境内 73~135。
    """
    dt = datetime(year, month, day, hour, minute)
    # 地方平太阳时（分钟，可为负/超24h）
    local_minutes = hour * 60 + minute + (longitude - 120.0) * 4.0
    # + 均时差
    true_minutes = local_minutes + equation_of_time(dt)
    # 归一到 0~1440
    true_minutes %= 1440.0
    h = int(true_minutes // 60)
    m = int(round(true_minutes % 60))
    if m == 60:
        m = 0
        h += 1
    h %= 24
    return h, m, true_minutes


def to_true_solar_text(year: int, month: int, day: int, hour: int, minute: int,
                       longitude: float = 120.0) -> str:
    """返回 "HH:MM" 文本。"""
    h, m, _ = to_true_solar(year, month, day, hour, minute)
    return f"{h:02d}:{m:02d}"
