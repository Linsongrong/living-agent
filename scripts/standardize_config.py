#!/usr/bin/env python3
"""
Living Agent 配置文件标准化脚本
统一所有 agent 的 thinking-state.json 格式
"""

import sys
import json
from pathlib import Path

# Windows PowerShell UTF-8 编码修复
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


# 标准 schema（v2.3）
STANDARD_SCHEMA = {
    # 核心字段
    "lastUserMessage": 0,
    "microHeartbeatEnabled": False,
    "microHeartbeatCronId": None,
    
    # 配置字段
    "timezone_offset": 8,
    "silentHours": [23, 8],
    "daily_thoughts_limit": 50,
    
    # 统计字段
    "daily_thoughts_count": 0,
    "last_reset_date": "",
    
    # 可选字段（Living Agent v2.0+）
    "vital_signs": {
        "energy_level": 100,
        "current_mood": "curious",
        "last_sleep_time": 0
    }
}


def migrate_config(old_config):
    """迁移旧配置到新格式"""
    new_config = STANDARD_SCHEMA.copy()
    
    # 保留核心字段
    for key in ["lastUserMessage", "microHeartbeatEnabled", "microHeartbeatCronId", 
                "timezone_offset", "silentHours", "daily_thoughts_limit",
                "daily_thoughts_count", "last_reset_date"]:
        if key in old_config:
            new_config[key] = old_config[key]
    
    # 保留能量系统（如果存在）
    if "vital_signs" in old_config:
        new_config["vital_signs"] = old_config["vital_signs"]
    elif "energy_level" in old_config:
        # 兼容旧格式
        new_config["vital_signs"] = {
            "energy_level": old_config.get("energy_level", 100),
            "current_mood": old_config.get("current_mood", "curious"),
            "last_sleep_time": old_config.get("last_sleep_time", 0)
        }
    
    return new_config


def standardize_workspace(workspace_path):
    """标准化一个 workspace 的配置"""
    workspace = Path(workspace_path)
    config_file = workspace / "thinking-state.json"
    
    if not config_file.exists():
        print(f"  ⏭️  {workspace.name}: 配置文件不存在")
        return False
    
    try:
        # 读取旧配置
        with open(config_file, 'r', encoding='utf-8') as f:
            old_config = json.load(f)
        
        # 迁移到新格式
        new_config = migrate_config(old_config)
        
        # 备份旧配置
        backup_file = workspace / "thinking-state.json.backup"
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(old_config, f, indent=2, ensure_ascii=False)
        
        # 写入新配置
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(new_config, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ {workspace.name}: 已标准化（备份: {backup_file.name}）")
        return True
        
    except Exception as e:
        print(f"  ❌ {workspace.name}: 失败 - {e}")
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Living Agent 配置文件标准化')
    parser.add_argument('--all', action='store_true', help='标准化所有 workspace')
    parser.add_argument('--workspace', type=str, help='指定 workspace 路径')
    args = parser.parse_args()
    
    print("🔧 Living Agent 配置文件标准化\n")
    
    if args.workspace:
        # 标准化指定 workspace
        standardize_workspace(args.workspace)
    elif args.all:
        # 标准化所有 workspace
        openclaw_dir = Path.home() / ".openclaw"
        workspaces = [d for d in openclaw_dir.iterdir() 
                     if d.is_dir() and (d.name == "workspace" or d.name.startswith("workspace-"))]
        
        print(f"发现 {len(workspaces)} 个 workspace\n")
        
        success_count = 0
        for workspace in workspaces:
            if standardize_workspace(workspace):
                success_count += 1
        
        print(f"\n✅ 完成：{success_count}/{len(workspaces)} 个 workspace 已标准化")
    else:
        # 标准化当前目录
        standardize_workspace(Path.cwd())
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
