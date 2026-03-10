# Living Agent - 思考锁（P1: 状态机）
"""
提供思考锁机制，防止多个思考任务同时执行
"""

import sys
import argparse
from filelock import Timeout

from .utils import get_lock, get_current_timestamp_ms, read_json_file, write_json_file, get_state_file_path


# 思考锁超时时间（毫秒）
THINKING_LOCK_TIMEOUT_MS = 5 * 60 * 1000  # 5 分钟


def acquire_thinking_lock(task_name: str, timeout: int = 30) -> bool:
    """
    尝试获取思考锁

    Args:
        task_name: 任务名称（如 "micro-heartbeat", "dream", "exploration"）
        timeout: 获取锁的超时时间（秒）

    Returns:
        True 表示成功获取锁，False 表示失败
    """
    lock = get_lock()
    try:
        lock.acquire(timeout=timeout)
    except Timeout:
        print(f"错误：无法获取文件锁", file=sys.stderr)
        return False

    try:
        # 直接读取文件，避免嵌套锁
        state = read_json_file(get_state_file_path())

        # 检查是否已有任务在思考
        if state.get('is_thinking', False):
            current_task = state.get('current_task', 'unknown')
            lock_time = state.get('thinking_lock_time', 0)
            current_time = get_current_timestamp_ms()

            # 检查锁是否过期
            if lock_time > 0 and current_time - lock_time > THINKING_LOCK_TIMEOUT_MS:
                # 锁已过期，强制覆盖
                print(f"警告：之前的任务 '{current_task}' 锁已过期，强制获取", file=sys.stderr)
            else:
                print(f"错误：大脑忙碌，当前任务: {current_task}", file=sys.stderr)
                return False

        # 获取锁成功，设置状态
        state['is_thinking'] = True
        state['current_task'] = task_name
        state['thinking_lock_time'] = get_current_timestamp_ms()
        write_json_file(get_state_file_path(), state)

        return True

    except Exception as e:
        print(f"错误：获取思考锁失败: {e}", file=sys.stderr)
        return False
    finally:
        if lock.is_locked:
            lock.release()


def release_thinking_lock(task_name: str = None) -> bool:
    """
    释放思考锁

    Args:
        task_name: 任务名称（用于验证）

    Returns:
        True 表示成功释放，False 表示失败
    """
    lock = get_lock()
    try:
        lock.acquire(timeout=10)
    except Timeout:
        print("错误：无法获取文件锁", file=sys.stderr)
        return False

    try:
        # 直接读取文件，避免嵌套锁
        state = read_json_file(get_state_file_path())

        # 验证任务名称
        current_task = state.get('current_task')
        if task_name and current_task != task_name:
            print(f"警告：任务名称不匹配，当前: {current_task}, 请求: {task_name}", file=sys.stderr)

        # 释放锁
        state['is_thinking'] = False
        state['current_task'] = None
        state['thinking_lock_time'] = None
        write_json_file(get_state_file_path(), state)

        return True

    except Exception as e:
        print(f"错误：释放思考锁失败: {e}", file=sys.stderr)
        return False
    finally:
        if lock.is_locked:
            lock.release()


def is_thinking() -> bool:
    """
    检查大脑是否正在思考
    """
    lock = get_lock()
    try:
        lock.acquire(timeout=5)
    except Timeout:
        return True  # 锁获取失败，保守返回 True

    try:
        state = read_json_file(get_state_file_path())
        is_busy = state.get('is_thinking', False)

        # 检查锁是否过期
        if is_busy:
            lock_time = state.get('thinking_lock_time', 0)
            current_time = get_current_timestamp_ms()
            if lock_time > 0 and current_time - lock_time > THINKING_LOCK_TIMEOUT_MS:
                # 锁已过期，视为空闲
                return False

        return is_busy
    finally:
        if lock.is_locked:
            lock.release()


def get_current_task() -> str:
    """
    获取当前正在执行的任务
    """
    lock = get_lock()
    try:
        lock.acquire(timeout=5)
    except Timeout:
        return "unknown"

    try:
        state = read_json_file(get_state_file_path())
        return state.get('current_task', 'idle')
    finally:
        if lock.is_locked:
            lock.release()


# CLI 接口
def main():
    parser = argparse.ArgumentParser(description="思考锁管理器")
    parser.add_argument('action', choices=['acquire', 'release', 'status'],
                        help='操作类型')
    parser.add_argument('--task', default='default', help='任务名称')

    args = parser.parse_args()

    if args.action == 'acquire':
        success = acquire_thinking_lock(args.task)
        if success:
            print("OK")
            sys.exit(0)
        else:
            print("FAILED")
            sys.exit(1)

    elif args.action == 'release':
        success = release_thinking_lock(args.task)
        if success:
            print("OK")
            sys.exit(0)
        else:
            print("FAILED")
            sys.exit(1)

    elif args.action == 'status':
        if is_thinking():
            task = get_current_task()
            print(f"BUSY:{task}")
        else:
            print("IDLE")


if __name__ == '__main__':
    main()
