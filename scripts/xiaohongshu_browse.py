#!/usr/bin/env python3
"""小红书养号脚本 - 模拟正常用户浏览行为

功能：
1. 随机时间间隔
2. 搜索红利指数相关关键词
3. 浏览帖子、点赞、收藏
4. 记录浏览日志
5. 学习热门内容
"""

import json
import random
import time
from datetime import datetime
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 搜索关键词池
SEARCH_KEYWORDS = [
    "红利指数",
    "红利低波",
    "股息率",
    "红利ETF",
    "定投红利",
    "红利基金",
    "高股息",
    "稳健投资",
    "被动收入",
    "分红投资",
    "红利指数定投",
    "中证红利",
    "上证红利",
    "红利投资策略",
]

# 行为配置
BEHAVIOR_CONFIG = {
    "min_searches": 2,        # 每次最少搜索数
    "max_searches": 4,        # 每次最多搜索数
    "min_posts": 3,           # 每个搜索最少浏览帖子数
    "max_posts": 8,           # 每个搜索最多浏览帖子数
    "min_scroll_time": 3,     # 最小滚动时间（秒）
    "max_scroll_time": 10,    # 最大滚动时间（秒）
    "like_probability": 0.3,   # 点赞概率
    "collect_probability": 0.2, # 收藏概率
    "comment_probability": 0.1, # 评论概率（暂不实现）
}


def random_sleep(min_sec=1, max_sec=5):
    """随机等待"""
    sleep_time = random.uniform(min_sec, max_sec)
    print(f"⏳ 等待 {sleep_time:.1f} 秒...")
    time.sleep(sleep_time)
    return sleep_time


def select_keywords():
    """随机选择今天要搜索的关键词"""
    num_searches = random.randint(
        BEHAVIOR_CONFIG["min_searches"],
        BEHAVIOR_CONFIG["max_searches"]
    )
    keywords = random.sample(SEARCH_KEYWORDS, num_searches)
    return keywords


def log_browse_session(keywords: list, posts_viewed: int, actions: dict):
    """记录浏览日志"""
    log_file = LOG_DIR / f"browse_{datetime.now().strftime('%Y%m')}.jsonl"
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "keywords": keywords,
        "posts_viewed": posts_viewed,
        "actions": actions,
        "duration_seconds": sum(actions.values()) if actions else 0,
    }
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    print(f"📝 浏览记录已保存")


def get_daily_task():
    """生成今日浏览任务"""
    keywords = select_keywords()
    
    task = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "keywords": keywords,
        "estimated_posts": sum(
            random.randint(BEHAVIOR_CONFIG["min_posts"], BEHAVIOR_CONFIG["max_posts"])
            for _ in keywords
        ),
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }
    
    return task


def main():
    """主函数 - 生成今日任务"""
    print("="*60)
    print("🍠 小红书养号 - 任务生成器")
    print("="*60)
    
    task = get_daily_task()
    
    print(f"\n📅 今日任务 ({task['date']})")
    print(f"关键词: {', '.join(task['keywords'])}")
    print(f"预计浏览帖子: {task['estimated_posts']} 个")
    print(f"\n状态: {task['status']}")
    
    # 保存任务
    task_file = PROJECT_ROOT / "output" / "daily_browse_task.json"
    task_file.parent.mkdir(exist_ok=True)
    
    with open(task_file, "w", encoding="utf-8") as f:
        json.dump(task, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 任务已保存: {task_file}")
    
    return task


if __name__ == "__main__":
    main()