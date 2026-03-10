# Living Agent - 思考锁（P1: 状态机）
"""
提供思考锁机制，防止多个思考任务同时执行
"""

import sys
import argparse
from filelock import Timeout
from pathlib import Path

# 支持直接运行和作为模块导入
try:
    from .utils import get_lock, get_current_timestamp_ms, read_json_file, write_json_file, get_state_file_path
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.utils import get_lock, get_current_timestamp_ms, read_json_file, write_json_file, get_state_file_path
