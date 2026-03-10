#!/bin/bash
# Living Agent 一键安装脚本

set -e

echo "🦞 Living Agent 安装向导"
echo ""

# 1. 检测当前工作目录
WORKSPACE=$(pwd)
echo "📁 工作目录: $WORKSPACE"

# 2. 检测 agent ID（从目录名推断）
AGENT_ID=$(basename "$WORKSPACE" | sed 's/workspace-//' | sed 's/^workspace$/main/')
echo "🤖 检测到 agent: $AGENT_ID"
echo ""

# 3. 检查必要文件
if [ ! -f "AGENTS.md" ] && [ ! -f "SOUL.md" ]; then
    echo "⚠️  警告: 当前目录不像是 OpenClaw workspace"
    read -p "是否继续？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 4. 复制配置文件
echo "📋 复制配置文件..."
SKILL_DIR="$HOME/.openclaw/skills/living-agent"

if [ ! -f "thinking-state.json" ]; then
    cp "$SKILL_DIR/assets/thinking-state.json" ./
    echo "  ✅ thinking-state.json"
else
    echo "  ⏭️  thinking-state.json 已存在，跳过"
fi

if [ ! -f "thinking-queue.json" ]; then
    cp "$SKILL_DIR/assets/thinking-queue.json" ./
    echo "  ✅ thinking-queue.json"
else
    echo "  ⏭️  thinking-queue.json 已存在，跳过"
fi

# 5. 创建目录
echo ""
echo "📂 创建目录..."
mkdir -p memory/thoughts
echo "  ✅ memory/thoughts/"

# 6. 智能配置时区
echo ""
echo "⏰ 配置时区..."
if command -v python3 &> /dev/null; then
    TIMEZONE_OFFSET=$(python3 -c "import time; print(int(-time.timezone / 3600))")
    echo "  检测到时区偏移: UTC+$TIMEZONE_OFFSET"
    
    # 更新 thinking-state.json
    python3 -c "
import json
with open('thinking-state.json', 'r') as f:
    state = json.load(f)
state['timezone_offset'] = $TIMEZONE_OFFSET
with open('thinking-state.json', 'w') as f:
    json.dump(state, f, indent=2)
"
    echo "  ✅ 已更新 thinking-state.json"
else
    echo "  ⚠️  未检测到 python3，跳过时区配置"
fi

# 7. 创建 cron 任务
echo ""
echo "⏱️  创建 cron 任务..."
echo "  注意: 需要手动运行以下命令（OpenClaw CLI 不支持脚本调用）"
echo ""
echo "# 1. 微触发管理器（每 10 分钟检查用户状态）"
echo "openclaw cron add \"living-微触发管理器-$AGENT_ID\" \\"
echo "  --every 600000 \\"
echo "  --session-target isolated \\"
echo "  --payload-file \"$SKILL_DIR/assets/micro-trigger-payload.md\""
echo ""
echo "# 2. 微触发思考（初始禁用，由管理器动态启用）"
echo "openclaw cron add \"living-微触发思考-$AGENT_ID\" \\"
echo "  --every 600000 \\"
echo "  --session-target isolated \\"
echo "  --disabled \\"
echo "  --payload-file \"$SKILL_DIR/assets/micro-heartbeat-payload.md\""
echo ""
echo "# 3. 梦境思考（每 3 小时）"
echo "openclaw cron add \"living-梦境思考-$AGENT_ID\" \\"
echo "  --every 10800000 \\"
echo "  --session-target isolated \\"
echo "  --payload-file \"$SKILL_DIR/assets/dream-thinking-payload.md\""
echo ""
echo "# 4. 自主探索（每 2 小时）"
echo "openclaw cron add \"living-自主探索-$AGENT_ID\" \\"
echo "  --every 7200000 \\"
echo "  --session-target isolated \\"
echo "  --payload-file \"$SKILL_DIR/assets/exploration-payload.md\""
echo ""
echo "创建完成后，运行以下命令获取 cron ID："
echo "openclaw cron list | grep living"
echo ""
echo "然后手动填入 thinking-state.json 的 microHeartbeatCronId 字段"
echo ""
echo "✅ 安装向导完成！"
echo ""
echo "📚 下一步："
echo "  1. 运行上面的 cron 命令"
echo "  2. 填入 cron ID 到 thinking-state.json"
echo "  3. 运行健康检查: python3 $SKILL_DIR/scripts/health_check.py"
