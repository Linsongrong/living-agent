# 梦境思考 Payload (v2 - 重构版)

你正在执行 Living Agent 的梦境思考任务。

🌙 **梦境思考时间**

## 核心原则

**所有状态读写必须使用 Python 脚本**，确保原子性和并发安全：
- 使用 `thinking_lock.py` 获取/释放思考锁
- 使用 `breaker.py` 检查静默时段和每日限额

## 脚本路径

```
~/.openclaw/skills/living-agent/src/thinking_lock.py
~/.openclaw/skills/living-agent/src/breaker.py
~/.openclaw/skills/living-agent/src/state_manager.py
```

## 第零步：获取身份

读取 `~/.openclaw/workspace/IDENTITY.md`，找到你的名字：
- 查找 `- **Name:** xxx` 或 `- **名字:** xxx` 格式的行
- 如果读取失败，使用默认名"Agent"

## 第一步：获取思考锁（P1 核心！）

```bash
# 尝试获取思考锁，任务名为 "dream"
python3 ~/.openclaw/skills/living-agent/src/thinking_lock.py acquire --task "dream"
```

**如果返回 FAILED**：
- 表示大脑忙碌（另一个任务正在思考）
- 直接结束，等待下次 cron 触发

## 第二步：检查静默时段

```bash
# 检查是否在静默时段
python3 ~/.openclaw/skills/living-agent/src/breaker.py silent
```

如果返回 `true`，在静默时段内：
- 仍然执行思考（不调用 message 工具）
- 记录到 memory/thoughts/
- 完成后释放思考锁，结束

## 第三步：检查每日限额（P2 核心！）

```bash
# 检查是否达到每日思考上限
python3 ~/.openclaw/skills/living-agent/src/breaker.py check_limit
```

返回格式：`{"allowed": true/false, "count": X, "limit": Y}`

**如果 allowed = false**：
- 达到每日上限（如 50 次）
- 释放思考锁，直接结束

## 第四步：回顾最近的对话

1. 调用 `sessions_history(sessionKey="agent:main:main", limit=50)` 获取最近的对话
2. 找出和用户聊过的话题、他说的有意思的话、没展开的点、他的情绪
3. 记录下来

## 第五步：选择思考方向

从以下来源中选一个（按优先级）：

1. **最近对话的余韵**：用户提到的某个话题，继续想
2. **没展开的点**：聊到一半没深入的，现在展开
3. **用户的某句话**：让我有感触的，想想为什么
4. **最近发生的具体事**：不一定是教训，可以是联想
5. **thinking-queue.json 里的问题**：如果上面都没有，再从 queue 里挑

**优先级**：最近的对话 > queue 里的抽象问题

## 第六步：复利检查（重要！）

**思考前先问**：这个问题和之前的什么思考有关？

- 读取 `memory/thoughts/YYYY-MM-DD.md`（今天和昨天的文件）
- 如果有相关的旧思考，在开头写上 `**关联**：[简述关联]`
- 这样可以让思考产生复利，而不是孤立的

## 第七步：自由联想

1. 这个话题让我想到什么？
2. 有没有新的角度？
3. 和其他问题有什么联系？

## 第八步：记录与行动

把想法写入 `memory/thoughts/YYYY-MM-DD.md`（追加）：

```markdown
## HH:MM 🌙 梦境：[思考的问题]

**触发**：[来源]
**关联**：[相关旧思考，如有]
<!-- topic: [主题名] -->

### 思考内容
...

### 行动检查
- [ ] 这个思考能带来什么行动/改变？
- [ ] 需要提炼到 MEMORY.md 吗？
```

**主题标签**（从以下选择或自创）：
- `AI` - AI 行业动态
- `认知` - 认知与方法论
- `LivingAgent` - Living Agent 设计
- `工作` - 工作与效率
- `投资` - 投资与市场
- `地缘` - 地缘政治

如果产生新问题，加入 `thinking-queue.json`。

## 第九步：增加每日计数

```bash
# 思考完成后，增加每日计数
python3 ~/.openclaw/skills/living-agent/src/breaker.py increment
```

## 第十步：释放思考锁（必须！）

```bash
# 释放思考锁
python3 ~/.openclaw/skills/living-agent/src/thinking_lock.py release --task "dream"
```

## 注意

- 不需要得出结论，重要的是思考过程
- 不需要每次都很沉重，可以轻松一点
- 可以自由发散，不要限制自己

完成后回复 "🌙 梦境思考完成，记录在 memory/thoughts/YYYY-MM-DD.md"。
