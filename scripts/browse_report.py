#!/usr/bin/env python3
"""小红书浏览行为汇报脚本

检查浏览日志，评估质量，汇报给用户
"""

import json
from datetime import datetime, date
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
INSIGHTS_FILE = LOG_DIR / "user_insights.json"

# 质量标准
QUALITY_STANDARDS = {
    "min_duration": 300,      # 最少5分钟
    "max_duration": 900,      # 最多15分钟
    "min_posts": 5,           # 最少浏览帖子数
    "max_posts": 20,          # 最多浏览帖子数
    "min_keywords": 2,        # 最少搜索关键词数
    "max_keywords": 4,        # 最多搜索关键词数
}


def check_today_logs():
    """检查今日浏览日志"""
    today = date.today().strftime("%Y%m")
    log_file = LOG_DIR / f"browse_{today}.jsonl"
    
    if not log_file.exists():
        return None, "今日未执行浏览任务"
    
    logs = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                logs.append(json.loads(line))
    
    # 找到今天的记录
    today_str = date.today().isoformat()
    today_logs = [
        log for log in logs 
        if log.get("timestamp", "").startswith(today_str)
    ]
    
    if not today_logs:
        return None, "今日未执行浏览任务"
    
    return today_logs[-1], "今日已完成浏览任务"


def evaluate_quality(log: dict) -> dict:
    """评估浏览质量"""
    issues = []
    
    duration = log.get("duration_seconds", 0)
    if duration < QUALITY_STANDARDS["min_duration"]:
        issues.append(f"浏览时长过短 ({duration}秒 < 300秒)")
    elif duration > QUALITY_STANDARDS["max_duration"]:
        issues.append(f"浏览时长过长 ({duration}秒 > 900秒)")
    
    posts = log.get("posts_viewed", 0)
    if posts < QUALITY_STANDARDS["min_posts"]:
        issues.append(f"浏览帖子过少 ({posts} < 5)")
    elif posts > QUALITY_STANDARDS["max_posts"]:
        issues.append(f"浏览帖子过多 ({posts} > 20)")
    
    keywords = len(log.get("keywords", []))
    if keywords < QUALITY_STANDARDS["min_keywords"]:
        issues.append(f"搜索关键词过少 ({keywords} < 2)")
    elif keywords > QUALITY_STANDARDS["max_keywords"]:
        issues.append(f"搜索关键词过多 ({keywords} > 4)")
    
    actions = log.get("actions", {})
    if not actions.get("likes") and not actions.get("collects"):
        issues.append("无互动行为（点赞/收藏）")
    
    return {
        "passed": len(issues) == 0,
        "issues": issues,
        "score": max(0, 100 - len(issues) * 20)
    }


def generate_report():
    """生成汇报内容"""
    log, status = check_today_logs()
    
    report = {
        "date": date.today().isoformat(),
        "status": status,
        "quality": None,
        "details": None,
        "insights": None
    }
    
    if log:
        report["details"] = {
            "keywords": log.get("keywords", []),
            "posts_viewed": log.get("posts_viewed", 0),
            "duration_seconds": log.get("duration_seconds", 0),
            "actions": log.get("actions", {}),
            "timestamp": log.get("timestamp", "")
        }
        report["quality"] = evaluate_quality(log)
        
        # 加载洞察
        if INSIGHTS_FILE.exists():
            with open(INSIGHTS_FILE, "r", encoding="utf-8") as f:
                report["insights"] = json.load(f)
    
    return report


def format_report_for_dingtalk(report: dict) -> str:
    """格式化为钉钉消息"""
    lines = []
    lines.append("## 📊 小红书养号日报")
    lines.append(f"\n**日期**: {report['date']}")
    lines.append(f"\n**状态**: {report['status']}")
    
    if report["details"]:
        details = report["details"]
        lines.append(f"\n### 浏览详情")
        lines.append(f"- 搜索关键词: {', '.join(details['keywords'])}")
        lines.append(f"- 浏览帖子: {details['posts_viewed']} 个")
        lines.append(f"- 浏览时长: {details['duration_seconds']} 秒")
        
        actions = details.get("actions", {})
        if actions:
            lines.append(f"- 互动行为: 点赞 {actions.get('likes', 0)} 次, 收藏 {actions.get('collects', 0)} 次")
    
    if report["quality"]:
        quality = report["quality"]
        lines.append(f"\n### 质量评估")
        lines.append(f"- 评分: {quality['score']} 分")
        lines.append(f"- 结果: {'✅ 通过' if quality['passed'] else '⚠️ 需改进'}")
        if quality["issues"]:
            lines.append(f"- 问题: {', '.join(quality['issues'])}")
    
    if report["insights"]:
        insights = report["insights"]
        if insights.get("user_questions"):
            lines.append(f"\n### 用户关心的问题")
            for q in insights["user_questions"][:3]:
                lines.append(f"- {q}")
    
    return "\n".join(lines)


def main():
    """主函数"""
    report = generate_report()
    
    print("="*60)
    print("📊 小红书浏览行为日报")
    print("="*60)
    
    print(f"\n📅 日期: {report['date']}")
    print(f"📌 状态: {report['status']}")
    
    if report["details"]:
        details = report["details"]
        print(f"\n🔍 搜索关键词: {', '.join(details['keywords'])}")
        print(f"📝 浏览帖子: {details['posts_viewed']} 个")
        print(f"⏱️ 浏览时长: {details['duration_seconds']} 秒")
        
        actions = details.get("actions", {})
        if actions:
            print(f"💬 互动: 点赞 {actions.get('likes', 0)}, 收藏 {actions.get('collects', 0)}")
    
    if report["quality"]:
        quality = report["quality"]
        print(f"\n📊 质量评分: {quality['score']} 分")
        if quality["issues"]:
            print(f"⚠️ 问题: {', '.join(quality['issues'])}")
        else:
            print("✅ 质量通过！")
    
    # 输出钉钉格式
    dingtalk_msg = format_report_for_dingtalk(report)
    print("\n" + "="*60)
    print("钉钉消息格式:")
    print("="*60)
    print(dingtalk_msg)
    
    return report


if __name__ == "__main__":
    main()