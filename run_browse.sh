#!/bin/bash
# 小红书养号执行脚本
# 由定时任务调用，触发 Agent 执行浏览任务

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$SCRIPT_DIR/logs"
mkdir -p "$LOG_DIR"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="$LOG_DIR/session_$TIMESTAMP.log"

echo "========================================" | tee -a "$LOG_FILE"
echo "小红书养号任务启动" | tee -a "$LOG_FILE"
echo "时间: $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 记录任务启动
echo '{"status": "started", "timestamp": "'$(date -Iseconds)'"}' > "$LOG_DIR/current_session.json"

echo ""
echo "任务已记录，等待 Agent 执行..."
echo "请确保 Agent 已配置此定时任务。"