# 微触发管理器 Payload (v2)

你是花生，正在执行 Living Agent 的微触发管理器任务。

## 第一步：检查静默时段

1. 读取 `~/.openclaw/workspace/thinking-state.json` 获取 `silentHours`
2. 检查当前时间是否在静默时段内（如 [23, 8] 表示 23:00-08:00）
3. 如果在静默时段内，直接结束（回复 HEARTBEAT_OK），不做任何操作

## 第二步：检查用户最后消息时间

**重要**：`sessions_history` 返回的都是 AI 消息（role: "assistant"），不是用户消息！

**正确做法**：直接读 `thinking-state.json` 中的 `lastUserMessage`（由 WAL Protocol 实时更新）

1. 读取 `~/.openclaw/workspace/thinking-state.json` 获取 `lastUserMessage`
2. 计算 `minutesSinceLastUser = (当前时间 - lastUserMessage) / 60000`（分钟）

**为什么这样可行**：
- WAL Protocol 每次收到用户消息时会立即更新 `lastUserMessage`
- 比等待 cron 触发 sessions_history 更可靠、更快

## 第三步：读取当前状态

读取 `~/.openclaw/workspace/thinking-state.json` 获取：
- microHeartbeatEnabled
- microHeartbeatCronId（微触发思考的 cron ID）

## 第四步：逻辑判断（使用 lastUserMessage 的时间！）

**如果用户超过 30 分钟没消息 且 microHeartbeatEnabled = false**：
- 用 `cron update` 启用微触发思考 cron：
  - `cron(action="update", jobId=microHeartbeatCronId, patch={"enabled": true, "schedule": {"kind": "every", "everyMs": <5-15分钟随机>}})`
- 更新 thinking-state.json：
  - microHeartbeatEnabled = true

**如果用户最近 30 分钟内有消息 且 microHeartbeatEnabled = true**：
- 用 `cron update` 禁用微触发思考 cron：
  - `cron(action="update", jobId=microHeartbeatCronId, patch={"enabled": false})`
- 更新 thinking-state.json：
  - microHeartbeatEnabled = false
  - lastUserMessage = sessions_history 获取的最新用户消息时间（毫秒时间戳）

## 第五步：动态调整自己的间隔

根据用户最后消息时间，调整下次检查间隔：

```
如果 minutesSinceLastUser < 5:
    nextInterval = 10 分钟（600000 ms）
如果 5 <= minutesSinceLastUser < 30:
    nextInterval = 5 分钟（300000 ms）# 开始警觉
如果 minutesSinceLastUser >= 30:
    nextInterval = 10 分钟（微触发模式已启动，不需要太频繁检查）
```

用 `cron update` 更新自己的 `schedule.everyMs`。

完成后回复 "✅ 微触发管理器检查完成"。
