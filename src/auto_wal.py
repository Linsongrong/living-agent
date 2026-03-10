#!/usr/bin/env python3
"""
Living Agent - 自动 WAL 更新脚本
从 chat_history.json 的 mtime 自动更新 lastUserMessage
"""

import sys
import os
from pathlib import Path

# 支持直接运行和作为模块导入
try:
    from .utils import get_state_file_path, read_json_file, write_json_file, get_current_timestamp_ms, get_chat_history_path
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.utils import get_state_file_path, read_json_file, write_json_file, get_current_timestamp_ms, get_chat_history_path


def auto_update_from_chat_history():
    """
    从 chat_history.json 的 mtime 自动更新 lastUserMessage
    
    Returns:
        bool: 是否更新了 lastUserMessage
    """
    try:
        # 读取当前状态
        state_file = get_state_file_path()
        state = read_json_file(state_file)
        current_last_user_msg = state.get('lastUserMessage', 0)
        
        # 获取 chat_history.json 的 mtime
        chat_history_path = get_chat_history_path()
        if not chat_history_path.exists():
            print("NO_CHAT_HISTORY")
            return False
        
        # 获取文件修改时间（毫秒）
        mtime_ms = int(os.path.getmtime(chat_history_path) * 1000)
        
        # 如果 chat_history 更新了，说明有新消息
        if mtime_ms > current_last_user_msg:
            state['lastUserMessage'] = mtime_ms
            write_json_file(state_file, state)
            print(f"AUTO_UPDATED: {mtime_ms}")
            return True
        else:
            print(f"NO_UPDATE_NEEDED: {current_last_user_msg}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return False


if __name__ == '__main__':
    # Windows PowerShell UTF-8 编码修复
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    
    auto_update_from_chat_history()
