# Changelog

All notable changes to this project will be documented in this file.

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

_Earlier versions: see previous CHANGELOG entries_
