# Living Agent - 状态管理器（P0: 文件锁）
"""
提供原子化的状态读写操作，使用文件锁防止并发冲突
"""

import sys
import json
import argparse
from filelock import Timeout
from typing import Dict, Any

from .utils import (
    get_lock,
    get_state_file_path,
    get_queue_file_path,
    read_json_file,
    write_json_file,
)


def acquire_lock(timeout: int = 10) -> bool:
    """
    获取文件锁
    """
    try:
        lock = get_lock()
        lock.acquire(timeout=timeout)
        return True
    except Timeout:
        return False


def release_lock() -> None:
    """
    释放文件锁
    """
    lock = get_lock()
    if lock.is_locked:
        lock.release()


def read_state() -> Dict[str, Any]:
    """
    读取状态（带锁）
    """
    with get_lock():
        return read_json_file(get_state_file_path())


def write_state(state: Dict[str, Any]) -> None:
    """
    写入状态（带锁）
    """
    with get_lock():
        write_json_file(get_state_file_path(), state)


def read_queue() -> Dict[str, Any]:
    """
    读取队列（带锁）
    """
    with get_lock():
        return read_json_file(get_queue_file_path())


def write_queue(queue: Dict[str, Any]) -> None:
    """
    写入队列（带锁）
    """
    with get_lock():
        write_json_file(get_queue_file_path(), queue)


def update_state(**kwargs) -> Dict[str, Any]:
    """
    原子更新状态字段
    """
    with get_lock():
        state = read_json_file(get_state_file_path())
        state.update(kwargs)
        write_json_file(get_state_file_path(), state)
        return state


def get_state_field(key: str, default: Any = None) -> Any:
    """
    获取状态字段（带锁）
    """
    with get_lock():
        state = read_json_file(get_state_file_path())
        return state.get(key, default)


# CLI 接口
def main():
    parser = argparse.ArgumentParser(description="状态管理器")
    parser.add_argument('action', choices=['read', 'write', 'get'],
                        help='操作类型')
    parser.add_argument('--key', help='要获取的键')
    parser.add_argument('--json', help='JSON 字符串（用于 write）')

    args = parser.parse_args()

    if args.action == 'read':
        state = read_state()
        print(json.dumps(state, ensure_ascii=False, indent=2))

    elif args.action == 'get':
        value = get_state_field(args.key)
        print(json.dumps({args.key: value}, ensure_ascii=False, indent=2))

    elif args.action == 'write':
        if not args.json:
            print("错误：write 需要 --json 参数", file=sys.stderr)
            sys.exit(1)
        data = json.loads(args.json)
        write_state(data)
        print("OK")


if __name__ == '__main__':
    main()
