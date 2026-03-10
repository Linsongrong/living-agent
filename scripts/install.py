#!/usr/bin/env python3
"""
Living Agent 一键安装脚本（Python 版本）
直接调用 OpenClaw cron API 创建任务
"""

import sys
import os
import json
import subprocess
from pathlib import Path

# Windows PowerShell UTF-8 编码修复
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


def run_command(cmd):
    """运行命令并返回输出"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def detect_agent_id():
    """检测当前 agent ID"""
    cwd = Path.cwd()
    if cwd.name == "workspace":
        return "main"
    elif cwd.name.startswith("workspace-"):
        return cwd.name.replace("workspace-", "")
    else:
        return "main"


def create_cron_job(name, every_ms, payload_file, disabled=False, agent_id="main"):
    """创建 cron 任务"""
    # 读取 payload 文件
    payload_path = Path(payload_file)
    if not payload_path.exists():
        print(f"  ❌ Payload 文件不存在: {payload_file}")
        return None
    
    with open(payload_path, 'r', encoding='utf-8') as f:
        payload = f.read()
    
    # 构建 cron add 命令
    cmd = [
        "openclaw", "cron", "add",
        "--name", name,
        "--every", f"{every_ms // 60000}m",
        "--session", "isolated",
        "--agent", agent_id,
        "--session-key", f"agent:{agent_id}:main",
        "--message", payload,
        "--json"  # 添加 JSON 输出
    ]
    
    if disabled:
        cmd.append("--disabled")
    
    # 执行命令
    print(f"  创建 {name}...")
    
    # 使用 PowerShell 执行（Windows）
    if sys.platform == "win32":
        # 转义特殊字符
        escaped_payload = payload.replace('"', '`"').replace('$', '`$')
        ps_cmd = f'openclaw cron add --name "{name}" --every {every_ms // 60000}m --session isolated --agent {agent_id} --session-key "agent:{agent_id}:main" --message "{escaped_payload}" --json'
        if disabled:
            ps_cmd += " --disabled"
        
        success, stdout, stderr = run_command(ps_cmd)
    else:
        success, stdout, stderr = run_command(" ".join([f'"{c}"' if " " in c else c for c in cmd]))
    
    if success and stdout:
        # 从输出中提取 cron ID
        try:
            result = json.loads(stdout)
            cron_id = result.get('id')
            print(f"  ✅ {name} (ID: {cron_id})")
            return cron_id
        except Exception as e:
            print(f"  ✅ {name} (无法解析 ID: {e})")
            return "unknown"
    else:
        print(f"  ❌ 创建失败: {stderr}")
        return None


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Living Agent 一键安装脚本')
    parser.add_argument('--yes', '-y', action='store_true', help='跳过确认提示')
    args = parser.parse_args()
    
    print("🦞 Living Agent 一键安装脚本\n")
    
    # 1. 检测工作目录
    workspace = Path.cwd()
    print(f"📁 工作目录: {workspace}")
    
    # 2. 检测 agent ID
    agent_id = detect_agent_id()
    print(f"🤖 检测到 agent: {agent_id}\n")
    
    # 3. 检查必要文件
    if not (workspace / "AGENTS.md").exists() and not (workspace / "SOUL.md").exists():
        print("⚠️  警告: 当前目录不像是 OpenClaw workspace")
        if not args.yes:
            response = input("是否继续？(y/n) ")
            if response.lower() != 'y':
                return 1
        else:
            print("  (--yes 模式，自动继续)")

    
    # 4. 复制配置文件
    print("\n📋 复制配置文件...")
    skill_dir = Path.home() / ".openclaw" / "skills" / "living-agent"
    
    for config_file in ["thinking-state.json", "thinking-queue.json"]:
        target = workspace / config_file
        if not target.exists():
            source = skill_dir / "assets" / config_file
            if source.exists():
                import shutil
                shutil.copy(source, target)
                print(f"  ✅ {config_file}")
            else:
                print(f"  ⚠️  源文件不存在: {source}")
        else:
            print(f"  ⏭️  {config_file} 已存在，跳过")
    
    # 5. 创建目录
    print("\n📂 创建目录...")
    (workspace / "memory" / "thoughts").mkdir(parents=True, exist_ok=True)
    print("  ✅ memory/thoughts/")
    
    # 6. 智能配置时区
    print("\n⏰ 配置时区...")
    try:
        import time
        timezone_offset = int(-time.timezone / 3600)
        print(f"  检测到时区偏移: UTC+{timezone_offset}")
        
        # 更新 thinking-state.json
        state_file = workspace / "thinking-state.json"
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            state['timezone_offset'] = timezone_offset
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
            print("  ✅ 已更新 thinking-state.json")
    except Exception as e:
        print(f"  ⚠️  时区配置失败: {e}")
    
    # 7. 创建 cron 任务
    print("\n⏱️  创建 cron 任务...")
    
    cron_ids = {}
    
    # 微触发管理器
    cron_ids['manager'] = create_cron_job(
        f"living-微触发管理器-{agent_id}",
        600000,  # 10 分钟
        skill_dir / "assets" / "micro-trigger-payload.md",
        agent_id=agent_id
    )
    
    # 微触发思考（初始禁用）
    cron_ids['micro'] = create_cron_job(
        f"living-微触发思考-{agent_id}",
        600000,  # 10 分钟
        skill_dir / "assets" / "micro-heartbeat-payload.md",
        disabled=True,
        agent_id=agent_id
    )
    
    # 梦境思考
    cron_ids['dream'] = create_cron_job(
        f"living-梦境思考-{agent_id}",
        10800000,  # 3 小时
        skill_dir / "assets" / "dream-thinking-payload.md",
        agent_id=agent_id
    )
    
    # 自主探索
    cron_ids['explore'] = create_cron_job(
        f"living-自主探索-{agent_id}",
        7200000,  # 2 小时
        skill_dir / "assets" / "exploration-payload.md",
        agent_id=agent_id
    )
    
    # 8. 自动填入 cron ID
    if cron_ids['micro'] and cron_ids['micro'] != "unknown":
        print("\n📝 自动填入 cron ID...")
        state_file = workspace / "thinking-state.json"
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            state['microHeartbeatCronId'] = cron_ids['micro']
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2)
            print(f"  ✅ microHeartbeatCronId = {cron_ids['micro']}")
    
    # 9. 完成
    print("\n✅ 安装完成！\n")
    print("📚 下一步:")
    print(f"  运行健康检查: python {skill_dir / 'scripts' / 'health_check.py'}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
