#!/usr/bin/env python3
"""
Living Agent 自动修复脚本
检测并修复常见问题
"""

import sys
import time
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import get_state_file_path, read_json_file, write_json_file, get_current_timestamp_ms
from breaker import update_last_user_message


def fix_last_user_message():
    """修复异常的 lastUserMessage"""
    state_file = get_state_file_path()
    state = read_json_file(state_file)
    
    last_user_msg = state.get('lastUserMessage', 0)
    current_time = get_current_timestamp_ms()
    time_ago = current_time - last_user_msg
    
    # 如果超过 7 天，认为异常
    if time_ago > 7 * 24 * 60 * 60 * 1000:
        print(f"⚠️  检测到 lastUserMessage 异常: {time_ago / 86400000:.1f} 天前")
        print("🔧 修复中...")
        
        # 更新为当前时间
        state['lastUserMessage'] = current_time
        write_json_file(state_file, state)
        
        print("✅ 已修复 lastUserMessage")
        return True
    
    return False


def fix_missing_fields():
    """补全缺失的配置字段"""
    state_file = get_state_file_path()
    state = read_json_file(state_file)
    
    fixed = False
    
    # 检查必要字段
    defaults = {
        'timezone_offset': 8,
        'silentHours': [23, 8],
        'daily_thoughts_limit': 50,
        'microHeartbeatEnabled': False,
        'lastUserMessage': 0,
        'daily_thoughts_count': 0,
        'last_reset_date': ''
    }
    
    for key, default_value in defaults.items():
        if key not in state:
            print(f"⚠️  缺失字段: {key}")
            state[key] = default_value
            fixed = True
    
    if fixed:
        write_json_file(state_file, state)
        print("✅ 已补全缺失字段")
    
    return fixed


def main():
    print("🔧 Living Agent 自动修复\n")
    
    # 检查配置文件是否存在
    state_file = get_state_file_path()
    if not state_file.exists():
        print(f"❌ 配置文件不存在: {state_file}")
        print("请先运行安装脚本")
        return 1
    
    fixed_count = 0
    
    # 1. 修复 lastUserMessage
    if fix_last_user_message():
        fixed_count += 1
    
    # 2. 补全缺失字段
    if fix_missing_fields():
        fixed_count += 1
    
    if fixed_count == 0:
        print("✅ 未发现问题")
    else:
        print(f"\n✅ 修复完成，共修复 {fixed_count} 个问题")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
