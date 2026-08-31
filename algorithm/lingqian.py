# -*- coding: utf-8 -*-
"""
黄大仙灵签（100签）抽签算法
============================
签诗数据来源：啬色园官方数据集（经 kaucim.ai 整理，已简体化，见 data/lingqian100.json）。
解读释义：data/lingqian_notes.py（解曰 / 典故 / 运势）。
纯算法实现，无 UI 依赖。
"""
from __future__ import annotations

import json
import os
import random
from typing import Any, Optional

_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

_cache: Optional[list] = None


def _load() -> list[dict[str, Any]]:
    global _cache
    if _cache is None:
        with open(os.path.join(_DATA_DIR, "lingqian100.json"), encoding="utf-8") as f:
            _cache = json.load(f)
    return _cache


def _notes() -> dict:
    from data import lingqian_notes
    return lingqian_notes.NOTES


def qiu_qian(seed: Optional[int] = None, number: Optional[int] = None) -> dict[str, Any]:
    """
    求签。number 指定签号（1-100）；否则随机抽取。
    返回签号/签题/吉凶/签诗四句/解读（解曰、典故、运势解析）。
    """
    items = _load()
    if number is not None:
        qian = next((x for x in items if x["number"] == number), None)
        if qian is None:
            raise ValueError(f"签号 {number} 不存在（范围 1-100）")
    else:
        rng = random.Random(seed)
        qian = rng.choice(items)

    notes = _notes().get(qian["number"], {})
    result = {
        "number": qian["number"],
        "title": qian["title"],
        "grade": qian["grade"],
        "poem": qian["poem"],
        "jie": notes.get("jie", ""),
        "diangu": notes.get("diangu", ""),
        "yunshi": notes.get("yunshi", ""),
    }
    return result


def list_all() -> list[dict[str, Any]]:
    return _load()


def to_text(result: dict[str, Any]) -> str:
    lines = [
        f"第{result['number']}签　{result['title']}　【{result['grade']}】",
        "",
        *result["poem"],
        "",
        f"解曰：{result['jie']}",
        f"典故：{result['diangu']}",
        f"运势：{result['yunshi']}",
    ]
    return "\n".join(lines)
