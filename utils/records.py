# -*- coding: utf-8 -*-
"""
排盘 / 抽签 / 起卦记录（本地存储）
==================================
- 所有记录仅保存于本机 JSON 文件，不上传云端、不外发任何数据；
- 记录分三类：paipan（八字+紫微排盘）、lingqian（灵签）、zhouyi（六十四卦）；
- 每条记录含保存时间、标题、概要与完整结果 payload，供一键复现；
- 按时间倒序，上限 500 条（超出裁剪最旧记录）。

存储路径：跨平台用户数据目录（Linux: ~/.local/share/destiny_cn/records.json）。
"""
from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Optional

MAX_RECORDS = 500

KIND_PAIPAN = "paipan"
KIND_LINGQIAN = "lingqian"
KIND_ZHOUYI = "zhouyi"

KIND_LABEL = {
    KIND_PAIPAN: "排盘",
    KIND_LINGQIAN: "灵签",
    KIND_ZHOUYI: "卦象",
}


def _record_dir() -> Path:
    """用户数据目录（无 GUI 环境也能工作）。"""
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg).expanduser() / "destiny_cn"
    home = Path.home()
    if os.name == "nt":  # Windows
        return home / "AppData" / "Local" / "destiny_cn"
    if os.uname().sysname == "Darwin":  # macOS
        return home / "Library" / "Application Support" / "destiny_cn"
    return home / ".local" / "share" / "destiny_cn"


def record_path() -> Path:
    return _record_dir() / "records.json"


def _load() -> list[dict]:
    try:
        with open(record_path(), encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, list) else []
    except Exception:  # noqa: BLE001 - 文件不存在/损坏均视为空
        return []


def _save(records: list[dict]) -> None:
    p = record_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(records, fh, ensure_ascii=False, default=str)
    os.replace(tmp, p)


# ---------- API ----------
def add(kind: str, title: str, summary: str, payload: Any) -> dict:
    """新增一条记录并落盘。返回该记录。"""
    rec = {
        "id": uuid.uuid4().hex,
        "kind": kind,
        "ts": time.time(),
        "time": time.strftime("%Y-%m-%d %H:%M"),
        "title": str(title),
        "summary": str(summary),
        "payload": payload,
    }
    records = _load()
    records.insert(0, rec)
    if len(records) > MAX_RECORDS:
        records = records[:MAX_RECORDS]
    _save(records)
    return rec


def all_records(kind: Optional[str] = None) -> list[dict]:
    """全部记录，按时间倒序；kind 过滤可选。"""
    records = _load()
    if kind:
        records = [r for r in records if r.get("kind") == kind]
    return sorted(records, key=lambda r: r.get("ts", 0), reverse=True)


def remove(rid: str) -> bool:
    records = _load()
    left = [r for r in records if r.get("id") != rid]
    if len(left) != len(records):
        _save(left)
        return True
    return False


def clear(kind: Optional[str] = None) -> int:
    """清空记录（可按类型），返回删除条数。"""
    records = _load()
    if kind is None:
        _save([])
        return len(records)
    left = [r for r in records if r.get("kind") != kind]
    _save(left)
    return len(records) - len(left)
