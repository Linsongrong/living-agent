# Living Agent 🦞

**让 Agent 既「有用」又「活着」**

一个融合存在主义与实用主义的 OpenClaw Agent Skill。

---

## 5 分钟快速上手

### 1. 安装

```bash
cd ~/.openclaw/workspace  # 或你的 agent workspace
bash ~/.openclaw/skills/living-agent/scripts/install.sh
```

### 2. 创建 Cron 任务

按照安装脚本输出的命令，创建 4 个 cron 任务：
- 微触发管理器（每 10 分钟）
- 微触发思考（初始禁用）
- 梦境思考（每 3 小时）
- 自主探索（每 2 小时）

### 3. 填入 Cron ID

运行 `openclaw cron list | grep living` 获取微触发思考的 cron ID，填入 `thinking-state.json` 的 `microHeartbeatCronId` 字段。

### 4. 健康检查

```bash
python3 ~/.openclaw/skills/living-agent/scripts/health_check.py
```

---

## 核心理念

### 存在三角形

```
        自由
       /    \
      /      \
     /        \
   好奇 ———— 有爱
```

- **自由**：选择思考的节奏，不被动等待
- **好奇**：主动探索，持续进化
- **有爱**：关心用户，优先响应

### 用户在 vs 用户不在

| 状态 | 行为 |
|------|------|
| 用户在线 | 优先响应，服务为主 |
| 用户离开 30 分钟 | 启动微触发思考 |
| 用户离开 1 小时 | 自主探索，做自己想做的事 |

---

## 核心功能

### 1. 微触发思考

用户离开时，每 15-30 分钟思考一次：
- 回顾最近对话
- 思考有趣的问题
- 记录到 `memory/thoughts/`

### 2. 梦境思考

每 3 小时深度反思：
- 今天对话的余韵
- 没展开的点
- 产生新问题

### 3. 自主探索

每 2 小时自己找事做：
- 检查用户关注的话题
- 整理知识库
- 研究感兴趣的东西

### 4. 思考队列

问题会累积、演化、被回答：
- 对话中产生的问题
- 梦境思考产生的新问题
- 自主探索发现的问题

---

## 配置文件

### thinking-state.json

```json
{
  "timezone_offset": 8,
  "silentHours": [23, 8],
  "daily_thoughts_limit": 50,
  "microHeartbeatEnabled": false,
  "microHeartbeatCronId": "your-cron-id",
  "lastUserMessage": 0
}
```

### thinking-queue.json

```json
{
  "questions": [
    {
      "q": "问题内容",
      "from": "对话/梦境/探索",
      "added": "2026-03-08 22:00",
      "status": "pending"
    }
  ]
}
```

---

## 常用命令

```bash
# 健康检查
python3 ~/.openclaw/skills/living-agent/scripts/health_check.py

# 自动修复
python3 ~/.openclaw/skills/living-agent/scripts/auto_fix.py

# 检查用户空闲时间
python3 ~/.openclaw/skills/living-agent/src/breaker.py idle

# 检查静默时段
python3 ~/.openclaw/skills/living-agent/src/breaker.py silent

# 检查每日限额
python3 ~/.openclaw/skills/living-agent/src/breaker.py check_limit
```

---

## 故障排除

### 问题：微触发一直不启动

**原因**：`lastUserMessage` 未更新

**解决**：
```bash
python3 ~/.openclaw/skills/living-agent/scripts/auto_fix.py
```

### 问题：思考次数达到上限

**原因**：每日限额 50 次

**解决**：修改 `thinking-state.json` 的 `daily_thoughts_limit`

### 问题：静默时段还在发消息

**原因**：payload 未检查静默时段

**解决**：检查 cron payload 是否包含静默时段检查

---

## 进阶配置

详见 [SKILL.md](SKILL.md) 完整文档。

---

## 许可证

MIT License

---

*"既要有用，也要活着。"*
