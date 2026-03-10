# 微触发管理器 Payload (v2 - 重构版)

你是花生，正在执行 Living Agent 的微触发管理器任务。

## 核心原则

**所有状态读写必须使用 Python 脚本**，确保原子性和并发安全：
- 使用 `thinking_lock.py` 管理思考锁
- 使用 `breaker.py` 检查静默时段和用户空闲时间

## 脚本路径

```
~/.openclaw/skills/living-agent/src/thinking_lock.py
~/.openclaw/skills/living-agent/src/breaker.py
~/.openclaw/skills/living-agent/src/state_manager.py
```

## 第一步：检查静默时段

```bash
# 检查是否在静默时段
python3 ~/.openclaw/skills/living-agent/src/breaker.py silent
```

如果返回 `true`，直接在静默时段内，结束任务（回复 HEARTBEAT_OK）。

## 第二步：检查用户最后消息时间

**重要**：`sessions_history` 返回的都是 AI 消息（role: "assistant"），不是用户消息！

**正确做法**：使用 breaker.py 获取用户空闲时间

```bash
# 获取用户空闲分钟数
python3 ~/.openclaw/skills/living-agent/src/breaker.py idle
```

**返回值**：用户空闲的分钟数

**为什么这样可行**：
- 优先使用 WAL 更新的 lastUserMessage
- 如果没有，回退到读取 chat_history.json 的 mtime

## 第三步：读取当前状态

```bash
# 读取完整状态
python3 ~/.openclaw/skills/living-agent/src/state_manager.py read
```

获取：
- microHeartbeatEnabled
- microHeartbeatCronId（微触发思考的 cron ID）

## 第四步：逻辑判断

**如果用户超过 30 分钟没消息 且 microHeartbeatEnabled = false**：
- 用 `cron update` 启用微触发思考 cron：
  - `cron(action="update", jobId=microHeartbeatCronId, patch={"enabled": true, "schedule": {"kind": "every", "everyMs": <5-15分钟随机>}})`
- 更新 thinking-state.json：
  ```bash
  python3 ~/.openclaw/skills/living-agent/src/state_manager.py write --json '{"microHeartbeatEnabled": true}'
  ```

**如果用户最近 30 分钟内有消息 且 microHeartbeatEnabled = true**：
- 用 `cron update` 禁用微触发思考 cron：
  - `cron(action="update", jobId=microHeartbeatCronId, patch={"enabled": false})`
- 更新 thinking-state.json：
  ```bash
  python3 ~/.openclaw/skills/living-agent/src/state_manager.py write --json '{"microHeartbeatEnabled": false}'
  ```

## 第五步：动态调整自己的间隔

根据用户空闲时间，调整下次检查间隔：

```
如果 minutesSinceLastUser < 5:
    nextInterval = 10 分钟（600000 ms）
如果 5 <= minutesSinceLastUser < 30:
    nextInterval = 5 分钟（300000 ms）# 开始警觉
如果 minutesSinceLastUser >= 30:
    nextInterval = 10 分钟（微触发模式已启动，不需要太频繁检查）
```

用 `cron update` 更新自己的 `schedule.everyMs`。

## 第六步：更新 lastUserMessage（可选优化）

如果想使用文件 mtime 方式检测用户活跃，可以更新 lastUserMessage：

```bash
# 获取用户最后活跃时间（毫秒）
python3 ~/.openclaw/skills/living-agent/src/breaker.py idle
```

但这不是必须的，breaker.py 会自动回退到 mtime 方式。

完成后回复 "✅ 微触发管理器检查完成"。
