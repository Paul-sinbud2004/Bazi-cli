# -*- coding: utf-8 -*-
"""
古风主题（宣纸白 / 墨黑 / 赭石红 / 暗黄）
=========================================
全局配色、字体与 QSS。所有页面共用，保证风格统一。

字体策略（v2.1.0）：
  - 不再硬编码固定中文字体；由 utils.fontman 探测系统优质中文字体或用户自选；
  - BASE_SIZE 为设计基准字号（14px），fs(px) 按用户字号等比缩放，
    页面内联样式的 font-size 一律经 theme.fs() 换算，实现全局自适应；
  - rebuild_qss() 在字体/字号变化时重建 QSS，由主窗口重新应用并重建页面。
"""
from __future__ import annotations

# ---------- 配色（古风五色） ----------
BG        = "#F5EFDF"   # 宣纸白（窗体背景）
BG_SOFT   = "#EFE7D2"   # 略深宣纸（导航/边栏）
CARD      = "#FDF9EF"   # 卡片米白
CARD_BORDER = "#DCCFB0" # 卡片描边（竹简黄）
INK       = "#2B2620"   # 墨黑（主文字）
INK_SOFT  = "#6E6453"   # 次级文字（淡墨）
ACCENT    = "#8C3A2B"   # 赭石红（标题/强调/主按钮）
ACCENT_HOVER = "#A84A36"
GOLD      = "#B08D2E"   # 暗黄（装饰/次要强调）
GOLD_SOFT = "#E5D5A8"
LINE      = "#DCCFB0"   # 分隔线
OK        = "#3E6B4F"   # 吉（墨绿）
WARN      = "#B08D2E"   # 中（暗黄）
BAD       = "#8C3A2B"   # 凶（赭石红）

# 四柱用色（金木水火土）
WUXING_COLOR = {"金": "#A67C2E", "木": "#3E6B4F", "水": "#2F5D7A",
                "火": "#8C3A2B", "土": "#7A6A45"}

# ---------- 字体（动态） ----------
# 当前生效的字体族与字号（rebuild_font() 时刷新；"" 表示跟随系统默认）
FONT_FAMILY = ""
FONT_SIZE = 14
BASE_SIZE = 14  # 设计基准字号（px）

# 兼容旧引用：旧代码可能读取 theme.FONT_FAMILY 作为字体族字符串
_FONT_FALLBACK = ("\"Noto Serif CJK SC\", \"Source Han Serif SC\", \"Source Han Serif CN\", "
                  "\"STZhongsong\", \"STSong\", \"KaiTi\", \"STKaiti\", \"SimSun\", serif")


def rebuild_font() -> tuple[str, int]:
    """从配置读取字体设置并刷新本模块状态。返回 (family, size)。"""
    global FONT_FAMILY, FONT_SIZE
    from utils.fontman import load_font_config
    FONT_FAMILY, FONT_SIZE = load_font_config()
    return FONT_FAMILY, FONT_SIZE


def fs(px: float) -> int:
    """设计字号 → 当前字号等比缩放（最小 9px）。"""
    scale = FONT_SIZE / BASE_SIZE
    return max(9, round(px * scale))


def font_family_css() -> str:
    """字体族 QSS 片段：自选字体用引号包裹；空则回退优先级列表（跟随系统渲染）。"""
    if FONT_FAMILY:
        return f"\"{FONT_FAMILY}\""
    return _FONT_FALLBACK


# ---------- QSS（动态重建） ----------
def _build_qss() -> str:
    fam = font_family_css()
    return f"""
* {{
    font-family: {fam};
    font-size: {fs(14)}px;
    color: {INK};
}}
QMainWindow, QWidget#root {{
    background-color: {BG};
}}
QLabel {{
    background: transparent;
}}
QLabel#appTitle {{
    font-size: {fs(26)}px;
    font-weight: bold;
    color: {ACCENT};
    letter-spacing: 6px;
}}
QLabel#appSub {{
    font-size: {fs(13)}px;
    color: {INK_SOFT};
    letter-spacing: 2px;
}}
QLabel#pageTitle {{
    font-size: {fs(20)}px;
    font-weight: bold;
    color: {ACCENT};
    padding-left: 10px;
    border-left: 4px solid {GOLD};
}}
QLabel#sectionTitle {{
    font-size: {fs(16)}px;
    font-weight: bold;
    color: {INK};
    padding-left: 8px;
    border-left: 3px solid {GOLD};
}}
QLabel#muted {{
    color: {INK_SOFT};
    font-size: {fs(13)}px;
}}
QPushButton {{
    background-color: {CARD};
    border: 1px solid {GOLD};
    border-radius: 6px;
    padding: 7px 18px;
    color: {ACCENT};
    font-size: {fs(14)}px;
}}
QPushButton:hover {{
    background-color: {GOLD_SOFT};
}}
QPushButton:pressed {{
    background-color: {GOLD};
    color: {CARD};
}}
QPushButton#primary {{
    background-color: {ACCENT};
    color: {CARD};
    border: 1px solid {ACCENT};
    font-weight: bold;
}}
QPushButton#primary:hover {{
    background-color: {ACCENT_HOVER};
}}
QPushButton#nav {{
    background: transparent;
    border: none;
    border-left: 4px solid transparent;
    border-radius: 0;
    text-align: left;
    padding: 12px 18px;
    font-size: {fs(15)}px;
    color: {INK_SOFT};
}}
QPushButton#nav:hover {{
    background-color: {GOLD_SOFT};
    color: {INK};
}}
QPushButton#nav:checked {{
    background-color: {CARD};
    border-left: 4px solid {ACCENT};
    color: {ACCENT};
    font-weight: bold;
}}
QFrame#card {{
    background-color: {CARD};
    border: 1px solid {CARD_BORDER};
    border-radius: 10px;
}}
QFrame#divider {{
    background-color: {LINE};
    max-height: 1px;
    min-height: 1px;
    border: none;
}}
QLineEdit, QDateEdit, QTimeEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
    background-color: {CARD};
    border: 1px solid {CARD_BORDER};
    border-radius: 6px;
    padding: 6px 10px;
    color: {INK};
    selection-background-color: {GOLD};
}}
QLineEdit:focus, QDateEdit:focus, QTimeEdit:focus, QComboBox:focus {{
    border-color: {GOLD};
}}
QComboBox::drop-down {{
    border: none;
    width: 24px;
}}
QComboBox QAbstractItemView {{
    background-color: {CARD};
    border: 1px solid {CARD_BORDER};
    selection-background-color: {GOLD_SOFT};
    selection-color: {INK};
}}
QCheckBox {{
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 1px solid {GOLD};
    border-radius: 3px;
    background: {CARD};
}}
QCheckBox::indicator:checked {{
    background-color: {ACCENT};
    border-color: {ACCENT};
}}
QTableWidget {{
    background-color: {CARD};
    border: 1px solid {CARD_BORDER};
    border-radius: 6px;
    gridline-color: {LINE};
    selection-background-color: {GOLD_SOFT};
    selection-color: {INK};
}}
QHeaderView::section {{
    background-color: {BG_SOFT};
    color: {INK};
    border: none;
    border-bottom: 2px solid {GOLD};
    padding: 8px;
    font-weight: bold;
}}
QTabWidget::pane {{
    border: 1px solid {CARD_BORDER};
    background: {CARD};
    border-radius: 6px;
}}
QScrollArea {{
    border: none;
    background: transparent;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
}}
QScrollBar::handle:vertical {{
    background: {GOLD};
    border-radius: 5px;
    min-height: 30px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QTextEdit, QPlainTextEdit {{
    background-color: {CARD};
    border: 1px solid {CARD_BORDER};
    border-radius: 6px;
    color: {INK};
    selection-background-color: {GOLD_SOFT};
}}
QMessageBox, QDialog {{
    background-color: {CARD};
}}
QListWidget {{
    background-color: {CARD};
    border: 1px solid {CARD_BORDER};
    border-radius: 6px;
    selection-background-color: {GOLD_SOFT};
    selection-color: {INK};
}}
QListWidget::item {{
    padding: 10px 12px;
    border-bottom: 1px solid {LINE};
}}
QListWidget::item:selected {{
    background-color: {GOLD_SOFT};
}}
QToolTip {{
    background-color: {CARD};
    color: {INK};
    border: 1px solid {GOLD};
    padding: 4px;
}}
"""


def rebuild_qss() -> str:
    """字体设置变化后调用：刷新字体状态并重建 QSS。"""
    rebuild_font()
    global QSS
    QSS = _build_qss()
    return QSS


# 模块加载时初始化（无 QApplication 环境下安全降级）
try:
    QSS = rebuild_qss()
except Exception:  # noqa: BLE001
    QSS = _build_qss()


def wuxing_qss(wx: str) -> str:
    """五行 → 前景色 QSS 片段（用于十神/纳音着色）"""
    color = WUXING_COLOR.get(wx, INK)
    return f"color: {color};"


def grade_qss(grade: str) -> str:
    """吉凶 → 前景色 QSS"""
    if any(g in grade for g in ("上上", "上吉", "吉", "大吉")):
        return f"color: {OK};"
    if any(g in grade for g in ("下下", "下", "凶", "大凶")):
        return f"color: {BAD};"
    return f"color: {WARN};"
