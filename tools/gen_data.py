#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
destiny_cn 数据生成脚本（构建期工具，非运行时依赖）
=====================================================
将公开标准数据集（啬色园黄大仙100签官方数据集 / open-iching 周易64卦结构化数据）
转换为简体中文 JSON，供程序 data/ 目录加载。

数据来源：
1. 黄大仙灵签100签：https://www.kaucim.ai/datasets/wong-tai-sin-kau-cim-100.json
   （源自香港啬色园黄大仙祠官方签问系统，单一权威来源）
2. 周易六十四卦卦辞爻辞：https://github.com/john-walks-slow/open-iching
   （《周易》经典原文结构化数据）

运行：python tools/gen_data.py
输出：data/lingqian100.json、data/gua64.json
"""
import json
import os
from opencc import OpenCC

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
SRC_WONG = "/tmp/wong_official.json"
SRC_ICHING = "/tmp/iching.json"

# ---- 周易原文勘误（对照通行本《周易》） ----
ICHING_FIX = {
    ("乾", "九二"): "见龙在田，利见大人。",
}

# 先天八卦序号（梅花易数起卦用）：乾1 兑2 离3 震4 巽5 坎6 艮7 坤8
XIAN_TIAN = {"乾": 1, "兑": 2, "离": 3, "震": 4, "巽": 5, "坎": 6, "艮": 7, "坤": 8}
# 八纯卦五行属性（五行卦性）
TRIGRAM_WUXING = {"乾": "金", "兑": "金", "离": "火", "震": "木", "巽": "木", "坎": "水", "艮": "土", "坤": "土"}
# 八卦卦象符号
TRIGRAM_SYMBOL = {"乾": "☰", "兑": "☱", "离": "☲", "震": "☳", "巽": "☴", "坎": "☵", "艮": "☶", "坤": "☷"}


def to_simplified(text):
    """繁体转简体（转换失败时原样返回）"""
    try:
        cc = OpenCC("t2s")
        return cc.convert(text)
    except Exception:
        return text


def gen_lingqian():
    with open(SRC_WONG, encoding="utf-8") as f:
        data = json.load(f)
    records = data["records"]
    assert len(records) == 100, f"灵签记录数异常: {len(records)}"
    signs = []
    for rec in records:
        poem = to_simplified(rec["poemZhHant"])
        # 签诗按空格拆为四句
        lines = [ln.strip() for ln in poem.split() if ln.strip()]
        if len(lines) == 2:  # 若官方文本为两句七言合并（如第100签），按每14字切分
            lines = [lines[0][: len(lines[0]) // 2], lines[0][len(lines[0]) // 2:],
                     lines[1][: len(lines[1]) // 2], lines[1][len(lines[1]) // 2:]]
        signs.append({
            "number": int(rec["number"]),
            "title": to_simplified(rec["titleZhHant"]),
            "grade": to_simplified(rec["gradeZhHant"]),
            "poem": lines,
        })
    out = os.path.join(DATA_DIR, "lingqian100.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(signs, f, ensure_ascii=False, indent=1)
    print(f"[灵签] {len(signs)} 签 → {out}")


def gen_gua():
    with open(SRC_ICHING, encoding="utf-8") as f:
        hexagrams = json.load(f)
    assert len(hexagrams) == 64
    out_list = []
    for g in hexagrams:
        lower, upper = g["combination"]  # open-iching: combination = [下卦, 上卦]
        lines = []
        for ln in g["lines"]:
            key = (g["name"], ln["name"])
            text = ICHING_FIX.get(key, ln["scripture"])
            lines.append({"name": ln["name"], "text": to_simplified(text)})
        out_list.append({
            "id": g["id"],
            "name": g["name"],
            "symbol": g["symbol"],
            "array": g["array"],          # 自下而上六爻，1=阳 0=阴
            "lower": lower,                # 下卦（内卦）
            "upper": upper,                # 上卦（外卦）
            "lower_symbol": TRIGRAM_SYMBOL[lower],
            "upper_symbol": TRIGRAM_SYMBOL[upper],
            "wuxing": TRIGRAM_WUXING[upper],  # 上卦五行（五行卦性）
            "xiantian_upper": XIAN_TIAN[upper],
            "xiantian_lower": XIAN_TIAN[lower],
            "guaci": to_simplified(g["scripture"]),
            "yaoci": lines,
        })
    out = os.path.join(DATA_DIR, "gua64.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(out_list, f, ensure_ascii=False, indent=1)
    print(f"[周易] {len(out_list)} 卦 → {out}")


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    gen_lingqian()
    gen_gua()
