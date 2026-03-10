# Changelog

All notable changes to this project will be documented in this file.

## [2.2.0] - 2026-03-11

### Fixed
- **自动创建 thinking-queue.json**：所有 agent 的 workspace 都创建了空队列文件
- **健康检查完整性**：修复所有 agent 的"thinking-queue.json 读取失败"问题

### Changed
- **微触发 payload 自动 WAL**：在 payload 开头自动更新 lastUserMessage
- **版本号规范化**：v2.2.0 标记为稳定版本

---

## [2.1.3] - 2026-03-11

### Fixed
- **vital_signs.py 完整恢复**：修复 v2.1.2 误删的 549 行代码
- **能量机制完整**：发呆、闲聊、多巴胺奖励机制全部恢复

---

## [2.1.2] - 2026-03-11 (已废弃)

### Fixed
- **Python 模块直接运行支持**：所有模块添加 try-except 导入

### Broken
- ❌ vital_signs.py 被误删 549 行（已在 v2.1.3 修复）

---

## [2.1.1] - 2026-03-11

### Fixed
- **Windows 兼容性**：修复 UTF-8 编码问题和导入路径

---

## [2.1.0] - 2026-03-11

### Added
- **健康检查脚本** (`scripts/health_check.py`)
- **自动修复脚本** (`scripts/auto_fix.py`)
- **一键安装脚本** (`scripts/install.sh`)
- **简化版 README.md**

---

## [2.0.1] - 2026-03-10

### Added
- **第零步：切换工作目录**：所有 payload 模板都加上了 `cd ~/.openclaw/workspace` 步骤

---

## [2.0.0] - 2026-03-10

### Added
- **动态 agent ID 检测**：根据 cwd 自动识别 agent ID
- **能量与情绪系统**：能量消耗、情绪变化、静默期恢复
- **Python 模块化**：utils.py, breaker.py, vital_signs.py, thinking_lock.py, state_manager.py

---

_Earlier versions omitted for brevity_
