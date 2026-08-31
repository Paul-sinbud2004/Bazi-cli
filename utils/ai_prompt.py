# -*- coding: utf-8 -*-
"""
AI 提示词一键生成
==================
把排盘结果组装成一段结构化、可直接粘贴到任意 AI 助手的命理分析提示词。
纯逻辑实现，无 UI 依赖；配合剪贴板即可"一键复制"。

生成策略：
- 标题说明 + 角色设定（资深命理师，依据传统典籍，条理清晰、避免迷信夸大）
- 出生信息与校正说明（真太阳时是否启用）
- 八字详盘：四柱/十神/藏干/纳音/强弱/格局/大运
- 紫微斗数：命身宫/五行局/四化/十二宫主辅星/大限
- 可选附加：已抽灵签、已起六十四卦
- 明确要求输出结构（分节、结论先行、给出建议）
"""
from __future__ import annotations

from typing import Any, Optional

from algorithm.bazi import to_text as bazi_text
from algorithm.ziwei import to_text as ziwei_text
from algorithm.lingqian import to_text as qian_text
from algorithm.zhouyi import to_text as gua_text


def _fmt_birth(profile: dict) -> str:
    name = profile.get("name") or "（未填写）"
    gender = profile.get("gender", "男")
    date = profile.get("solar_date", "")
    t = profile.get("solar_time", "12:00")
    lon = profile.get("longitude", 120.0)
    use_ts = profile.get("use_true_solar", False)
    ts = profile.get("true_solar_display", "")
    lines = [
        f"- 姓名/称呼：{name}",
        f"- 性别：{gender}",
        f"- 公历出生：{date} {t}",
        f"- 出生地经度：{lon}°E",
    ]
    if use_ts and ts:
        lines.append(f"- 真太阳时（已校正）：{ts}")
    return "\n".join(lines)


def build_prompt(profile: dict, bazi: dict, ziwei: dict,
                 qian: Optional[dict] = None, gua: Optional[dict] = None) -> str:
    """生成完整 AI 提示词。bazi/ziwei 为排盘结果 dict，qian/gua 可选。"""
    sections: list[str] = [
        "你是一位精通中国传统命理（子平八字、紫微斗数、周易）的资深命理师。",
        "请依据我提供的排盘结果，结合《渊海子平》《三命通会》《紫微斗数全书》《周易》等典籍的传统论断方法，",
        "条理清晰、客观理性地进行分析。请避免宿命论与夸大恐吓，重事实、重趋势、重建议。",
        "",
        "【出生信息】",
        _fmt_birth(profile),
        "",
        "【八字排盘】",
        bazi_text(bazi),
        "",
        "【紫微斗数排盘】",
        ziwei_text(ziwei),
    ]

    if qian:
        sections += ["", "【黄大仙灵签】", qian_text(qian)]

    if gua:
        sections += ["", "【周易六十四卦】", gua_text(gua)]

    sections += [
        "",
        "【请按以下结构分析】",
        "1. 八字论断：日主强弱、格局喜忌、五行流通，大运走势与关键年份。",
        "2. 紫微论断：命身宫组合、十二宫吉凶、四化牵引，大限趋势。",
        "3. 综合结论：事业、财运、感情、健康四方面的主要特征与建议。",
        "4. 趋吉避凶：给出 3-5 条具体、可执行的建议（如方位、颜色、行业、心态等）。",
    ]

    if qian:
        sections.append("5. 结合灵签所问之事，解读签意并给出指引。")
    if gua:
        sections.append("6. 结合卦象与动爻，解读当前时局与应对之道。")

    sections.append("请用简体中文，分节作答，结论先行，控制在 1200 字以内。")
    return "\n".join(sections)


def quick_prompt(profile: dict, bazi: dict, ziwei: dict) -> str:
    """快捷版：仅八字+紫微，不附带占卜结果。"""
    return build_prompt(profile, bazi, ziwei)
