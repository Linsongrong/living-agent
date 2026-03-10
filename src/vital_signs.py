# Living Agent - 能量与情绪系统 (v2.0)
"""
提供能量流转、情绪管理、前后台行为隔离等功能
"""

import sys
import json
import argparse
import random
from typing import Dict, Any
from pathlib import Path

# 支持直接运行和作为模块导入
try:
    from .utils import (
        get_lock,
        get_state_file_path,
        read_json_file,
        write_json_file,
        get_current_timestamp_ms,
        get_chat_history_path,
    )
    from .breaker import is_in_silent_hours
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from src.utils import (
        get_lock,
        get_state_file_path,
        read_json_file,
        write_json_file,
        get_current_timestamp_ms,
        get_chat_history_path,
    )
    from src.breaker import is_in_silent_hours
