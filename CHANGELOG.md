# Changelog

All notable changes to this project will be documented in this file.

## [1.2.3] - 2026-03-10

### Fixed
- **silentHours 逻辑修正**
  - 之前：静默时段内"不思考"（错误）
  - 现在：静默时段内"继续思考，但不发送消息"（正确）
  - 影响：微触发思考任务
  - 微触发管理器：移除静默时段检查（由微触发思考处理）

---

## [1.2.2] - 2026-03-10

### Fixed
- **设计缺陷修复：队列空时自动发现问题**
  - 之前：cron 任务 payload 只说"选择问题思考"，队列空时直接 HEARTBEAT_OK
  - 现在：队列空时按 P0-P4 优先级自动发现问题（自我反思、检查 NOW.md、对话复盘等）
  - 影响：所有使用微触发任务的 agent
  - 根本原因：payload 文档（micro-heartbeat-payload.md）写得很详细，但 cron 任务用的是简化版

---

## [1.2.1] - 2026-03-09

### Fixed
- **微触发管理器静默时段检查**：修复 micro-trigger-payload.md 缺少 silentHours 检查的 bug
- 现在两个 payload 都会在静默时段内跳过任务

---

## [1.2.0] - 2026-03-09

### Changed
- **动态身份读取**：payload 自动从 `IDENTITY.md` 读取 agent 名字，无需手动替换
- 移除 `{{AGENT_NAME}}` 占位符，改为运行时动态获取
- 适合多 agent 共享使用

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
