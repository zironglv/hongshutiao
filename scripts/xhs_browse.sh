#!/bin/bash
# 小红书养号浏览脚本
# 使用 chrome-bridge MCP 执行养号任务

set -e

# 配置
KEYWORDS=("红利指数" "股息率" "红利ETF" "高股息" "稳健投资")
POSTS_TO_VIEW=$((RANDOM % 6 + 5))  # 5-10 个帖子
LOG_DIR="hongshutiao/logs"
LOG_FILE="${LOG_DIR}/$(date +%Y-%m-%d)_browse_log.jsonl"
DINGTALK_WEBHOOK="https://oapi.dingtalk.com/robot/send?access_token=2b9b77312e004ab329d64fbdddec83230b4ff95871032418aaff833edbad138f"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 随机选择关键词
KEYWORD=${KEYWORDS[$RANDOM % ${#KEYWORDS[@]}]}
echo "关键词: $KEYWORD"
echo "计划浏览: $POSTS_TO_VIEW 个帖子"

# 记录开始时间
START_TIME=$(date +%s)

# 打开搜索页
echo "=== 步骤 1: 打开小红书搜索页 ==="
mcporter call chrome-bridge chrome_navigate --args '{"url": "https://www.xiaohongshu.com/search_result?keyword=${KEYWORD}&type=51"}' --timeout 30000
sleep 3

# 验证页面加载
TITLE=$(mcporter call chrome-bridge chrome_javascript --args '{"code": "return document.title;"}' --timeout 30000 | jq -r '.result')
echo "页面标题: $TITLE"

# 记录帖子
POSTS_LOG="[]"

# 浏览帖子
for i in $(seq 1 $POSTS_TO_VIEW); do
  echo ""
  echo "=== 浏览第 $i 个帖子 ==="
  
  # 获取最新 ref
  echo "获取页面元素..."
  mcporter call chrome-bridge chrome_read_page --args '{"filter": "interactive"}' --timeout 30000 > /tmp/xhs_page.json
  
  # 找到帖子 ref（从 ref_23 开始，每隔 3 个）
  POST_REF="ref_$((23 + (i - 1) * 3))"
  
  # 点击帖子
  echo "点击帖子 (ref: $POST_REF)..."
  mcporter call chrome-bridge chrome_click_element --args '{"ref": "$POST_REF"}' --timeout 30000 || {
    echo "点击失败，尝试下一个 ref..."
    POST_REF="ref_$((23 + i * 3))"
    mcporter call chrome-bridge chrome_click_element --args '{"ref": "$POST_REF"}' --timeout 30000
  }
  
  sleep 3
  
  # 获取帖子标题
  POST_TITLE=$(mcporter call chrome-bridge chrome_javascript --args '{"code": "return document.title;"}' --timeout 30000 | jq -r '.result')
  echo "帖子标题: $POST_TITLE"
  
  # 滚动浏览
  SCROLL_COUNT=$((RANDOM % 3 + 2))
  echo "滚动 $SCROLL_COUNT 次..."
  for j in $(seq 1 $SCROLL_COUNT); do
    mcporter call chrome-bridge chrome_computer --args '{"action": "scroll", "direction": "down"}' --timeout 30000
    sleep $((RANDOM % 4 + 4))
  done
  
  # 停留
  STAY_TIME=$((RANDOM % 31 + 30))
  echo "停留 $STAY_TIME 秒..."
  sleep $STAY_TIME
  
  # 记录帖子
  POST_DURATION=$STAY_TIME
  POSTS_LOG=$(echo "$POSTS_LOG" | jq --arg title "$POST_TITLE" --arg duration "$POST_DURATION" '. + [{"title": $title, "duration_seconds": ($duration | tonumber)}]')
  
  # 返回搜索结果页
  echo "返回搜索结果页..."
  mcporter call chrome-bridge chrome_keyboard --args '{"keys": "Escape"}' --timeout 30000
  sleep 2
  
  # 验证返回
  TITLE=$(mcporter call chrome-bridge chrome_javascript --args '{"code": "return document.title;"}' --timeout 30000 | jq -r '.result')
  echo "当前页面: $TITLE"
  
  # 随机间隔
  INTERVAL=$((RANDOM % 11 + 5))
  echo "间隔 $INTERVAL 秒..."
  sleep $INTERVAL
done

# 记录结束时间
END_TIME=$(date +%s)
TOTAL_DURATION=$((END_TIME - START_TIME))

# 保存日志
echo ""
echo "=== 保存日志 ==="
LOG_JSON=$(jq -n \
  --arg timestamp "$(date -Iseconds)" \
  --arg keyword "$KEYWORD" \
  --argjson posts "$POSTS_LOG" \
  --arg total_duration "$TOTAL_DURATION" \
  --arg total_posts "$POSTS_TO_VIEW" \
  '{
    "timestamp": $timestamp,
    "browser_type": "chrome-bridge",
    "login_status": "logged_in",
    "keywords_searched": [$keyword],
    "posts_viewed": $posts,
    "total_duration_seconds": ($total_duration | tonumber),
    "total_posts": ($total_posts | tonumber)
  }')

echo "$LOG_JSON" >> "$LOG_FILE"
echo "日志保存到: $LOG_FILE"

# 发送钉钉通知
echo ""
echo "=== 发送钉钉通知 ==="
curl -s -X POST "$DINGTALK_WEBHOOK" \
  -H "Content-Type: application/json" \
  -d "$(jq -n \
    --arg keyword "$KEYWORD" \
    --arg posts "$POSTS_TO_VIEW" \
    --arg duration "$TOTAL_DURATION" \
    '{
      "msgtype": "text",
      "text": {
        "content": "【养号任务完成】靑枫_QwQ\n关键词: $keyword\n浏览: $posts 个帖子\n时长: $duration 秒"
      }
    }')"

echo ""
echo "=== 养号任务完成 ==="
echo "关键词: $KEYWORD"
echo "浏览帖子: $POSTS_TO_VIEW 个"
echo "总时长: $TOTAL_DURATION 秒"