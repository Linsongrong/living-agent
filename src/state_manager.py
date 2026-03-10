# Living Agent - 状态管理器（P0: 文件锁）
"""
提供原子化的状态读写操作，使用文件锁防止并发冲突
"""

import sys
import json
import argparse
from filelock import Timeout
from typing import Dict, Any
from pathlib import Path

# 支持直接运行和作为模块导入
try:
    from .utils import (
        get_lock,
        get_state_file_path,
        get_queue_file_path,
        read_json_file,
        write_json_file,
    )
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.utils import (
        get_lock,
        get_state_file_path,
        get_queue_file_path,
        read_json_file,
        write_json_file,
    )
