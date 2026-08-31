# -*- coding: utf-8 -*-
"""
紫微斗数排盘算法
================
依据《紫微斗数全书》传统安星规则实现，已与 zhycw.com / omigo-doushu 等
行业公开排盘规则交叉验证。纯算法实现，无任何 UI 依赖。

排盘流程：
1. 定命宫 / 身宫（寅宫起正月顺数至生月，再起子时逆/顺数至生时）
2. 布十二宫（命宫起逆时针：命宫、兄弟、夫妻、子女、财帛、疾厄、
   迁移、交友、官禄、田宅、福德、父母）
3. 定十二宫天干（五虎遁）
4. 定五行局（命宫干支纳音：金4局 木3局 水2局 火6局 土5局）
5. 安紫微星（五行局 + 农历生日查表），安十四主星
6. 安辅星（左辅右弼 / 文昌文曲 / 天魁天钺 / 禄存擎羊陀罗 / 火铃 / 地空地劫 / 天马）
7. 安四化（生年干四化表）
8. 定大限（阳男阴女顺行、阴男阳女逆行；命宫起，岁数=五行局数）
9. 命主 / 身主（生年支查表）
"""
from __future__ import annotations

from typing import Any, Optional

from data.ganzhi import BRANCHES, STEMS, STEM_YINYANG, get_nayin

# ---------- 常量表 ----------

# 五虎遁：寅宫天干
_WUHU_DUN = {
    "甲": "丙", "己": "丙",
    "乙": "戊", "庚": "戊",
    "丙": "庚", "辛": "庚",
    "丁": "壬", "壬": "壬",
    "戊": "甲", "癸": "甲",
}

# 五行局（纳音五行 → 局名）
_NAYIN_TO_JU = {"金": "金四局", "木": "木三局", "水": "水二局", "火": "火六局", "土": "土五局"}

# 五行局起限岁数
_JU_AGE = {"水二局": 2, "木三局": 3, "金四局": 4, "土五局": 5, "火六局": 6}

# 紫微星位置表（权威查表法，30日 × 5 局，地支 index 0=子）
# 来源：《紫微斗数全书》标准表，与 zhycw.com / 12ky / 易德轩 / FANzR 参考一致
_ZIWEI_TABLE = {
    # 水二局：丑寅寅卯卯辰辰巳巳午 午未未申申酉酉戌戌亥 亥子子丑丑寅寅卯卯辰
    "水二局": [1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7, 7, 8, 8, 9, 9, 10, 10, 11,
               11, 0, 0, 1, 1, 2, 2, 3, 3, 4],
    # 木三局：辰丑寅巳寅卯午卯辰未 辰巳申巳午酉午未戌未 申亥申酉子酉戌丑戌亥
    "木三局": [4, 1, 2, 5, 2, 3, 6, 3, 4, 7, 4, 5, 8, 5, 6, 9, 6, 7, 10, 7,
               8, 11, 8, 9, 0, 9, 10, 1, 10, 11],
    # 金四局：亥辰丑寅子巳寅卯丑午 卯辰寅未辰巳卯申巳午 辰酉午未巳戌未申午亥
    "金四局": [11, 4, 1, 2, 0, 5, 2, 3, 1, 6, 3, 4, 2, 7, 4, 5, 3, 8, 5, 6,
               4, 9, 6, 7, 5, 10, 7, 8, 6, 11],
    # 土五局：午亥辰丑寅未子巳寅卯 申丑午卯辰酉寅未辰巳 戌卯申巳午亥辰酉午未
    "土五局": [6, 11, 4, 1, 2, 7, 0, 5, 2, 3, 8, 1, 6, 3, 4, 9, 2, 7, 4, 5,
               10, 3, 8, 5, 6, 11, 4, 9, 6, 7],
    # 火六局：酉午亥辰丑寅戌未子巳 寅卯亥申丑午卯辰子酉 寅未辰巳丑戌卯申巳午
    "火六局": [9, 6, 11, 4, 1, 2, 10, 7, 0, 5, 2, 3, 11, 8, 1, 6, 3, 4, 0, 9,
               2, 7, 4, 5, 1, 10, 3, 8, 5, 6],
}

# 十四主星：紫微星系相对紫微偏移（逆时针为负）、天府星系相对天府偏移（顺时针为正）
_ZIWEI_OFFSET = {"紫微": 0, "天机": -1, "太阳": -3, "武曲": -4, "天同": -5, "廉贞": -8}
_TIANFU_OFFSET = {"天府": 0, "太阴": 1, "贪狼": 2, "巨门": 3, "天相": 4, "天梁": 5, "七杀": 6, "破军": 10}

# 左辅辰起正月顺数、右弼戌起正月逆数；文昌戌起子时逆数、文曲辰起子时顺数
_CHEN, _XU, _HAI = 4, 10, 11

# 禄存（年干 → 地支 index）
_LUCUN = {"甲": 2, "乙": 3, "丙": 5, "丁": 6, "戊": 5, "己": 6, "庚": 8, "辛": 9, "壬": 11, "癸": 0}

# 天魁 / 天钺（年干 → (魁, 钺)）
_KUIYUE = {
    "甲": (1, 7), "戊": (1, 7), "庚": (1, 7),
    "乙": (0, 8), "己": (0, 8),
    "丙": (11, 9), "丁": (11, 9),
    "壬": (3, 5), "癸": (3, 5),
    "辛": (6, 2),
}

# 天马（年支三合 → 马地）
_MA_GROUP = {
    frozenset([2, 6, 10]): 8,   # 寅午戌 → 申
    frozenset([8, 0, 4]): 2,    # 申子辰 → 寅
    frozenset([5, 9, 1]): 11,   # 巳酉丑 → 亥
    frozenset([11, 3, 7]): 5,   # 亥卯未 → 巳
}

# 火星 / 铃星起始宫（年支三合 → 子时宫位，顺数至生时）
_HUO_LING_START = {
    frozenset([2, 6, 10]): (1, 3),   # 寅午戌：火丑 铃卯
    frozenset([8, 0, 4]): (2, 10),   # 申子辰：火寅 铃戌
    frozenset([5, 9, 1]): (3, 10),   # 巳酉丑：火卯 铃戌
    frozenset([11, 3, 7]): (9, 10),  # 亥卯未：火酉 铃戌
}

# 生年干四化（甲...癸 → 星: 化）
_SIHUA = {
    "甲": {"廉贞": "化禄", "破军": "化权", "武曲": "化科", "太阳": "化忌"},
    "乙": {"天机": "化禄", "天梁": "化权", "紫微": "化科", "太阴": "化忌"},
    "丙": {"天同": "化禄", "天机": "化权", "文昌": "化科", "廉贞": "化忌"},
    "丁": {"太阴": "化禄", "天同": "化权", "天机": "化科", "巨门": "化忌"},
    "戊": {"贪狼": "化禄", "太阴": "化权", "右弼": "化科", "天机": "化忌"},
    "己": {"武曲": "化禄", "贪狼": "化权", "天梁": "化科", "文曲": "化忌"},
    "庚": {"太阳": "化禄", "武曲": "化权", "太阴": "化科", "天同": "化忌"},
    "辛": {"巨门": "化禄", "太阳": "化权", "文曲": "化科", "文昌": "化忌"},
    "壬": {"天梁": "化禄", "紫微": "化权", "左辅": "化科", "武曲": "化忌"},
    "癸": {"破军": "化禄", "巨门": "化权", "太阴": "化科", "贪狼": "化忌"},
}

# 命主（生年支 → 星）
_MING_ZHU = {0: "贪狼", 1: "巨门", 2: "禄存", 3: "文曲", 4: "廉贞", 5: "武曲",
             6: "破军", 7: "武曲", 8: "廉贞", 9: "文曲", 10: "禄存", 11: "巨门"}
# 身主（生年支 → 星）
_SHEN_ZHU = {0: "火星", 1: "天相", 2: "天梁", 3: "天同", 4: "文昌", 5: "天机",
             6: "火星", 7: "天相", 8: "天梁", 9: "天同", 10: "文昌", 11: "天机"}

# 十二宫名（逆时针排列顺序）
_PALACE_NAMES = ["命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄",
                 "迁移", "交友", "官禄", "田宅", "福德", "父母"]

# 主星五行（用于显示/解读）
_STAR_WUXING = {
    "紫微": "土", "天机": "木", "太阳": "火", "武曲": "金", "天同": "水",
    "廉贞": "火", "天府": "土", "太阴": "水", "贪狼": "木", "巨门": "水",
    "天相": "水", "天梁": "土", "七杀": "金", "破军": "水",
}

_HOUR_BRANCH = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]


def _branch_index(branch: str) -> int:
    return BRANCHES.index(branch)


def _shift(idx: int, step: int) -> int:
    return (idx + step) % 12


def _year_group(year_branch_idx: int) -> frozenset:
    for group in _HUO_LING_START:
        if year_branch_idx in group:
            return group
    return frozenset()


def _palace_gan(year_gan: str, palace_branch_idx: int) -> str:
    """按五虎遁求某地支宫的宫干。寅宫干由年干定，其余顺推。"""
    yin_gan = _WUHU_DUN[year_gan]
    yin_idx = 2  # 寅
    diff = (palace_branch_idx - yin_idx) % 12
    return STEMS[(STEMS.index(yin_gan) + diff) % 10]


def paipan(year_gan: str, year_zhi: str, month: int, day: int,
           hour: int, gender: str = "男", lunar_year_text: str = "") -> dict[str, Any]:
    """
    紫微斗数排盘主入口。

    参数：
      year_gan/year_zhi  生年干支（如 "甲"、"辰"）
      month/day          农历月、日（数字）。注意：闰月需由调用方先行按派别
                         归一化（见 algorithm.__init__._normalize_leap_month），
                         本函数假定传入的是已归一化的月份。
      hour               时辰 index（0=子时 ... 11=亥时）
      gender             "男" / "女"
      lunar_year_text    农历年文字（仅展示用，如 "甲辰年"）

    返回：
      dict：{ming_gong, shen_gong, wuxing_ju, ming_zhu, shen_zhu,
             sihua, palaces, dayun_start_age, dayun_forward, ...}
    """
    year_idx = _branch_index(year_zhi)
    year_gan2 = year_gan
    hour = hour % 12

    # ---- 1. 命宫 / 身宫 ----
    month_pos = _shift(2, month - 1)          # 寅起正月顺数
    ming = _shift(month_pos, -hour)           # 逆数时辰
    shen = _shift(month_pos, hour)            # 顺数时辰
    ming_branch = BRANCHES[ming]
    shen_branch = BRANCHES[shen]

    # ---- 2. 五行局（命宫干支纳音） ----
    ming_gan = _palace_gan(year_gan2, ming)
    ming_ganzhi = ming_gan + ming_branch
    nayin = get_nayin(ming_ganzhi)
    # 纳音名末字为五行（如 霹雳火 → 火、海中金 → 金）
    ju = _NAYIN_TO_JU.get(nayin[-1], "土五局") if nayin else "土五局"

    # ---- 3. 紫微星（权威查表法）→ 十四主星 ----
    ziwei = _ZIWEI_TABLE[ju][(day - 1) % 30]
    tianfu = (4 - ziwei) % 12

    major: dict[int, list[str]] = {i: [] for i in range(12)}
    for star, off in _ZIWEI_OFFSET.items():
        major[_shift(ziwei, off)].append(star)
    for star, off in _TIANFU_OFFSET.items():
        major[_shift(tianfu, off)].append(star)

    # ---- 4. 辅星 ----
    minor: dict[int, list[str]] = {i: [] for i in range(12)}
    minor[_shift(_CHEN, month - 1)].append("左辅")          # 辰起正月顺
    minor[_shift(_XU, -(month - 1))].append("右弼")         # 戌起正月逆
    minor[_shift(_XU, -hour)].append("文昌")                # 戌起子时逆
    minor[_shift(_CHEN, hour)].append("文曲")               # 辰起子时顺
    minor[_shift(_HAI, -hour)].append("地空")               # 亥起子时逆
    minor[_shift(_HAI, hour)].append("地劫")                # 亥起子时顺

    lucun = _LUCUN[year_gan2]
    minor[lucun].append("禄存")
    minor[_shift(lucun, 1)].append("擎羊")
    minor[_shift(lucun, -1)].append("陀罗")

    kui, yue = _KUIYUE[year_gan2]
    minor[kui].append("天魁")
    minor[yue].append("天钺")

    group = _year_group(year_idx)
    if group:
        ma = _MA_GROUP[group]
        minor[ma].append("天马")
        huo, ling = _HUO_LING_START[group]
        minor[_shift(huo, hour)].append("火星")
        minor[_shift(ling, hour)].append("铃星")

    # ---- 5. 四化（生年干） ----
    sihua_map = _SIHUA[year_gan2]          # {星: 化X}
    # 找出主星/辅星落宫并标注四化
    palace_sihua: dict[int, list[str]] = {i: [] for i in range(12)}
    for star, hua in sihua_map.items():
        # 主星或辅星所在宫
        found = None
        for i in range(12):
            if star in major[i] or star in minor[i]:
                found = i
                break
        if found is not None:
            palace_sihua[found].append(f"{star}{hua}")

    # ---- 6. 十二宫布列（命宫起逆时针） ----
    palaces: list[dict[str, Any]] = []
    for k in range(12):
        palace_idx = _shift(ming, -k)          # 逆时针
        branch = BRANCHES[palace_idx]
        gan = _palace_gan(year_gan2, palace_idx)
        palaces.append({
            "index": k,
            "name": _PALACE_NAMES[k],
            "branch": branch,
            "gan": gan,
            "ganzhi": gan + branch,
            "major": sorted(major[palace_idx], key=lambda s: list(_STAR_WUXING).index(s) if s in _STAR_WUXING else 99),
            "minor": sorted(minor[palace_idx]),
            "sihua": palace_sihua[palace_idx],
            "nayin": get_nayin(gan + branch),
        })

    # ---- 7. 大限 ----
    # 规则（《紫微斗数全书》权威）：阳男阴女顺行，阴男阳女逆行
    #   顺行 = 顺时针 = 地支递增方向（命→父母→福德→田宅→官禄→交友→迁移→疾厄→财帛→子女→夫妻→兄弟）
    #   逆行 = 逆时针 = 地支递减方向（命→兄弟→夫妻→子女→财帛→疾厄→迁移→交友→官禄→田宅→福德→父母）
    # 本模块 palaces 按逆时针（地支递减）布列：palaces[k] = 命宫 - k，
    #   故递减方向 = palaces 正向（idx=k），递增方向 = palaces 反向（idx=(12-k)%12）。
    forward = (gender == "男" and STEM_YINYANG[year_gan2] == 1) or \
              (gender == "女" and STEM_YINYANG[year_gan2] == 0)
    start_age = _JU_AGE[ju]
    for k, palace in enumerate(palaces):
        if forward:                       # 顺行 → 递增方向
            idx = (12 - k) % 12
        else:                             # 逆行 → 递减方向
            idx = k
        a = start_age + idx * 10
        palace["dayun"] = f"{a}-{a + 9}"

    result: dict[str, Any] = {
        "lunar_year": lunar_year_text or f"{year_gan2}{year_zhi}年",
        "year_gan": year_gan2,
        "year_zhi": year_zhi,
        "gender": gender,
        "lunar_month": month,
        "lunar_day": day,
        "hour_branch": _HOUR_BRANCH[hour],
        "ming_gong": ming_branch,
        "shen_gong": shen_branch,
        "ming_ganzhi": ming_ganzhi,
        "wuxing_ju": ju,
        "ming_zhu": _MING_ZHU[year_idx],
        "shen_zhu": _SHEN_ZHU[year_idx],
        "ziwei_branch": BRANCHES[ziwei],
        "tianfu_branch": BRANCHES[tianfu],
        "sihua_summary": [f"{s}{h}" for s, h in sihua_map.items()],
        "dayun_start_age": start_age,
        "dayun_forward": "顺行" if forward else "逆行",
        "palaces": palaces,
    }
    return result


def to_text(result: dict[str, Any]) -> str:
    """将排盘结果转为可读文本（供 AI 提示词 / 控制台预览）。"""
    lines = [
        f"【紫微斗数排盘】{result['lunar_year']} 农历{result['lunar_month']}月{result['lunar_day']}日 {result['hour_branch']}时",
        f"性别：{result['gender']}　命宫：{result['ming_gong']}　身宫：{result['shen_gong']}",
        f"五行局：{result['wuxing_ju']}　命主：{result['ming_zhu']}　身主：{result['shen_zhu']}",
        f"四化（{result['year_gan']}干）：{'、'.join(result['sihua_summary'])}",
        f"大限：{result['dayun_start_age']}岁起运，{result['dayun_forward']}",
        "",
    ]
    for p in result["palaces"]:
        major = " ".join(p["major"]) if p["major"] else "空"
        minor = " ".join(p["minor"]) if p["minor"] else ""
        hua = " ".join(p["sihua"]) if p["sihua"] else ""
        lines.append(
            f"{p['name']}({p['ganzhi']})大限{p['dayun']}：主星[{major}] "
            f"辅星[{minor}] {hua}".rstrip()
        )
    return "\n".join(lines)


# ---------- 便捷入口 ----------

def paipan_from_lunar(year_gan: str, year_zhi: str, lunar_month: int, lunar_day: int,
                      hour: int, gender: str = "男", year_ganzhi: str = "") -> dict[str, Any]:
    """由农历信息排盘。year_ganzhi 如 '甲辰'（可选，用于展示）。"""
    if year_ganzhi:
        year_gan = year_ganzhi[0]
        year_zhi = year_ganzhi[1]
    return paipan(year_gan, year_zhi, lunar_month, lunar_day, hour, gender,
                  lunar_year_text=f"{year_ganzhi or (year_gan + year_zhi)}年")
