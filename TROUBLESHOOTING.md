# TROUBLESHOOTING.md

Living Agent 常见问题排查指南

---

## 快速诊断

```bash
# 运行健康检查
python ~/.openclaw/skills/living-agent/scripts/health_check.py

# 自动修复常见问题
python ~/.openclaw/skills/living-agent/scripts/auto_fix.py
```

---

## 常见问题

### 1. 微触发一直不启动

**症状**：用户离开很久，但微触发思考从未运行

**原因**：`lastUserMessage` 未更新，管理器误判用户"刚离开"

**解决**：
```bash
# 手动更新 lastUserMessage
python ~/.openclaw/skills/living-agent/src/breaker.py update_last_user_message

# 或运行自动修复
python ~/.openclaw/skills/living-agent/scripts/auto_fix.py
```

**预防**：在 AGENTS.md 添加 WAL Protocol 提醒，每次收到用户消息时更新

---

### 2. 微触发在用户在线时还在运行

**症状**：用户正在聊天，但微触发思考还在执行

**原因**：`lastUserMessage` 太旧（超过 7 天），管理器误判用户"离开很久"

**解决**：
```bash
# 运行自动修复（会检测并修复异常的 lastUserMessage）
python ~/.openclaw/skills/living-agent/scripts/auto_fix.py
```

---

### 3. thinking-queue.json 读取失败

**症状**：健康检查报告"thinking-queue.json 读取失败"

**原因**：文件不存在或格式错误

**解决**：
```bash
# 创建空队列文件
echo '{"questions": []}' > thinking-queue.json

# 或运行安装脚本
python ~/.openclaw/skills/living-agent/scripts/install.py --yes
```

---

### 4. Cron 任务失败（edit 工具错误）

**症状**：cron 任务报告 `edit` 失败

**原因**：Living Agent 的 payload 使用了不稳定的 `edit` 工具

**解决**：
- 这是已知问题，Living Agent v2.4 会修复
- 临时方案：忽略这些错误，它们不影响核心功能

---

### 5. 配置文件字段不一致

**症状**：不同 agent 的 `thinking-state.json` 字段不同

**原因**：历史遗留问题，不同版本的配置格式

**解决**：
```bash
# 标准化所有 workspace 的配置
python ~/.openclaw/skills/living-agent/scripts/standardize_config.py --all

# 或标准化单个 workspace
cd ~/.openclaw/workspace-xxx
python ~/.openclaw/skills/living-agent/scripts/standardize_config.py
```

---

### 6. 思考次数达到上限

**症状**：健康检查显示"今日思考: 50/50 (100%)"

**原因**：达到每日思考上限（默认 50 次）

**解决**：
```json
// 编辑 thinking-state.json
{
  "daily_thoughts_limit": 100  // 增加限额
}
```

---

### 7. 静默时段还在发消息

**症状**：23:00-08:00 期间收到 Living Agent 的消息

**原因**：payload 未检查静默时段，或 `silentHours` 配置错误

**解决**：
```json
// 检查 thinking-state.json
{
  "silentHours": [23, 8]  // 23:00-08:00
}
```

---

### 8. 能量过低，Agent 不思考

**症状**：健康检查显示"能量: 20%"，微触发思考跳过

**原因**：能量系统正常工作，Agent 决定休息

**解决**：
- 这是正常行为，不需要修复
- 静默时段会自动恢复能量
- 或手动恢复：
  ```bash
  python ~/.openclaw/skills/living-agent/src/vital_signs.py recover
  ```

---

### 9. Cron ID 未设置

**症状**：健康检查显示"微触发 cron ID: 未设置"

**原因**：安装时未填入 cron ID

**解决**：
```bash
# 1. 获取 cron ID
openclaw cron list | grep living

# 2. 手动填入 thinking-state.json
{
  "microHeartbeatCronId": "your-cron-id-here"
}

# 或重新运行安装脚本（会自动填入）
python ~/.openclaw/skills/living-agent/scripts/install.py --yes
```

---

### 10. Windows PowerShell 中文乱码

**症状**：运行脚本时中文显示为乱码

**原因**：PowerShell 默认使用 GBK 编码

**解决**：
```powershell
# 在命令前加上 chcp 65001
chcp 65001; python ~/.openclaw/skills/living-agent/scripts/health_check.py
```

---

## 诊断命令

### 检查用户空闲时间
```bash
python ~/.openclaw/skills/living-agent/src/breaker.py idle
```

### 检查静默时段
```bash
python ~/.openclaw/skills/living-agent/src/breaker.py silent
```

### 检查每日限额
```bash
python ~/.openclaw/skills/living-agent/src/breaker.py check_limit
```

### 检查能量状态
```bash
python ~/.openclaw/skills/living-agent/src/vital_signs.py status
```

### 检查思考锁
```bash
python ~/.openclaw/skills/living-agent/src/thinking_lock.py status
```

---

## 日志查看

### 查看 cron 任务运行历史
```bash
openclaw cron runs --id <cron-id>
```

### 查看最近的思考记录
```bash
cat memory/thoughts/$(date +%Y-%m-%d).md
```

---

## 重置和清理

### 重置每日计数
```json
// 编辑 thinking-state.json
{
  "daily_thoughts_count": 0,
  "last_reset_date": ""
}
```

### 清理旧思考记录
```bash
# 删除 7 天前的思考记录
find memory/thoughts/ -name "*.md" -mtime +7 -delete
```

### 完全重置 Living Agent
```bash
# 1. 删除所有 cron 任务
openclaw cron list | grep living | awk '{print $1}' | xargs -I {} openclaw cron remove --id {}

# 2. 删除配置文件
rm thinking-state.json thinking-queue.json

# 3. 重新安装
python ~/.openclaw/skills/living-agent/scripts/install.py --yes
```

---

## 获取帮助

如果以上方法都无法解决问题：

1. 运行健康检查并保存输出：
   ```bash
   python ~/.openclaw/skills/living-agent/scripts/health_check.py > health_report.txt
   ```

2. 查看 Living Agent 版本：
   ```bash
   cat ~/.openclaw/skills/living-agent/VERSION
   ```

3. 在 GitHub 提交 Issue：https://github.com/Linsongrong/living-agent/issues

---

**最后更新**：Living Agent v2.3.2
