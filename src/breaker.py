# Living Agent - 防破产与时区管理（P2）
"""
提供每日思考次数限制、静默时段判断等功能
"""

import sys
import argparse
from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple

from .utils import get_lock, get_state_file_path, get_current_date, get_current_timestamp_ms, expand_path, read_json_file, write_json_file


# 默认配置
DEFAULT_DAILY_LIMIT = 50
DEFAULT_TIMEZONE_OFFSET = 8
DEFAULT_SILENT_HOURS = [23, 8]


def get_user_local_time(timezone_offset: int = None) -> datetime:
    """
    获取用户本地时间
    """
    if timezone_offset is None:
        timezone_offset = get_timezone_offset()

    # 使用 timezone-aware UTC 时间
    utc_now = datetime.now(timezone.utc)
    # 时区偏移可能是浮点数（如 8.5 表示 +8:30）
    hours = int(timezone_offset)
    minutes = int((timezone_offset - hours) * 60)
    return utc_now + timedelta(hours=hours, minutes=minutes)


def get_timezone_offset() -> int:
    """
    从状态文件获取时区偏移
    """
    try:
        state = read_json_file(get_state_file_path())
        return state.get('timezone_offset', DEFAULT_TIMEZONE_OFFSET)
    except Exception:
        return DEFAULT_TIMEZONE_OFFSET


def is_in_silent_hours(timezone_offset: int = None) -> bool:
    """
    判断当前是否在静默时段

    Args:
        timezone_offset: 时区偏移（小时）

    Returns:
        True 表示在静默时段
    """
    if timezone_offset is None:
        timezone_offset = get_timezone_offset()

    lock = get_lock()
    try:
        lock.acquire(timeout=5)
    except Exception:
        return False

    try:
        state = read_json_file(get_state_file_path())
        silent_hours = state.get('silentHours', DEFAULT_SILENT_HOURS)
    finally:
        if lock.is_locked:
            lock.release()

    if not silent_hours or len(silent_hours) != 2:
        return False

    silent_start, silent_end = silent_hours
    local_time = get_user_local_time(timezone_offset)
    current_hour = local_time.hour

    # 处理跨天的情况（如 23:00-08:00）
    if silent_start > silent_end:
        # 跨天：23:00-08:00
        return current_hour >= silent_start or current_hour < silent_end
    else:
        # 同一天：比如 00:00-06:00
        return silent_start <= current_hour < silent_end


def check_and_increment_daily_count() -> Tuple[bool, int, int]:
    """
    原子操作：检查并增加每日思考次数

    Returns:
        (是否成功, 当前次数, 限制次数)
    """
    lock = get_lock()
    try:
        lock.acquire(timeout=5)
    except Exception:
        return False, -1, -1

    try:
        state = read_json_file(get_state_file_path())
        today = get_current_date()

        # 获取或初始化字段
        daily_count = state.get('daily_thoughts_count', 0)
        last_reset = state.get('last_reset_date', '')
        daily_limit = state.get('daily_thoughts_limit', DEFAULT_DAILY_LIMIT)

        # 检查是否需要重置
        if last_reset != today:
            daily_count = 0
            state['daily_thoughts_count'] = 0
            state['last_reset_date'] = today

        # 检查是否超过限制
        if daily_count >= daily_limit:
            return False, daily_count, daily_limit

        # 增加计数
        state['daily_thoughts_count'] = daily_count + 1
        write_json_file(get_state_file_path(), state)

        return True, daily_count + 1, daily_limit

    finally:
        if lock.is_locked:
            lock.release()


def check_daily_limit() -> Tuple[bool, int, int]:
    """
    检查是否达到每日思考次数上限（仅检查，不增加）

    Returns:
        (是否允许, 当前次数, 限制次数)
    """
    lock = get_lock()
    try:
        lock.acquire(timeout=5)
    except Exception:
        return False, -1, -1

    try:
        state = read_json_file(get_state_file_path())
        today = get_current_date()

        daily_count = state.get('daily_thoughts_count', 0)
        last_reset = state.get('last_reset_date', '')
        daily_limit = state.get('daily_thoughts_limit', DEFAULT_DAILY_LIMIT)

        if last_reset != today:
            daily_count = 0

        allowed = daily_count < daily_limit
        return allowed, daily_count, daily_limit
    finally:
        if lock.is_locked:
            lock.release()


def increment_daily_count() -> bool:
    """
    增加每日思考计数（仅增加）

    Returns:
        True 表示成功，False 表示已达上限
    """
    success, _, _ = check_and_increment_daily_count()
    return success


def get_user_last_active_time() -> Optional[int]:
    """
    获取用户最后活跃时间（毫秒时间戳）

    通过读取 chat_history.json 的 mtime 来判断用户是否在线
    """
    # 尝试读取 OpenClaw 的聊天历史文件
    possible_paths = [
        "~/.openclaw/workspace/chat_history.json",
        "~/.openclaw/workspace/sessions_history.json",
    ]

    for path_str in possible_paths:
        path = expand_path(path_str)
        if path.exists():
            mtime = int(path.stat().st_mtime * 1000)
            return mtime

    # 如果都找不到，返回 None
    return None


def get_user_idle_minutes() -> int:
    """
    获取用户空闲分钟数

    优先使用 thinking-state.json 中的 lastUserMessage，
    如果没有则回退到读取 chat_history.json 的 mtime
    """
    lock = get_lock()
    try:
        lock.acquire(timeout=5)
    except Exception:
        # 锁获取失败，保守处理
        return 9999

    try:
        state = read_json_file(get_state_file_path())
        last_user_msg = state.get('lastUserMessage', 0)
    finally:
        if lock.is_locked:
            lock.release()

    if last_user_msg > 0:
        current_time = get_current_timestamp_ms()
        return int((current_time - last_user_msg) / 60000)

    # 回退：读取文件的 mtime
    last_active = get_user_last_active_time()
    if last_active:
        current_time = get_current_timestamp_ms()
        return int((current_time - last_active) / 60000)

    # 没有数据，返回最大值
    return 9999


# CLI 接口
def main():
    parser = argparse.ArgumentParser(description="防破产与时区管理")
    parser.add_argument('action', choices=['check_limit', 'increment', 'silent', 'idle', 'local_time'],
                        help='操作类型')

    args = parser.parse_args()

    if args.action == 'check_limit':
        allowed, count, limit = check_daily_limit()
        print(f"{{\"allowed\": {allowed}, \"count\": {count}, \"limit\": {limit}}}")

    elif args.action == 'increment':
        success = increment_daily_count()
        if success:
            print("OK")
        else:
            print("LIMIT_REACHED")
            sys.exit(1)

    elif args.action == 'silent':
        in_silent = is_in_silent_hours()
        print("true" if in_silent else "false")

    elif args.action == 'idle':
        minutes = get_user_idle_minutes()
        print(str(minutes))

    elif args.action == 'local_time':
        local = get_user_local_time()
        print(local.strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == '__main__':
    main()
