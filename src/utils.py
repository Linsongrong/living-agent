# Living Agent - 工具函数模块
"""
提供基础工具函数：路径处理、时间处理等
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional
from filelock import FileLock


# 全局锁实例
_state_lock: Optional[FileLock] = None


def get_lock(lock_path: str = None) -> FileLock:
    """
    获取文件锁实例
    """
    global _state_lock
    if _state_lock is None:
        if lock_path is None:
            lock_path = str(get_lock_file_path())
        _state_lock = FileLock(lock_path, timeout=10)
    return _state_lock


def expand_path(path: str) -> Path:
    """
    展开 ~ 为用户主目录，返回 Path 对象
    """
    return Path(os.path.expanduser(path))


def get_workspace_dir() -> Path:
    """
    获取 OpenClaw workspace 目录
    """
    return expand_path("~/.openclaw/workspace")


def get_state_file_path() -> Path:
    """
    获取 thinking-state.json 路径
    """
    return get_workspace_dir() / "thinking-state.json"


def get_queue_file_path() -> Path:
    """
    获取 thinking-queue.json 路径
    """
    return get_workspace_dir() / "thinking-queue.json"


def get_lock_file_path() -> Path:
    """
    获取锁文件路径
    """
    return get_workspace_dir() / "thinking-state.lock"


def get_thoughts_dir() -> Path:
    """
    获取思考记录目录
    """
    dir_path = get_workspace_dir() / "memory" / "thoughts"
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_today_thoughts_file() -> Path:
    """
    获取今天的思考记录文件
    """
    today = datetime.now().strftime("%Y-%m-%d")
    return get_thoughts_dir() / f"{today}.md"


def read_json_file(file_path: Path) -> Dict[str, Any]:
    """
    读取 JSON 文件（无锁，仅供内部使用）
    """
    if not file_path.exists():
        return {}

    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json_file(file_path: Path, data: Dict[str, Any]) -> None:
    """
    写入 JSON 文件（无锁，仅供内部使用）
    """
    # 先写临时文件，再重命名（原子写入）
    temp_path = file_path.with_suffix('.tmp')
    with open(temp_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    temp_path.replace(file_path)


def get_current_timestamp_ms() -> int:
    """
    获取当前时间戳（毫秒）
    """
    return int(datetime.now().timestamp() * 1000)


def get_current_timestamp() -> str:
    """
    获取当前时间戳字符串（秒）
    """
    return datetime.now().isoformat()


def get_current_date() -> str:
    """
    获取当前日期字符串
    """
    return datetime.now().strftime("%Y-%m-%d")


def get_current_time() -> str:
    """
    获取当前时间字符串
    """
    return datetime.now().strftime("%H:%M:%S")


def get_file_mtime(file_path: Path) -> Optional[int]:
    """
    获取文件的最后修改时间（毫秒时间戳）
    """
    if not file_path.exists():
        return None
    return int(file_path.stat().st_mtime * 1000)
