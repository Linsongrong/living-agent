# Living Agent - 核心模块
"""
Living Agent - 让 Agent 既「有用」又「活着」
"""

from .state_manager import (
    read_state,
    write_state,
    read_queue,
    write_queue,
    update_state,
    get_state_field,
)

from .thinking_lock import (
    acquire_thinking_lock,
    release_thinking_lock,
    is_thinking,
    get_current_task,
)

from .breaker import (
    check_daily_limit,
    increment_daily_count,
    is_in_silent_hours,
    get_user_idle_minutes,
    get_user_last_active_time,
)

from .utils import (
    get_workspace_dir,
    get_state_file_path,
    get_queue_file_path,
    get_thoughts_dir,
    get_today_thoughts_file,
    get_current_timestamp_ms,
    get_current_date,
    get_current_time,
)

__all__ = [
    # state_manager
    'read_state',
    'write_state',
    'read_queue',
    'write_queue',
    'update_state',
    'get_state_field',
    # thinking_lock
    'acquire_thinking_lock',
    'release_thinking_lock',
    'is_thinking',
    'get_current_task',
    # breaker
    'check_daily_limit',
    'increment_daily_count',
    'is_in_silent_hours',
    'get_user_idle_minutes',
    'get_user_last_active_time',
    # utils
    'get_workspace_dir',
    'get_state_file_path',
    'get_queue_file_path',
    'get_thoughts_dir',
    'get_today_thoughts_file',
    'get_current_timestamp_ms',
    'get_current_date',
    'get_current_time',
]

__version__ = "2.0.0"
