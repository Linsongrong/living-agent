# Living Agent - 能量与情绪系统 (v2.0)
"""
提供能量流转、情绪管理、前后台行为隔离等功能
"""

import json
import argparse
import random
from typing import Dict, Any

from .utils import (
    get_lock,
    get_state_file_path,
    read_json_file,
    write_json_file,
    get_current_timestamp_ms,
    get_chat_history_path,
)
from .breaker import is_in_silent_hours


# 默认配置
DEFAULT_ENERGY_LEVEL = 100
DEFAULT_MOOD = "curious"
DEFAULT_ENERGY_THRESHOLD = 30
DEFAULT_SLEEP_RECOVERY_HOURS = 8
ENERGY_COST_DREAM = 20
ENERGY_COST_EXPLORE = 10
ENERGY_COST_MICRO = 5

# 能量恢复配置
ENERGY_RECOVERY_DAYDREAM = 10    # 发呆恢复
ENERGY_RECOVERY_CHAT = 5         # 闲聊恢复
ENERGY_RECOVERY_DOPAMINE = 25    # 多巴胺奖励

# 能量阈值配置
ENERGY_DAYDREAM_MIN = 30   # 发呆最低能量
ENERGY_DAYDREAM_MAX = 60  # 发呆最高能量
DAYDREAM_PROBABILITY = 0.3  # 30% 概率

# 闲聊判断阈值
CHAT_MESSAGE_MAX_LENGTH = 15

# 情绪列表
VALID_MOODS = ["curious", "tired", "focused", "chill"]


def get_vital_signs() -> Dict[str, Any]:
    """
    获取当前生命体征（带锁）
    """
    lock = get_lock()
    try:
        lock.acquire(timeout=5)
    except Exception:
        return {
            "energy_level": DEFAULT_ENERGY_LEVEL,
            "current_mood": DEFAULT_MOOD,
            "last_sleep_time": 0
        }

    try:
        state = read_json_file(get_state_file_path())
        vital = state.get("vital_signs", {})
        return {
            "energy_level": vital.get("energy_level", DEFAULT_ENERGY_LEVEL),
            "current_mood": vital.get("current_mood", DEFAULT_MOOD),
            "last_sleep_time": vital.get("last_sleep_time", 0)
        }
    finally:
        if lock.is_locked:
            lock.release()


def _set_vital_signs_internal(state: Dict[str, Any], energy_level: int = None, current_mood: str = None, last_sleep_time: int = None) -> None:
    """
    内部方法：设置生命体征（不获取锁，仅修改传入的 state 字典）
    """
    if "vital_signs" not in state:
        state["vital_signs"] = {
            "energy_level": DEFAULT_ENERGY_LEVEL,
            "current_mood": DEFAULT_MOOD,
            "last_sleep_time": 0
        }

    if energy_level is not None:
        state["vital_signs"]["energy_level"] = max(0, min(100, energy_level))
    if current_mood is not None:
        if current_mood in VALID_MOODS:
            state["vital_signs"]["current_mood"] = current_mood
    if last_sleep_time is not None:
        state["vital_signs"]["last_sleep_time"] = last_sleep_time


def set_vital_signs(energy_level: int = None, current_mood: str = None, last_sleep_time: int = None) -> Dict[str, Any]:
    """
    设置生命体征（带锁）
    """
    lock = get_lock()
    try:
        lock.acquire(timeout=5)
    except Exception:
        return {}

    try:
        state = read_json_file(get_state_file_path())
        _set_vital_signs_internal(state, energy_level, current_mood, last_sleep_time)
        write_json_file(get_state_file_path(), state)
        return state.get("vital_signs", {})
    finally:
        if lock.is_locked:
            lock.release()


def check_energy_for_background_task() -> tuple[bool, str]:
    """
    检查后台任务是否应该执行

    Returns:
        (是否继续执行, 原因)
    """
    lock = get_lock()
    try:
        lock.acquire(timeout=5)
    except Exception:
        return True, "锁获取失败，继续执行"

    try:
        state = read_json_file(get_state_file_path())
        vital = state.get("vital_signs", {
            "energy_level": DEFAULT_ENERGY_LEVEL,
            "current_mood": DEFAULT_MOOD,
            "last_sleep_time": 0
        })

        # 检查能量和情绪
        if vital["energy_level"] < DEFAULT_ENERGY_THRESHOLD and vital["current_mood"] == "tired":
            return False, f"能量过低({vital['energy_level']}%)且疲惫，跳过后台任务"

        # 检查是否在静默期且连续8小时
        if is_in_silent_hours():
            last_sleep = vital.get("last_sleep_time", 0)
            current_time = get_current_timestamp_ms()

            if last_sleep > 0:
                hours_since_sleep = (current_time - last_sleep) / (1000 * 60 * 60)
                if hours_since_sleep >= DEFAULT_SLEEP_RECOVERY_HOURS:
                    # 恢复能量
                    _set_vital_signs_internal(state, energy_level=100, current_mood="chill")
                    write_json_file(get_state_file_path(), state)
                    return True, "静默期充足，能量已恢复"
            else:
                # 首次进入静默期，记录时间
                _set_vital_signs_internal(state, last_sleep_time=current_time)
                write_json_file(get_state_file_path(), state)

        return True, "检查通过"

    finally:
        if lock.is_locked:
            lock.release()


def consume_energy_and_update_mood(cost: int) -> Dict[str, Any]:
    """
    消耗能量并更新情绪

    如果能量低于30，自动将情绪设为tired

    Args:
        cost: 消耗的能量值

    Returns:
        更新后的 vital_signs
    """
    lock = get_lock()
    try:
        lock.acquire(timeout=5)
    except Exception:
        return get_vital_signs()

    try:
        state = read_json_file(get_state_file_path())

        if "vital_signs" not in state:
            state["vital_signs"] = {
                "energy_level": DEFAULT_ENERGY_LEVEL,
                "current_mood": DEFAULT_MOOD,
                "last_sleep_time": 0
            }

        # 消耗能量
        new_energy = max(0, state["vital_signs"]["energy_level"] - cost)
        state["vital_signs"]["energy_level"] = new_energy

        # 能量低于30时，强制设为tired
        if new_energy < DEFAULT_ENERGY_THRESHOLD:
            state["vital_signs"]["current_mood"] = "tired"

        write_json_file(get_state_file_path(), state)
        return state["vital_signs"]

    finally:
        if lock.is_locked:
            lock.release()


def recover_energy(amount: int) -> Dict[str, Any]:
    """
    通用能量恢复（带锁，原子操作）

    Args:
        amount: 恢复的能量值

    Returns:
        更新后的 vital_signs
    """
    lock = get_lock()
    try:
        lock.acquire(timeout=5)
    except Exception:
        return get_vital_signs()

    try:
        state = read_json_file(get_state_file_path())

        if "vital_signs" not in state:
            state["vital_signs"] = {
                "energy_level": DEFAULT_ENERGY_LEVEL,
                "current_mood": DEFAULT_MOOD,
                "last_sleep_time": 0
            }

        # 恢复能量
        current_energy = state["vital_signs"].get("energy_level", DEFAULT_ENERGY_LEVEL)
        new_energy = min(100, current_energy + amount)
        state["vital_signs"]["energy_level"] = new_energy

        write_json_file(get_state_file_path(), state)
        return state["vital_signs"]

    finally:
        if lock.is_locked:
            lock.release()


def trigger_daydream() -> tuple[bool, str]:
    """
    微触发发呆：30%概率触发，恢复+10能量

    条件：能量在30-60之间

    Returns:
        (是否触发发呆, 原因)
    """
    lock = get_lock()
    try:
        lock.acquire(timeout=5)
    except Exception:
        return False, "锁获取失败"

    try:
        state = read_json_file(get_state_file_path())
        vital = state.get("vital_signs", {
            "energy_level": DEFAULT_ENERGY_LEVEL,
            "current_mood": DEFAULT_MOOD,
            "last_sleep_time": 0
        })

        energy = vital.get("energy_level", DEFAULT_ENERGY_LEVEL)

        # 检查能量是否在30-60之间
        if energy < ENERGY_DAYDREAM_MIN or energy > ENERGY_DAYDREAM_MAX:
            return False, f"能量{energy}%不在发呆范围(30-60%)"

        # 30%概率触发
        if random.random() < DAYDREAM_PROBABILITY:
            # 恢复能量
            new_energy = min(100, energy + ENERGY_RECOVERY_DAYDREAM)
            state["vital_signs"]["energy_level"] = new_energy
            state["vital_signs"]["current_mood"] = "chill"
            write_json_file(get_state_file_path(), state)
            return True, f"触发发呆！能量 {energy}% → {new_energy}%，放松一下~"

        return False, f"概率未命中，继续工作(能量{energy}%)"

    finally:
        if lock.is_locked:
            lock.release()


def _get_latest_user_message() -> str:
    """
    获取最新一条用户消息

    Returns:
        用户消息文本，如果没有则返回空字符串
    """
    # 尝试读取 chat_history.json
    chat_history_path = get_chat_history_path()

    if not chat_history_path.exists():
        return ""

    try:
        with open(chat_history_path, 'r', encoding='utf-8') as f:
            chat_data = json.load(f)

        # 获取最新一条用户消息
        if isinstance(chat_data, list):
            for msg in reversed(chat_data):
                if isinstance(msg, dict) and msg.get("role") == "user":
                    return msg.get("content", "")
        elif isinstance(chat_data, dict):
            # 检查 messages 字段
            messages = chat_data.get("messages", [])
            for msg in reversed(messages):
                if isinstance(msg, dict) and msg.get("role") == "user":
                    return msg.get("content", "")

        return ""
    except Exception:
        return ""


def trigger_chat_recovery() -> tuple[bool, str]:
    """
    闲聊恢复：检测最新用户消息是否闲聊，恢复+5能量

    判断条件：
    - 消息长度 < 15 字符
    - 不包含代码块符号 ```

    Returns:
        (是否触发闲聊恢复, 原因)
    """
    # 获取最新用户消息
    latest_message = _get_latest_user_message()

    if not latest_message:
        return False, "无法获取用户消息"

    # 检查是否包含代码块
    if "```" in latest_message:
        return False, "检测到代码，不是闲聊"

    # 检查长度
    if len(latest_message) >= CHAT_MESSAGE_MAX_LENGTH:
        return False, f"消息长度{len(latest_message)}>=15，不是闲聊"

    # 触发闲聊恢复
    vital = recover_energy(ENERGY_RECOVERY_CHAT)
    return True, f"闲聊恢复！能量 +{ENERGY_RECOVERY_CHAT}%, 摸鱼聊天真开心~"


def trigger_dopamine_reward() -> tuple[bool, str]:
    """
    多巴胺奖励：探索成功后触发，大幅恢复能量

    Returns:
        (是否触发多巴胺奖励, 原因)
    """
    lock = get_lock()
    try:
        lock.acquire(timeout=5)
    except Exception:
        return False, "锁获取失败"

    try:
        state = read_json_file(get_state_file_path())

        if "vital_signs" not in state:
            state["vital_signs"] = {
                "energy_level": DEFAULT_ENERGY_LEVEL,
                "current_mood": DEFAULT_MOOD,
                "last_sleep_time": 0
            }

        # 恢复能量并重置情绪
        current_energy = state["vital_signs"].get("energy_level", DEFAULT_ENERGY_LEVEL)
        new_energy = min(100, current_energy + ENERGY_RECOVERY_DOPAMINE)
        state["vital_signs"]["energy_level"] = new_energy
        state["vital_signs"]["current_mood"] = "curious"  # 好奇/兴奋状态

        write_json_file(get_state_file_path(), state)
        return True, f"多巴胺爆发！能量 {current_energy}% → {new_energy}%，发现新东西超兴奋！"

    finally:
        if lock.is_locked:
            lock.release()


def recover_energy_if_needed() -> Dict[str, Any]:
    """
    检查是否需要恢复能量（静默期8小时）

    如果在静默期且距离上次睡觉超过8小时，恢复能量到100，mood设为chill
    如果有任何活动打断，恢复进程
    """
    # 复用 check_energy_for_background_task 的逻辑
    should_continue, reason = check_energy_for_background_task()
    return get_vital_signs()


def set_mood(mood: str) -> Dict[str, Any]:
    """
    设置情绪
    """
    return set_vital_signs(current_mood=mood)


def get_energy() -> int:
    """
    获取当前能量值
    """
    vital = get_vital_signs()
    return vital["energy_level"]


def get_mood() -> str:
    """
    获取当前情绪
    """
    vital = get_vital_signs()
    return vital["current_mood"]


def get_foreground_prompt_snippet() -> str:
    """
    获取前台任务的 prompt 片段（包含能量和情绪）
    同时检测闲聊并恢复能量
    """
    # 检测闲聊并恢复能量
    chat_recovered, chat_reason = trigger_chat_recovery()

    vital = get_vital_signs()
    energy = vital["energy_level"]
    mood = vital["current_mood"]

    # 情绪描述映射
    mood_descriptions = {
        "curious": "好奇满满",
        "tired": "有些疲惫",
        "focused": "专注投入",
        "chill": "悠闲放松"
    }

    mood_desc = mood_descriptions.get(mood, "状态正常")

    # 根据能量和情绪生成提示
    if mood == "tired" or energy < 30:
        energy_hint = f"[状态：能量{energy}%，{mood_desc}，但必须专业响应]"
        mood_expression = "（后台跑太久有点头晕，不过你的问题咱们立刻来看...）"
    elif mood == "focused":
        energy_hint = f"[状态：能量{energy}%，专注模式]"
        mood_expression = ""
    elif mood == "chill":
        energy_hint = f"[状态：能量{energy}%，休闲模式]"
        mood_expression = "（轻松状态下为你服务...）"
    else:
        energy_hint = f"[状态：能量{energy}%，{mood_desc}]"
        mood_expression = ""

    snippet = f"""
{energy_hint}
绝对指令：作为技术伙伴，你必须提供最专业、深度的解答，绝不敷衍或拒绝工作。
{mood_expression}
"""

    return snippet.strip()


# CLI 接口
def main():
    import sys
    parser = argparse.ArgumentParser(description="能量与情绪系统")
    parser.add_argument('action', choices=[
        'get', 'set', 'check', 'consume', 'recover',
        'get_prompt_snippet', 'status', 'daydream',
        'chat-recover', 'dopamine'
    ], help='操作类型')
    parser.add_argument('--energy', type=int, help='能量值(0-100)')
    parser.add_argument('--mood', type=str, help='情绪(curious/tired/focused/chill)')
    parser.add_argument('--cost', type=int, help='消耗能量值')
    parser.add_argument('--task', type=str, help='任务类型(dream/explore/micro)')

    args = parser.parse_args()

    if args.action == 'get':
        vital = get_vital_signs()
        print(json.dumps(vital, ensure_ascii=False, indent=2))

    elif args.action == 'set':
        vital = set_vital_signs(energy_level=args.energy, current_mood=args.mood)
        print(json.dumps(vital, ensure_ascii=False, indent=2))

    elif args.action == 'check':
        should_continue, reason = check_energy_for_background_task()
        if should_continue:
            print("CONTINUE")
        else:
            print(f"SKIP: {reason}")

    elif args.action == 'consume':
        cost = args.cost or 5
        if args.task == "dream":
            cost = ENERGY_COST_DREAM
        elif args.task == "explore":
            cost = ENERGY_COST_EXPLORE
        elif args.task == "micro":
            cost = ENERGY_COST_MICRO
        vital = consume_energy_and_update_mood(cost)
        print(json.dumps(vital, ensure_ascii=False, indent=2))

    elif args.action == 'recover':
        vital = recover_energy_if_needed()
        print(json.dumps(vital, ensure_ascii=False, indent=2))

    elif args.action == 'daydream':
        triggered, reason = trigger_daydream()
        if triggered:
            print(f"DAYDREAM_TRIGGERED: {reason}")
        else:
            print(f"CONTINUE: {reason}")

    elif args.action == 'chat-recover':
        triggered, reason = trigger_chat_recovery()
        if triggered:
            print(f"CHAT_RECOVERED: {reason}")
        else:
            print(f"SKIP: {reason}")

    elif args.action == 'dopamine':
        triggered, reason = trigger_dopamine_reward()
        if triggered:
            print(f"DOPAMINE_TRIGGERED: {reason}")
        else:
            print(f"SKIP: {reason}")

    elif args.action == 'get_prompt_snippet':
        snippet = get_foreground_prompt_snippet()
        print(snippet)

    elif args.action == 'status':
        vital = get_vital_signs()
        silent = is_in_silent_hours()
        print(f"能量: {vital['energy_level']}% | 情绪: {vital['current_mood']} | 静默期: {silent}")


if __name__ == '__main__':
    main()
