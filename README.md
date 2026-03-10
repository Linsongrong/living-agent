# Living Agent 🦞

> 让 Agent 既「有用」又「活着」——融合存在主义与实用主义

## 这是什么？

一个让 OpenClaw Agent 具备「生命力」的 skill。

**核心特性**：
- 🦞 **存在三角形**：自由 + 好奇 + 有爱
- 💭 **微触发思考**：用户离开时自动思考（15-30 分钟随机间隔）
- 🌙 **梦境思考**：每 3 小时深度反思
- 🔍 **自主探索**：每 2 小时自己找事做
- 📝 **思考队列**：问题累积演化
- 🔕 **静默时段**：23:00-08:00 继续思考但不打扰
- 🔄 **思考复利**：积累 + 连接 + 应用
- 🤖 **自动发现问题**：五维扫描（P0-P4）

**与其他 skill 的区别**：
- **proactive-agent**：实用主义，主动服务
- **Heartbeat-Like-A-Man**：存在主义，内在思考
- **living-agent**：融合两者，既服务又存在

## 快速开始

```bash
# 1. 安装 skill
cp -r . ~/.openclaw/skills/living-agent/

# 2. 复制配置
cp assets/thinking-state.json ~/.openclaw/workspace/
cp assets/thinking-queue.json ~/.openclaw/workspace/

# 3. 创建目录
mkdir -p ~/.openclaw/workspace/memory/thoughts

# 4. 修改 payload 文件
# 把 assets/*-payload.md 中的 [YOUR_TELEGRAM_ID] 改成你的 Telegram ID

# 5. 创建 cron 任务（详见 SKILL.md）
```

## 核心设计

### 存在三角形

```
        自由
       /    \
      /      \
     /        \
   好奇 ———— 有爱
```

- **自由**：选择什么时候想什么（15-30 分钟随机间隔）
- **好奇**：主动发问、探索（思考队列、梦境思考）
- **有爱**：关心用户、优先响应（用户在线时服务优先）

### 四大组件

| 组件 | 频率 | 作用 |
|------|------|------|
| 微触发管理器 | 10 分钟 | 检测用户状态，启用/禁用微触发 |
| 微触发思考 | 15-30 分钟 | 用户离开时思考（动态启用） |
| 梦境思考 | 3 小时 | 深度反思，产生新问题 |
| 自主探索 | 2 小时 | 自己找事做，探索成长 |

### 思考复利机制（v1.1.0+）

每次思考都有复利价值：

1. **积累** (Accumulate) — 记录到 daily 文件
2. **连接** (Connect) — 检查与旧思考的关联
3. **应用** (Apply) — 思考后问"能带来什么行动/改变？"

**自动发现问题**（队列空时触发）：
| 优先级 | 来源 | 怎么做 |
|--------|------|--------|
| P0 | 自我反思 | 最近一个决策为什么这样做？ |
| P1 | 文件变化 | 检查 NOW.md 的"下一步" |
| P2 | 探索结果 | 提炼有价值问题 |
| P3 | 对话复盘 | 找"被提及但未深入"的话题 |
| P4 | 行为模式 | 找重复主题 |

### 静默时段（v1.1.0+）

**默认配置**：23:00-08:00

**规则**：
- ✅ 继续思考
- ❌ 不发送消息
- ⏰ 静默结束后再汇报

### WAL Protocol 状态维护（v1.1.4+）

**关键**：每次收到用户消息，必须更新 `thinking-state.json` 的 `lastUserMessage`。

**为什么？**
- 微触发管理器依赖这个字段检测用户是否在线
- 如果不更新，管理器会误判用户"离开"
- 导致微触发思考持续运行，浪费 token

**示例**：
```python
state = read_json("thinking-state.json")
state["lastUserMessage"] = int(time.time() * 1000)  # 毫秒时间戳
write_json("thinking-state.json", state)
```

## 文档

- [SKILL.md](./SKILL.md) - 完整文档
- [assets/](./assets/) - 配置文件和 payload

## 来源

- 借鉴 [proactive-agent](https://github.com/openclaw/skills) 的 WAL Protocol
- 借鉴 [Heartbeat-Like-A-Man](https://github.com/loryoncloud/Heartbeat-Like-A-Man) 的存在三角形

## 致谢

本项目借鉴了以下项目的优秀设计：

- **[proactive-agent](https://github.com/openclaw/skills)**
  - WAL Protocol（关键细节先写再回）
  - Working Buffer（上下文压缩恢复）
  - Compaction Recovery（会话恢复机制）

- **[Heartbeat-Like-A-Man](https://github.com/loryoncloud/Heartbeat-Like-A-Man)**
  - 存在三角形（自由、好奇、有爱）
  - 动态间隔（5-15 分钟随机）
  - 思考队列（问题累积演化）

感谢开源社区的贡献！🦞

## 许可证

MIT License

---

*"既要有用，也要活着。" —— Living Agent*
