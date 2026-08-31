# -*- coding: utf-8 -*-
"""
古风主题（宣纸白 / 墨黑 / 赭石红 / 暗黄）
=========================================
全局配色、字体与 QSS。所有页面共用，保证风格统一。
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

# ---------- 字体 ----------
# 优先使用系统古风衬线字体，缺失时回退。
FONT_FAMILY = ("\"Noto Serif CJK SC\", \"Source Han Serif SC\", \"Source Han Serif CN\", "
               "\"STZhongsong\", \"STSong\", \"KaiTi\", \"STKaiti\", \"SimSun\", serif")

# 四柱用色（金木水火土）
WUXING_COLOR = {"金": "#A67C2E", "木": "#3E6B4F", "水": "#2F5D7A",
                "火": "#8C3A2B", "土": "#7A6A45"}

QSS = f"""
* {{
    font-family: {FONT_FAMILY};
    font-size: 14px;
    color: {INK};
}}
QMainWindow, QWidget#root {{
    background-color: {BG};
}}
QLabel {{
    background: transparent;
}}
QLabel#appTitle {{
    font-size: 26px;
    font-weight: bold;
    color: {ACCENT};
    letter-spacing: 6px;
}}
QLabel#appSub {{
    font-size: 13px;
    color: {INK_SOFT};
    letter-spacing: 2px;
}}
QLabel#pageTitle {{
    font-size: 20px;
    font-weight: bold;
    color: {ACCENT};
    padding-left: 10px;
    border-left: 4px solid {GOLD};
}}
QLabel#sectionTitle {{
    font-size: 16px;
    font-weight: bold;
    color: {INK};
    padding-left: 8px;
    border-left: 3px solid {GOLD};
}}
QLabel#muted {{
    color: {INK_SOFT};
    font-size: 13px;
}}
QPushButton {{
    background-color: {CARD};
    border: 1px solid {GOLD};
    border-radius: 6px;
    padding: 7px 18px;
    color: {ACCENT};
    font-size: 14px;
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
    font-size: 15px;
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
QMessageBox {{
    background-color: {CARD};
}}
QToolTip {{
    background-color: {CARD};
    color: {INK};
    border: 1px solid {GOLD};
    padding: 4px;
}}
"""


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
