# -*- coding: utf-8 -*-
"""
destiny_cn 算法层（无 UI 依赖，独立可测）
==========================================
统一入口：paipan_all() 一键排出八字 + 紫微斗数；lingqian() / qigua() 占卜。

模块：
  bazi     八字排盘（四柱/十神/藏干/纳音/强弱/格局/大运流年）
  ziwei    紫微斗数排盘（十二宫/安星/四化/五行局/大限）
  lingqian 黄大仙100签
  zhouyi   周易六十四卦起卦
"""
from __future__ import annotations

from typing import Any, Optional

from algorithm import bazi, ziwei


def get_lunar(year: int, month: int, day: int, hour: int = 12, minute: int = 0) -> dict[str, Any]:
    """公历 → 农历/干支信息（供输入页与排盘页复用）。"""
    return bazi.get_lunar_info(year, month, day, hour, minute)


def _normalize_leap_month(month: int, day: int, leap: bool, mode: str = "next") -> int:
    """
    紫微斗数闰月归一化（仅排本命盘时使用；八字用节气月，不受影响）。

    派别（三大主流，均见诸典籍/名家，本模块默认采用【next】）：
      next  闰月一律按下月推排（默认）。依据《紫微斗数全书》卷二·安命身例明文：
            "又若闰月正月生者要在二月内起安身命，凡有闰月具要依此为例"；
            陆斌兆《紫微斗数讲义》、倪海厦、梁湘润、王栽珊等遵此。
            即闰X月作X+1月，日数不变（闰十二月 → 次年正月）。
      half  十五分界（王亭之中州派、钦天门蔡明宏等）：初一至十五归上月、
            十六至月底归下月。此派多用于排命盘参考，亦为流月/斗君推算法则。
      same  闰月按当月（了无居士、慧耕、透派张耀文、钟义明等）。
    """
    if not leap:
        return month
    if mode == "same":
        return month
    if mode == "half":
        return month if day <= 15 else (month + 1 if month < 12 else 1)
    # next（默认）
    return month + 1 if month < 12 else 1


def paipan_all(year: int, month: int, day: int, hour: int, minute: int = 0,
               gender: str = "男", leap_month_mode: str = "next") -> dict[str, Any]:
    """
    一键完整排盘：八字 + 紫微斗数。
    返回 {"bazi": {...}, "ziwei": {...}, "lunar": {...}}

    leap_month_mode：紫微斗数闰月派别，"next"（默认，按下月）/"half"（十五分界）/"same"（当月）。
    """
    lunar = bazi.get_lunar_info(year, month, day, hour, minute)
    b = bazi.paipan(year, month, day, hour, minute, gender)
    # 紫微斗数专用：闰月归一化（八字仍用节气月，不受影响）
    zw_month = _normalize_leap_month(lunar["month"], lunar["day"], lunar["leap"], leap_month_mode)
    z = ziwei.paipan(
        year_gan=lunar["year_ganzhi"][0],
        year_zhi=lunar["year_ganzhi"][1],
        month=zw_month,
        day=lunar["day"],
        hour=lunar["hour_index"],
        gender=gender,
        lunar_year_text=lunar["year_ganzhi"] + "年",
    )
    return {"bazi": b, "ziwei": z, "lunar": lunar}


__all__ = ["bazi", "ziwei", "lingqian", "zhouyi", "get_lunar", "paipan_all"]
