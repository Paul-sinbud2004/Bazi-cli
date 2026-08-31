# -*- coding: utf-8 -*-
"""
周易六十四卦起卦算法
====================
卦辞 / 爻辞数据：data/gua64.json（《周易》通行本原文，已简体化）。
起卦方法（梅花易数）：
  1. 时间起卦：年支序数+月+日 → 上卦；年支序数+月+日+时辰序数 → 下卦；
     年支序数+月+日+时辰序数 → 动爻（余0取6）。
  2. 随机起卦：模拟三枚铜钱掷六次（3背=老阳动、0背=老阴动、2背=少阳、1背=少阴）。
本模块同时给出本卦、变卦、动爻爻辞与逐爻解释。纯算法实现，无 UI 依赖。
"""
from __future__ import annotations

import json
import os
import random
from typing import Any, Optional

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

_cache: Optional[list] = None
_map: Optional[dict] = None

# 八卦序（先天数）：乾1 兑2 离3 震4 巽5 坎6 艮7 坤8
TRIGRAM_ORDER = ["乾", "兑", "离", "震", "巽", "坎", "艮", "坤"]
TRIGRAM_INDEX = {name: i + 1 for i, name in enumerate(TRIGRAM_ORDER)}
# 八卦五行
TRIGRAM_WUXING = {"乾": "金", "兑": "金", "离": "火", "震": "木", "巽": "木", "坎": "水", "艮": "土", "坤": "土"}
# 八卦象征
TRIGRAM_IMAGE = {"乾": "天", "兑": "泽", "离": "火", "震": "雷", "巽": "风", "坎": "水", "艮": "山", "坤": "地"}
# 地支序数（梅花易数时间起卦用）：子1 ... 亥12
_BRANCH_NUM = {b: i + 1 for i, b in enumerate(["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"])}
# 时辰序数
_HOUR_NUM = {b: i + 1 for i, b in enumerate(["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"])}


def _load() -> list[dict[str, Any]]:
    global _cache
    if _cache is None:
        with open(os.path.join(_DATA_DIR, "gua64.json"), encoding="utf-8") as f:
            _cache = json.load(f)
    return _cache


def _map_by_lower_upper() -> dict:
    """(上卦, 下卦) → 卦 dict"""
    global _map
    if _map is None:
        _map = {(g["upper"], g["lower"]): g for g in _load()}
    return _map


def _gua_by_array(array: list[int]) -> Optional[dict]:
    for g in _load():
        if g["array"] == array:
            return g
    return None


def _notes() -> dict:
    from data import gua_notes
    return gua_notes.NOTES


def _hexagram(name_or_id) -> dict:
    """按卦名或 id 取卦"""
    if isinstance(name_or_id, int):
        return next(g for g in _load() if g["id"] == name_or_id)
    return next(g for g in _load() if g["name"] == name_or_id)


def _build_result(ben_gua: dict, dong_yao: Optional[int],
                  bian_gua: Optional[dict], method: str, seed: Optional[int]) -> dict[str, Any]:
    notes = _notes().get(ben_gua["id"], {})
    # 动爻爻辞
    dong_yao_text = ""
    dong_yao_name = ""
    if dong_yao is not None and 0 <= dong_yao < len(ben_gua["yaoci"]):
        dong_yao_text = ben_gua["yaoci"][dong_yao]["text"]
        dong_yao_name = ben_gua["yaoci"][dong_yao]["name"]
    # 若动爻为全卦（无具体爻动，如六爻皆静）则不显示动爻辞
    result = {
        "method": method,
        "ben_gua": ben_gua["name"],
        "ben_symbol": ben_gua["symbol"],
        "ben_upper": ben_gua["upper"],
        "ben_lower": ben_gua["lower"],
        "ben_upper_symbol": ben_gua["upper_symbol"],
        "ben_lower_symbol": ben_gua["lower_symbol"],
        "ben_wuxing": ben_gua["wuxing"],
        "guaci": ben_gua["guaci"],
        "array": ben_gua["array"],
        "yaoci": ben_gua["yaoci"],
        "dong_yao": dong_yao,              # 0-5 或 None
        "dong_yao_name": dong_yao_name,
        "dong_yao_text": dong_yao_text,
        "bian_gua": bian_gua["name"] if bian_gua else None,
        "bian_symbol": bian_gua["symbol"] if bian_gua else None,
        "bian_upper": bian_gua["upper"] if bian_gua else None,
        "bian_lower": bian_gua["lower"] if bian_gua else None,
        "bian_guaci": bian_gua["guaci"] if bian_gua else None,
        "ji": notes.get("ji", ""),
        "yun": notes.get("yun", ""),
        "shiye": notes.get("shiye", ""),
        "ganqing": notes.get("ganqing", ""),
        "caiyun": notes.get("caiyun", ""),
    }
    return result


def qigua_by_time(year_branch: str, lunar_month: int, lunar_day: int,
                  hour_branch: str) -> dict[str, Any]:
    """
    时间起卦（梅花易数）：
      上卦 = (年支数 + 月 + 日) % 8（余0取8）
      下卦 = (年支数 + 月 + 日 + 时数) % 8
      动爻 = (年支数 + 月 + 日 + 时数) % 6（余0取6）
    返回本卦/动爻/变卦/卦辞爻辞。
    """
    y = _BRANCH_NUM[year_branch]
    h = _HOUR_NUM[hour_branch]
    upper_num = (y + lunar_month + lunar_day) % 8 or 8
    lower_num = (y + lunar_month + lunar_day + h) % 8 or 8
    dong = (y + lunar_month + lunar_day + h) % 6 or 6

    upper = TRIGRAM_ORDER[upper_num - 1]
    lower = TRIGRAM_ORDER[lower_num - 1]
    ben_gua = _map_by_lower_upper()[(upper, lower)]

    # 变卦
    array = list(ben_gua["array"])
    dong_idx = dong - 1
    array[dong_idx] = 1 - array[dong_idx]
    bian_gua = _gua_by_array(array)

    return _build_result(ben_gua, dong_idx, bian_gua, "时间起卦", None)


def qigua_by_coins(seed: Optional[int] = None) -> dict[str, Any]:
    """
    铜钱摇卦：六爻自下而上，每爻三枚（背=阳）。
      三背 = 老阳(9) 动爻 → 阳
      二背 = 少阳(7) → 阳
      一背 = 少阴(8) → 阴
      零背 = 老阴(6) 动爻 → 阴
    动爻位置（可能有多个）取第一个动爻为「用神爻」展示，变卦按全部动爻变。
    """
    rng = random.Random(seed)
    coins: list[dict] = []
    array = []
    for _ in range(6):
        backs = sum(rng.randint(0, 1) for _ in range(3))
        if backs == 3:
            value, moving = 1, True
        elif backs == 2:
            value, moving = 1, False
        elif backs == 1:
            value, moving = 0, False
        else:
            value, moving = 0, True
        coins.append({"backs": backs, "value": value, "moving": moving})
        array.append(value)

    ben_gua = _gua_by_array(array)
    if ben_gua is None:
        raise RuntimeError("未能匹配卦象")

    # 变卦（全部动爻取反）
    bian_array = list(array)
    moving_idx = [i for i, c in enumerate(coins) if c["moving"]]
    for i in moving_idx:
        bian_array[i] = 1 - bian_array[i]
    bian_gua = _gua_by_array(bian_array)

    dong = moving_idx[0] if moving_idx else None
    result = _build_result(ben_gua, dong, bian_gua, "铜钱起卦", seed)
    result["coins"] = [
        {"position": i + 1, "backs": c["backs"], "value": c["value"], "moving": c["moving"]}
        for i, c in enumerate(coins)
    ]
    return result


def get_gua(gua_id: int) -> dict[str, Any]:
    """按卦序（1-64）取单卦详情"""
    g = _hexagram(gua_id)
    notes = _notes().get(g["id"], {})
    return {
        "id": g["id"],
        "name": g["name"],
        "symbol": g["symbol"],
        "array": g["array"],
        "lower": g["lower"],
        "upper": g["upper"],
        "guaci": g["guaci"],
        "yaoci": g["yaoci"],
        "wuxing": g["wuxing"],
        "ji": notes.get("ji", ""),
        "yun": notes.get("yun", ""),
        "shiye": notes.get("shiye", ""),
        "ganqing": notes.get("ganqing", ""),
        "caiyun": notes.get("caiyun", ""),
    }


def list_all() -> list[dict[str, Any]]:
    return _load()


def to_text(result: dict[str, Any]) -> str:
    lines = [
        f"【{result['method']}】",
        f"本卦：{result['ben_symbol']} {result['ben_gua']}（上{result['ben_upper']}下{result['ben_lower']}，{result['ben_wuxing']}）",
        f"卦辞：{result['guaci']}",
        f"吉凶：{result['ji']}",
    ]
    if result["dong_yao"] is not None:
        lines.append(f"动爻：{result['dong_yao_name']}（{result['dong_yao_text']}）")
    if result["bian_gua"]:
        lines.append(f"变卦：{result['bian_symbol']} {result['bian_gua']}（{result['bian_guaci']}）")
    lines += [
        f"整体运势：{result['yun']}",
        f"事业：{result['shiye']}",
        f"感情：{result['ganqing']}",
        f"财运：{result['caiyun']}",
    ]
    return "\n".join(lines)
