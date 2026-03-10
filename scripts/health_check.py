#!/usr/bin/env python3
"""
Living Agent 健康检查脚本
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta

# 添加 skill 根目录到路径，使 src 成为可导入的包
skill_root = Path(__file__).parent.parent
sys.path.insert(0, str(skill_root))

from src.utils import get_state_file_path, read_json_file, get_current_timestamp_ms
from src.breaker import get_user_idle_minutes, is_in_silent_hours, check_daily_limit


def format_time_ago(ms_ago):
    """格式化时间差"""
    if ms_ago < 0:
        return "未来（异常）"
    
    minutes = ms_ago / 60000
    if minutes < 1:
        return "刚刚"
    elif minutes < 60:
        return f"{int(minutes)} 分钟前"
    elif minutes < 1440:
        return f"{int(minutes / 60)} 小时前"
    else:
        return f"{int(minutes / 1440)} 天前"


def check_cron_status():
    """检查 cron 任务状态（需要 OpenClaw CLI）"""
    # 这里简化处理，实际需要调用 openclaw cron list
    return None


def main():
    # Windows PowerShell UTF-8 编码修复
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    
    print("🦞 Living Agent 健康检查\n")
    
    # 1. 检查配置文件
    state_file = get_state_file_path()
    if not state_file.exists():
        print("❌ thinking-state.json 不存在")
        print(f"   路径: {state_file}")
        return 1
    
    print(f"✅ 配置文件: {state_file}")
    
    # 2. 读取状态
    try:
        state = read_json_file(state_file)
    except Exception as e:
        print(f"❌ 读取配置失败: {e}")
        return 1
    
    print("\n📊 当前状态:")
    
    # 3. 检查 lastUserMessage
    last_user_msg = state.get('lastUserMessage', 0)
    current_time = get_current_timestamp_ms()
    time_ago = current_time - last_user_msg
    
    if last_user_msg == 0:
        print("  ⚠️  lastUserMessage: 未设置")
    elif time_ago > 7 * 24 * 60 * 60 * 1000:  # 7 天
        print(f"  ❌ lastUserMessage: {format_time_ago(time_ago)} (异常！)")
    else:
        print(f"  ✅ lastUserMessage: {format_time_ago(time_ago)}")
    
    # 4. 检查用户空闲时间
    idle_minutes = get_user_idle_minutes()
    if idle_minutes < 30:
        print(f"  ✅ 用户状态: 在线（空闲 {idle_minutes} 分钟）")
    elif idle_minutes < 120:
        print(f"  ⚠️  用户状态: 离开（空闲 {idle_minutes} 分钟）")
    else:
        print(f"  ⏸️  用户状态: 长时间离开（空闲 {idle_minutes} 分钟）")
    
    # 5. 检查微触发状态
    micro_enabled = state.get('microHeartbeatEnabled', False)
    if micro_enabled:
        print("  🔄 微触发思考: 已启用")
    else:
        print("  ⏸️  微触发思考: 已禁用")
    
    # 6. 检查静默时段
    in_silent = is_in_silent_hours()
    silent_hours = state.get('silentHours', [23, 8])
    if in_silent:
        print(f"  🌙 静默时段: 是 ({silent_hours[0]}:00-{silent_hours[1]}:00)")
    else:
        print(f"  ☀️  静默时段: 否 ({silent_hours[0]}:00-{silent_hours[1]}:00)")
    
    # 7. 检查每日限额
    allowed, count, limit = check_daily_limit()
    percentage = int(count / limit * 100) if limit > 0 else 0
    if percentage < 50:
        print(f"  ✅ 今日思考: {count}/{limit} ({percentage}%)")
    elif percentage < 80:
        print(f"  ⚠️  今日思考: {count}/{limit} ({percentage}%)")
    else:
        print(f"  🔥 今日思考: {count}/{limit} ({percentage}%)")
    
    # 8. 检查能量系统（如果启用）
    if 'energy' in state:
        energy = state['energy']
        mood = state.get('mood', 'unknown')
        
        if energy >= 70:
            emoji = "💪"
        elif energy >= 40:
            emoji = "😐"
        else:
            emoji = "😴"
        
        print(f"  {emoji} 能量: {energy}%")
        print(f"  😊 情绪: {mood}")
    
    # 9. 检查 cron ID
    print("\n⏱️  Cron 配置:")
    micro_cron_id = state.get('microHeartbeatCronId')
    if micro_cron_id:
        print(f"  ✅ 微触发 cron ID: {micro_cron_id}")
    else:
        print("  ⚠️  微触发 cron ID: 未设置")
    
    # 10. 检查目录
    print("\n📂 目录检查:")
    workspace = state_file.parent
    
    thoughts_dir = workspace / "memory" / "thoughts"
    if thoughts_dir.exists():
        thought_files = list(thoughts_dir.glob("*.md"))
        print(f"  ✅ memory/thoughts/: {len(thought_files)} 个文件")
    else:
        print("  ⚠️  memory/thoughts/: 不存在")
    
    queue_file = workspace / "thinking-queue.json"
    if queue_file.exists():
        try:
            with open(queue_file) as f:
                queue = json.load(f)
            pending = len([q for q in queue.get('questions', []) if q.get('status') == 'pending'])
            print(f"  ✅ thinking-queue.json: {pending} 个待思考问题")
        except:
            print("  ⚠️  thinking-queue.json: 读取失败")
    else:
        print("  ⚠️  thinking-queue.json: 不存在")
    
    print("\n✅ 健康检查完成")
    return 0


if __name__ == '__main__':
    sys.exit(main())
