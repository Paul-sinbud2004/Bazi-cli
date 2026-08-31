# -*- coding: utf-8 -*-
"""
字体管理
========
1. 取消固定中文字体硬编码：默认按优先级探测系统已安装的优质中文字体；
2. 枚举系统中所有支持简体中文的合法字体，供用户自定义选择；
3. 字体 / 字号配置持久化（QSettings），重启自动生效。

本模块仅依赖 Qt 非可视化类，可独立测试。
"""
from __future__ import annotations

from typing import Optional

from PyQt6.QtGui import QFont, QFontDatabase
from PyQt6.QtWidgets import QApplication

from utils import config as cfg

# 键名
KEY_FAMILY = "font_family"   # "" = 跟随系统默认
KEY_SIZE = "font_size"        # 基准字号（px，默认 14）

DEFAULT_SIZE = 14
MIN_SIZE, MAX_SIZE = 9, 32

# 自动探测优先级：古风衬线优先，其次楷体，再次通用中文字体
_PREFERRED = [
    "Noto Serif CJK SC", "Noto Serif SC", "Source Han Serif SC", "Source Han Serif CN",
    "Source Han Serif TC", "AR PL UMing CN", "AR PL UKai CN", "WenQuanYi Zen Hei",
    "WenQuanYi Micro Hei",
    "STZhongsong", "STSong", "STKaiti", "Songti SC", "Kaiti SC",
    "SimSun", "KaiTi", "STXihei", "Microsoft YaHei", "PingFang SC", " Hiragino Sans GB",
    "Droid Sans Fallback",
]


# ---------- 枚举系统字体 ----------
def chinese_families() -> list[str]:
    """当前系统已安装、且支持简体中文渲染的全部字体族（排序）。"""
    try:
        db = QFontDatabase
        families = db.families()
    except Exception:  # noqa: BLE001 - 无 QApplication 等异常时退化为空
        return []
    out = []
    for f in families:
        try:
            ws = db.writingSystems(f)
        except Exception:  # noqa: BLE001
            continue
        from PyQt6.QtGui import QFontDatabase as QFD
        if QFD.WritingSystem.SimplifiedChinese in ws:
            out.append(f)
    return sorted(out)


def default_family() -> str:
    """按优先级探测系统最佳中文字体；找不到任何中文字体时返回 ""（跟随系统）。"""
    installed = set(chinese_families())
    for name in _PREFERRED:
        n = name.strip()
        if n in installed:
            return n
    # 没有命中优先列表：若系统存在任一中文字体则取排序后的第一个
    cands = [c for c in sorted(installed)
             if not c.startswith(".") and "@" not in c]
    return cands[0] if cands else ""


# ---------- 配置读写 ----------
def load_font_config() -> tuple[str, int]:
    """读取用户字体配置；未设置过时返回自动探测的默认值。"""
    family = cfg.get(KEY_FAMILY, None)
    if family is None:
        family = default_family()
    size = cfg.get(KEY_SIZE, DEFAULT_SIZE)
    try:
        size = int(size)
    except (TypeError, ValueError):
        size = DEFAULT_SIZE
    size = max(MIN_SIZE, min(MAX_SIZE, size))
    return str(family), size


def save_font_config(family: str, size: int) -> None:
    cfg.set(KEY_FAMILY, str(family))
    cfg.set(KEY_SIZE, int(max(MIN_SIZE, min(MAX_SIZE, size))))


def reset_font_config() -> None:
    """恢复默认（自动探测）。"""
    cfg.set(KEY_FAMILY, default_family())
    cfg.set(KEY_SIZE, DEFAULT_SIZE)


# ---------- 应用到 QApplication ----------
def app_font(family: str, size: int) -> Optional[QFont]:
    """构造全局 QFont；family 为空返回 None（交给系统默认）。"""
    if not family:
        return None
    f = QFont(family)
    f.setPixelSize(size)
    f.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
    return f
