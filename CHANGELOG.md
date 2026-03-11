# Changelog

All notable changes to this project will be documented in this file.

## [3.0.0] - 2026-03-11

### 🎉 Major Refactor: From "Pretending to be Alive" to "Truly Alive"

**Breaking Changes:**
- Removed micro-trigger manager and micro-trigger thinking
- Changed core architecture from 4 functions to 2 functions + wisdom sedimentation

### Removed
- **微触发管理器** — WAL Protocol already handles user state detection
- **微触发思考** — Overlaps with dream thinking, produces fragmented output, low ROI

### Added
- **智慧沉淀机制** (Wisdom Sedimentation)
  - `memory/pending-insights.md` for accumulating insights
  - Dynamic trigger when >= 10 insights accumulated
  - Manual integration into MEMORY.md in main session
- **sessions_history 上下文** — Isolated sessions can now access conversation context

### Changed
- **梦境思考** (Dream Thinking)
  - From: systemEvent → main session
  - To: isolated + sessions_history
  - Reason: Has context without consuming main session, doesn't interrupt conversation
- **自主探索** (Autonomous Exploration)
  - Added context recovery steps (read SOUL.md + NOW.md + thoughts)
  - Only executes when user is away > 30 minutes
  - Differentiated exploration directions for multiple agents

### Optimized
- Reduced from 15 cron tasks to 3 tasks
- Complete growth loop: Think → Explore → Sediment
- Better cost-benefit ratio

### Key Insights
- "活着"的最小单元不是思考频率，而是上下文连续性
- 一个有上下文的深度思考 > 十个没上下文的浅层思考
- 灵光一现不是独立功能，是思考质量足够高时的副产品
- 智慧沉淀需要：提炼 → 归纳 → 应用 → 迭代

### Documentation
- Added `docs/refactor-2026-03-11.md` — Complete refactor record
- Rewrote SKILL.md for v3.0 architecture
- Updated installation guide and best practices

---

## [2.3.3] - 2026-03-11

### Removed
- **install.py**：移除 Python 安装脚本（Windows 兼容性问题太多）
- 保留 `install.sh`（Bash 脚本，输出命令让用户手动执行）

### Fixed
- 清理了 16 个测试/重复 cron 任务

---

## [2.3.2] - 2026-03-11

### Added
- **standardize_config.py**：配置文件标准化脚本
- **TROUBLESHOOTING.md**：故障排查文档

### Fixed
- 统一所有 agent 的 thinking-state.json 格式

---

## [2.3.1] - 2026-03-11

### Added
- **install.py**：Python 一键安装脚本（实验性，后续移除）

---

## [2.3.0] - 2026-03-11

### Added
- **auto_wal.py**：自动 WAL 更新脚本
- **AGENTS.md WAL 提醒**：在主 workspace 添加 WAL Protocol 提醒

---

_Earlier versions: see git history_
