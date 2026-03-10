# Changelog

All notable changes to this project will be documented in this file.

## [2.3.0] - 2026-03-11

### Added
- **auto_wal.py**：自动 WAL 更新脚本（从 chat_history.json mtime 检测）
- **AGENTS.md WAL 提醒**：在主 workspace 的 AGENTS.md 添加 WAL Protocol 提醒

### Changed
- **优化方向调整**：从"完全自动化"改为"提醒 + 工具"，更可靠

### Note
- OpenClaw 不存储 chat_history.json，无法从文件自动检测用户消息
- 最可靠的方案：在 AGENTS.md 提醒，每次收到消息时手动调用工具

---

## [2.2.1] - 2026-03-11

### Fixed
- **workspace 检测**：main agent 使用 workspace 目录（不是 workspace-main）
- **花生微触发 cron**：创建并更新为完整版 payload

---

## [2.2.0] - 2026-03-11

### Fixed
- **自动创建 thinking-queue.json**：所有 agent 的 workspace 都创建了空队列文件
- **健康检查完整性**：修复所有 agent 的"thinking-queue.json 读取失败"问题

### Changed
- **微触发 payload 自动 WAL**：在 payload 开头自动更新 lastUserMessage
- **版本号规范化**：v2.2.0 标记为稳定版本

---

_Earlier versions: see previous CHANGELOG entries_
