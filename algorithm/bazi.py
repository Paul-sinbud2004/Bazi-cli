# -*- coding: utf-8 -*-
"""
八字（子平法）排盘算法
======================
四柱、大运、流年由行业标准库 lunar_python（lunar-java 官方移植版）生成，
保证节气换月、换年准确；十神 / 藏干 / 纳音 / 强弱 / 格局为本模块
基于《渊海子平》规则整理（数据表见 data/ganzhi.py）。
纯算法实现，无任何 UI 依赖。
"""
from __future__ import annotations

from typing import Any, Optional

from lunar_python import Solar

from data.ganzhi import (
    BRANCHES, STEMS, STEM_WUXING, BRANCH_WUXING, CANG_GAN, SHENG, KE,
    CHANGSHENG_TABLE, CHANGSHENG_NAMES, shishen, get_nayin,
)

# 十神五行属性颜色/分类用
_SHISHEN_TYPE = {
    "比肩": "比劫", "劫财": "比劫",
    "食神": "食伤", "伤官": "食伤",
    "偏财": "财", "正财": "财",
    "七杀": "官杀", "正官": "官杀",
    "偏印": "印", "正印": "印",
}

# 格局（月令本气十神 → 格局名）
_GEJU = {
    "正官": "正官格", "七杀": "七杀格",
    "正财": "正财格", "偏财": "偏财格",
    "正印": "正印格", "偏印": "偏印格",
    "食神": "食神格", "伤官": "伤官格",
    "比肩": "建禄格", "劫财": "羊刃格",
}


def _chang_sheng(day_gan: str, branch: str) -> str:
    """日主在某地支的十二长生状态。"""
    wx = STEM_WUXING[day_gan]
    yy = 1 if day_gan in "甲丙戊庚壬" else 0
    seq = CHANGSHENG_TABLE.get((wx, yy), [])
    if branch in seq:
        return CHANGSHENG_NAMES[seq.index(branch)]
    return ""


def _strength_score(day_gan: str, gan_list: list[str], branch_list: list[str]) -> int:
    """
    日主强弱计分（简化但合理的传统加权法）：
      + 月令（本气）是否生扶日主：生扶 +3，克泄 +3(负)
      + 四支藏干通根：本气 1.2 分、中气 0.8 分、余气 0.5 分（同五行）
      + 天干比劫 +1、印星 +0.8；官杀 -1、财 -1、食伤 -1
    得分 > 0 为身强，< 0 为身弱。
    """
    score = 0
    day_wx = STEM_WUXING[day_gan]

    # 月令
    month_branch = branch_list[1]
    cang = CANG_GAN.get(month_branch, [])
    if cang:
        benqi = cang[0]
        if STEM_WUXING[benqi] == day_wx:
            score += 3
        elif SHENG.get(STEM_WUXING[benqi]) == day_wx:   # 印生我
            score += 2
        elif KE.get(day_wx) == STEM_WUXING[benqi]:       # 我克财
            score -= 2
        else:
            score -= 2

    # 地支通根（除月令外）
    for i, br in enumerate(branch_list):
        if i == 1:
            continue
        for j, cg in enumerate(CANG_GAN.get(br, [])):
            if STEM_WUXING[cg] == day_wx:
                score += {0: 1.2, 1: 0.8, 2: 0.5}.get(j, 0.5)

    # 天干生扶克泄
    for i, g in enumerate(gan_list):
        if i == 0 or g == day_gan:
            continue
        wx = STEM_WUXING[g]
        if wx == day_wx:
            score += 1
        elif SHENG.get(wx) == day_wx:
            score += 0.8
        else:
            score -= 1

    return round(score, 1)


def _geju(day_gan: str, gan_list: list[str], branch_list: list[str]) -> str:
    """
    取格：以月令本气十神定格；
    月令本气为比劫（建禄/羊刃）时，取月令中气/余气且透干者为格，
    否则按本气。
    """
    month_branch = branch_list[1]
    cang = CANG_GAN.get(month_branch, [])
    if not cang:
        return "无格"

    # 优先：月令透干之藏干定格
    for cg in cang:
        if cg in gan_list:
            ss = shishen(day_gan, cg)
            if ss in _GEJU:
                return _GEJU[ss]
    # 其次：月令本气
    ss = shishen(day_gan, cang[0])
    return _GEJU.get(ss, "无格")


def _pillar_detail(day_gan: str, gan: str, zhi: str) -> dict[str, Any]:
    """单柱详情：天干/地支/五行/阴阳/藏干(含十神)/纳音/十神"""
    cang = CANG_GAN.get(zhi, [])
    cang_detail = [
        {"gan": cg, "shishen": shishen(day_gan, cg)}
        for cg in cang
    ]
    return {
        "gan": gan,
        "zhi": zhi,
        "ganzhi": gan + zhi,
        "gan_wuxing": STEM_WUXING[gan],
        "zhi_wuxing": BRANCH_WUXING[zhi],
        "gan_yinyang": "阳" if gan in "甲丙戊庚壬" else "阴",
        "nayin": get_nayin(gan + zhi),
        "shishen": shishen(day_gan, gan),
        "canggan": cang_detail,
    }


def paipan(solar_year: int, solar_month: int, solar_day: int,
           solar_hour: int, solar_minute: int = 0, gender: str = "男") -> dict[str, Any]:
    """
    八字排盘主入口（公历输入）。

    返回 dict：
      solar / lunar 字符串、四柱（含十神/藏干/纳音）、日主、
      强弱（得分/判断）、格局、起运（岁/月/日、顺逆）、大运列表（含流年）。
    """
    solar = Solar.fromYmdHms(solar_year, solar_month, solar_day, solar_hour, solar_minute, 0)
    lunar = solar.getLunar()
    ec = lunar.getEightChar()

    day_gan = ec.getDayGan()
    pillars_raw = [
        (ec.getYearGan(), ec.getYearZhi()),
        (ec.getMonthGan(), ec.getMonthZhi()),
        (ec.getDayGan(), ec.getDayZhi()),
        (ec.getTimeGan(), ec.getTimeZhi()),
    ]
    pillars = [_pillar_detail(day_gan, g, z) for g, z in pillars_raw]

    # 强弱
    gan_list = [g for g, _ in pillars_raw]
    branch_list = [z for _, z in pillars_raw]
    score = _strength_score(day_gan, gan_list, branch_list)
    strength = "身强" if score > 0 else ("身弱" if score < 0 else "中和")
    geju = _geju(day_gan, gan_list, branch_list)

    # 胎元（月柱天干+1、地支+3）、命宫（八字命宫：子起正月逆数至生月，再起子时顺数至生时）
    # —— lunar_python 自带 getTaiYuan / getMingGong / getShenGong
    tai_yuan = ec.getTaiYuan()
    ming_gong8 = ec.getMingGong()
    shen_gong8 = ec.getShenGong()

    # 大运
    yun = ec.getYun(1 if gender == "男" else 0)
    start_year = yun.getStartYear()
    start_month = yun.getStartMonth()
    start_day = yun.getStartDay()
    forward = yun.isForward()

    dayun_list: list[dict[str, Any]] = []
    for d in yun.getDaYun():
        gz = d.getGanZhi()
        if not gz:          # idx 0 为出生至起运的过渡段（干支为空），跳过
            continue
        gan2, zhi2 = gz[0], gz[1]
        item = {
            "index": d.getIndex(),
            "ganzhi": gz,
            "gan": gan2,
            "zhi": zhi2,
            "start_age": d.getStartAge(),
            "end_age": d.getEndAge(),
            "start_year": d.getStartYear(),
            "end_year": d.getEndYear(),
            "nayin": get_nayin(gz),
            "shishen": shishen(day_gan, gan2),
            "liunian": [
                {"year": y.getYear(), "ganzhi": y.getGanZhi(), "age": y.getAge()}
                for y in d.getLiuNian()
            ],
        }
        dayun_list.append(item)

    # 日主十二长生（对四支）
    changsheng = {b: _chang_sheng(day_gan, b) for b in branch_list}

    result: dict[str, Any] = {
        "solar_text": f"{solar_year}年{solar_month}月{solar_day}日 {solar_hour:02d}:{solar_minute:02d}",
        "lunar_text": f"{lunar.getYearInGanZhi()}年{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}日 {ec.getTimeZhi()}时",
        "gender": gender,
        "pillars": pillars,
        "day_master": day_gan,
        "day_master_wuxing": STEM_WUXING[day_gan],
        "strength_score": score,
        "strength": strength,
        "geju": geju,
        "tai_yuan": tai_yuan,
        "ming_gong": ming_gong8,
        "shen_gong": shen_gong8,
        "changsheng": changsheng,
        "dayun_start": {"year": start_year, "month": start_month, "day": start_day},
        "dayun_forward": "顺排" if forward else "逆排",
        "dayun": dayun_list,
    }
    return result


def to_text(result: dict[str, Any]) -> str:
    """八字排盘转可读文本。"""
    p = result["pillars"]
    lines = [
        f"【八字排盘】{result['solar_text']}　{result['lunar_text']}",
        f"性别：{result['gender']}　日主：{result['day_master']}（{result['day_master_wuxing']}）",
        "",
        "　　　年柱　　月柱　　日柱　　时柱",
    ]
    line_gan = "天干　" + "　".join(f"{x['gan']}({x['shishen']})" for x in p)
    line_zhi = "地支　" + "　".join(f"{x['zhi']}({x['zhi_wuxing']})" for x in p)
    line_nayin = "纳音　" + "　".join(f"{x['nayin']}" for x in p)
    lines += [line_gan, line_zhi, line_nayin]
    for i, name in enumerate(["年", "月", "日", "时"]):
        cang = "、".join(f"{c['gan']}{c['shishen']}" for c in p[i]["canggan"])
        lines.append(f"{name}支藏干：{cang}")
    lines.append(f"强弱：{result['strength']}（得分 {result['strength_score']}）　格局：{result['geju']}")
    lines.append(f"胎元：{result['tai_yuan']}　命宫：{result['ming_gong']}　身宫：{result['shen_gong']}")
    lines.append(f"起运：{result['dayun_start']['year']}岁{result['dayun_start']['month']}个月"
                 f"{result['dayun_start']['day']}天，{result['dayun_forward']}")
    lines.append("大运：")
    for d in result["dayun"]:
        ly = "、".join(f"{x['year']}{x['ganzhi']}" for x in d["liunian"][:5])
        lines.append(f"  {d['start_age']}-{d['end_age']}岁 {d['ganzhi']}({d['shishen']}) "
                     f"[{d['start_year']}-{d['end_year']}] 流年:{ly}...")
    return "\n".join(lines)


def get_lunar_info(solar_year: int, solar_month: int, solar_day: int,
                   solar_hour: int, solar_minute: int = 0) -> dict[str, Any]:
    """取农历信息（供紫微斗数排盘/UI 显示）。"""
    solar = Solar.fromYmdHms(solar_year, solar_month, solar_day, solar_hour, solar_minute, 0)
    lunar = solar.getLunar()
    m = lunar.getMonth()
    return {
        "year_ganzhi": lunar.getYearInGanZhi(),
        "month_ganzhi": lunar.getMonthInGanZhi(),
        "day_ganzhi": lunar.getDayInGanZhi(),
        "month": abs(m),
        "day": lunar.getDay(),
        "month_cn": lunar.getMonthInChinese(),
        "day_cn": lunar.getDayInChinese(),
        "leap": m < 0,
        "hour_branch": lunar.getTimeZhi(),
        "hour_index": ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"].index(lunar.getTimeZhi()),
        "shengxiao": lunar.getYearShengXiao(),
        "jieqi": lunar.getPrevJieQi().getName() if lunar.getPrevJieQi() else "",
    }
