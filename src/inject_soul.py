# Living Agent - 灵魂注入器 (v2.0)
"""
轻量级 Hook，用于前台任务（用户主动发送消息）时，
读取能量和情绪，动态注入到会话上下文中
"""

import json
import argparse

from .vital_signs import get_vital_signs, get_foreground_prompt_snippet


def inject_soul() -> str:
    """
    生成前台任务所需的灵魂注入片段

    包含：
    - 当前能量值
    - 当前情绪
    - 绝对指令（必须专业响应）
    - 可选的情绪表达

    Returns:
        可注入到 System Prompt 的文本片段
    """
    return get_foreground_prompt_snippet()


def get_soul_status() -> dict:
    """
    获取完整的灵魂状态

    Returns:
        包含能量、情绪、状态描述的字典
    """
    vital = get_vital_signs()

    # 状态描述
    if vital["current_mood"] == "tired" or vital["energy_level"] < 30:
        status = "疲惫但必须响应"
    elif vital["current_mood"] == "focused":
        status = "专注工作中"
    elif vital["current_mood"] == "chill":
        status = "休闲放松"
    else:
        status = "好奇探索中"

    return {
        "energy_level": vital["energy_level"],
        "current_mood": vital["current_mood"],
        "status": status,
        "in_silent_hours": False  # 前台任务不需要检查静默
    }


def main():
    parser = argparse.ArgumentParser(description="灵魂注入器")
    parser.add_argument('action', choices=['inject', 'status'], help='操作类型')

    args = parser.parse_args()

    if args.action == 'inject':
        snippet = inject_soul()
        print(snippet)

    elif args.action == 'status':
        status = get_soul_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
