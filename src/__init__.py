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

from .vital_signs import (
    get_vital_signs,
    set_vital_signs,
    check_energy_for_background_task,
    consume_energy_and_update_mood,
    recover_energy_if_needed,
    get_energy,
    get_mood,
    get_foreground_prompt_snippet,
)

from .inject_soul import (
    inject_soul,
    get_soul_status,
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
    # vital_signs
    'get_vital_signs',
    'set_vital_signs',
    'check_energy_for_background_task',
    'consume_energy_and_update_mood',
    'recover_energy_if_needed',
    'get_energy',
    'get_mood',
    'get_foreground_prompt_snippet',
    # inject_soul
    'inject_soul',
    'get_soul_status',
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
