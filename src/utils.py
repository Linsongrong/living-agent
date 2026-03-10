# Living Agent - 工具函数模块
"""
提供基础工具函数：路径处理，时间处理等
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional
from filelock import FileLock


# 全局锁实例（按 agent_id 存储）
_state_locks: Dict[str, FileLock] = {}

# Agent ID 缓存
_cached_agent_id: Optional[str] = None


def get_agent_id() -> str:
    """
    获取当前 Agent ID

    优先级：
    1. 环境变量 OPENCLAW_AGENT_ID
    2. 环境变量 AGENT_ID
    3. 默认值 "default"
    """
    global _cached_agent_id
    if _cached_agent_id is not None:
        return _cached_agent_id

    # 尝试从环境变量读取
    agent_id = os.environ.get("OPENCLAW_AGENT_ID") or os.environ.get("AGENT_ID")
    if agent_id:
        _cached_agent_id = agent_id
        return agent_id

    # 使用默认值
    _cached_agent_id = "default"
    return _cached_agent_id


def set_agent_id(agent_id: str) -> None:
    """
    手动设置 Agent ID（用于测试或特殊情况）
    """
    global _cached_agent_id
    _cached_agent_id = agent_id


def get_workspace_dir(agent_id: str = None) -> Path:
    """
    获取 OpenClaw workspace 目录

    Args:
        agent_id: Agent 标识，默认从环境变量获取
    """
    if agent_id is None:
        agent_id = get_agent_id()
    return expand_path(f"~/.openclaw/workspace-{agent_id}")


def get_state_file_path(agent_id: str = None) -> Path:
    """
    获取 thinking-state.json 路径
    """
    return get_workspace_dir(agent_id) / "thinking-state.json"


def get_queue_file_path(agent_id: str = None) -> Path:
    """
    获取 thinking-queue.json 路径
    """
    return get_workspace_dir(agent_id) / "thinking-queue.json"


def get_lock_file_path(agent_id: str = None) -> Path:
    """
    获取锁文件路径
    """
    return get_workspace_dir(agent_id) / "thinking-state.lock"


def get_thoughts_dir(agent_id: str = None) -> Path:
    """
    获取思考记录目录
    """
    if agent_id is None:
        agent_id = get_agent_id()
    dir_path = get_workspace_dir(agent_id) / "memory" / "thoughts"
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_today_thoughts_file(agent_id: str = None) -> Path:
    """
    获取今天的思考记录文件
    """
    today = datetime.now().strftime("%Y-%m-%d")
    return get_thoughts_dir(agent_id) / f"{today}.md"


# ========== 兼容旧接口（不推荐使用）==========

# 为了兼容，保持旧的全局路径（deprecated）
def _get_legacy_workspace_dir() -> Path:
    """
    获取旧的公共 workspace 目录（兼容模式）
    """
    return expand_path("~/.openclaw/workspace")


# ========== 以下是基础工具函数 ==========

def expand_path(path: str) -> Path:
    """
    展开 ~ 为用户主目录，返回 Path 对象
    """
    return Path(os.path.expanduser(path))


def get_lock(agent_id: str = None) -> FileLock:
    """
    获取文件锁实例

    Args:
        agent_id: Agent 标识，默认从环境变量获取
    """
    if agent_id is None:
        agent_id = get_agent_id()

    if agent_id not in _state_locks:
        lock_path = str(get_lock_file_path(agent_id))
        _state_locks[agent_id] = FileLock(lock_path, timeout=10)
    return _state_locks[agent_id]


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
    # 确保目录存在
    file_path.parent.mkdir(parents=True, exist_ok=True)
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


# ========== 多租户路径兼容函数 ==========

def get_chat_history_path(agent_id: str = None) -> Path:
    """
    获取 chat_history.json 路径
    """
    if agent_id is None:
        agent_id = get_agent_id()
    return get_workspace_dir(agent_id) / "chat_history.json"


def get_sessions_history_path(agent_id: str = None) -> Path:
    """
    获取 sessions_history.json 路径
    """
    if agent_id is None:
        agent_id = get_agent_id()
    return get_workspace_dir(agent_id) / "sessions_history.json"
