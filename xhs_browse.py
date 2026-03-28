#!/usr/bin/env python3
"""
小红书养号脚本
- 随机选择2-4个关键词搜索
- 浏览5-15分钟
- 模拟正常用户行为
"""

import random
import time
import json
import os
from datetime import datetime
from pathlib import Path

# 关键词池
KEYWORDS = [
    "红利指数",
    "股息率",
    "高股息股票",
    "红利ETF",
    "分红策略",
    "稳健投资",
    "价值投资",
    "股票分红",
    "养老投资",
    "被动收入",
    "理财知识",
    "基金定投",
    "投资心得",
    "财务自由",
    "复利投资",
]

# 日志目录
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def log(msg: str, level: str = "INFO"):
    """输出带时间戳的日志"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [{level}] {msg}")


def random_sleep(min_sec: float, max_sec: float):
    """随机等待"""
    sleep_time = random.uniform(min_sec, max_sec)
    log(f"等待 {sleep_time:.1f} 秒...")
    time.sleep(sleep_time)


def simulate_scroll():
    """模拟滚动行为 - 返回 JavaScript 代码"""
    scroll_times = random.randint(3, 6)
    scripts = []
    for _ in range(scroll_times):
        scroll_distance = random.randint(300, 800)
        scripts.append(f"window.scrollBy(0, {scroll_distance});")
    return scripts


def simulate_reading():
    """模拟阅读 - 返回等待时间列表"""
    return [random.uniform(3, 8) for _ in range(random.randint(2, 4))]


def simulate_click_post():
    """模拟点击帖子行为"""
    # 这个函数返回行为描述，实际执行由外部控制
    return {
        "read_time": random.uniform(5, 15),
        "scroll_times": random.randint(1, 3),
    }


def generate_session_report(
    keywords_used: list, 
    duration: float, 
    posts_viewed: int,
    actions: list
) -> dict:
    """生成会话报告"""
    return {
        "timestamp": datetime.now().isoformat(),
        "duration_minutes": round(duration / 60, 1),
        "keywords_searched": keywords_used,
        "posts_viewed": posts_viewed,
        "actions_count": len(actions),
        "actions": actions,
        "status": "completed",
    }


def save_log(report: dict):
    """保存日志到文件"""
    filename = f"xhs_browse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = LOG_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    log(f"日志已保存: {filepath}")
    return filepath


def get_session_params():
    """获取本次会话参数"""
    # 随机选择2-4个关键词
    num_keywords = random.randint(2, 4)
    keywords = random.sample(KEYWORDS, num_keywords)
    
    # 随机浏览时长 5-15 分钟
    duration_minutes = random.uniform(5, 15)
    
    return {
        "keywords": keywords,
        "duration_minutes": duration_minutes,
        "total_seconds": duration_minutes * 60,
    }


if __name__ == "__main__":
    # 输出会话参数供外部调用
    params = get_session_params()
    print(json.dumps(params, ensure_ascii=False))