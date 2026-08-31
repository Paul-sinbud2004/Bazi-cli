# -*- coding: utf-8 -*-
"""
配置管理（QSettings 封装）
==========================
持久化：最近输入（姓名/性别/出生日期时间/经度/真太阳时开关）、
紫微闰月派别、界面偏好等。纯 Qt 依赖，无 UI 组件。
"""
from __future__ import annotations

import json
from typing import Any, Optional

from PyQt6.QtCore import QSettings

_ORG = "destiny_cn"
_APP = "destiny_cn"


def _settings() -> QSettings:
    return QSettings(_ORG, _APP)


def get(key: str, default: Any = None) -> Any:
    v = _settings().value(key, default)
    return v


def set(key: str, value: Any) -> None:
    _settings().setValue(key, value)


def get_json(key: str, default: Any = None) -> Any:
    raw = _settings().value(key, None)
    if raw is None:
        return default
    try:
        return json.loads(raw)
    except Exception:
        return default


def set_json(key: str, value: Any) -> None:
    _settings().setValue(key, json.dumps(value, ensure_ascii=False))


# ---------- 业务级便捷接口 ----------

DEFAULTS = {
    "name": "",
    "gender": "男",
    "solar_date": "",          # "YYYY-MM-DD"
    "solar_time": "12:00",
    "longitude": 120.0,        # 出生地经度（东经，用于真太阳时）
    "use_true_solar": False,   # 是否使用真太阳时校正
    "leap_month_mode": "next", # 紫微闰月派别：next/half/same
    "true_solar_display": "",  # 校正后的真太阳时（展示用）
}


def load_profile() -> dict:
    """读取完整用户档案（含默认值）。"""
    p = dict(DEFAULTS)
    saved = get_json("profile", {})
    if isinstance(saved, dict):
        p.update(saved)
    return p


def save_profile(profile: dict) -> None:
    set_json("profile", profile)


def load_birth() -> Optional[dict]:
    """便捷取出生信息（无则 None）"""
    p = load_profile()
    if not p.get("solar_date"):
        return None
    return p
