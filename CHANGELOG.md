# Changelog

All notable changes to this project will be documented in this file.

## [1.1.6] - 2026-03-10

### Fixed
- **Working Buffer 重复**：删除重复的 Working Buffer 章节（之前出现两次）
- **配置文件章节缺失**：添加 `## 配置文件` 章节（之前悬空）
- **微触发管理器重复**：移除"微触发时做什么"（已有 §1.5 独立章节）

### Changed
- **通用化描述**：将 "Lin 关注的话题" 改为 "用户关注的话题"
- **通用化示例**：将 `"from": "对话/Lin/梦境/探索"` 改为 `"from": "对话/用户/梦境/探索"`

---

## [1.1.5] - 2026-03-10

### Fixed
- **配置文件补全**：添加缺失的 `silentHours: [23, 8]` 字段
- **频率统一**：微触发间隔从 `[5, 15]` 统一为 `[15, 30]`（减少碎片化）
- **系统架构图**：微触发管理器频率改为"每10分钟"（检查频率），避免混淆

### Added
- **微触发思考章节**：独立章节说明微触发思考做什么（之前混在管理器里）
- **WAL First Thing First 代码示例**：明确如何更新 `lastUserMessage`
- **Working Buffer 检测方法**：如何检测 60% context

### Changed
- **清理重复内容**：定期汇报和思考复利机制整合到统一位置
- **移除重复说明**：微触发管理器部分移除"微触发时做什么"（已有独立章节）

---

## [1.1.4] - 2026-03-10

### Fixed
- **WAL Protocol 状态维护**：明确要求每次收到用户消息时更新 `lastUserMessage`（避免微触发误判）
- **微触发管理器检测方式**：明确使用 `thinking-state.json` 的 `lastUserMessage`，而不是 `sessions_history`

### Added
- **静默时段完整说明**：所有任务在静默时段继续执行但不发送消息
- **文件写入最佳实践**：通用指导，适用于所有组件（推荐 `read` + `write`，避免 `edit` 失败）

### Changed
- **整合状态维护到 WAL Protocol**：作为 "First Thing First" 步骤
- **移除重复的文件写入注意事项**：统一到配置文件后的通用章节

---

## [1.2.1] - 2026-03-09

### Fixed
- **微触发管理器静默时段检查**：修复 micro-trigger-payload.md 缺少 silentHours 检查的 bug（感谢社区反馈）
- 现在两个 payload 都会在 23:00-08:00 静默时段内跳过任务

---

## [1.2.0] - 2026-03-09

### Changed
- **动态身份读取**：payload 自动从 `IDENTITY.md` 读取 agent 名字，无需手动替换
- 移除 `{{AGENT_NAME}}` 占位符，改为运行时动态获取
- 适合多 agent 共享使用（花生、瓜皮、小派、小暖等）

---

## [1.1.1] - 2026-03-09

### Changed
- **通用化模板**：将个性化内容改为通用占位符，适合社区使用
- author 改为 "OpenClaw Community"

---

## [1.1.0] - 2026-03-09

### Added
- **自动发现问题机制**：队列空时触发五维扫描（自我反思/文件变化/探索结果/对话复盘/行为模式）
- **思考主题索引**：`memory/thoughts/index.md` 聚合同主题思考
- **定期提炼检查**：HEARTBEAT.md 加入精华提炼流程

### Changed
- **微触发间隔**：从 [5, 15] 分钟调整为 [15, 30] 分钟，避免碎片化
- **复利检查**：思考前强制检查与旧思考的关联
- **行动检查**：每次思考后问"能带来什么行动/改变？"
- **统一记录格式**：三个 payload 都使用统一的记录模板（触发/关联/主题标签/行动检查）

### Fixed
- 解决思考孤立问题：强制关联旧思考
- 解决队列空就停的问题：自动发现问题
- dream-thinking-payload 和 exploration-payload 缺失 v1.1.0 特性 → 已补齐

---

## [1.0.0] - 2026-03-08

### Added
- 初始版本发布
- 核心组件：
  - 微触发管理器（检测用户状态）
  - 微触发思考（用户离开时思考）
  - 梦境思考（每 3 小时深度反思）
  - 自主探索（每 2 小时自己找事做）
- 核心设计：
  - 存在三角形（自由、好奇、有爱）
  - WAL Protocol（关键细节先写再回）
  - Working Buffer（上下文压缩恢复）
  - 思考队列（问题累积演化）

### Credits
- 借鉴 [proactive-agent](https://github.com/openclaw/skills) 的 WAL Protocol 和 Working Buffer
- 借鉴 [Heartbeat-Like-A-Man](https://github.com/openclaw/skills) 的存在三角形设计
