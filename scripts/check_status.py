#!/usr/bin/env python3
"""
状态检查脚本
检查预处理流水线的当前状态
"""

import os
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path.home() / ".copaw/workspaces/qwq-automation/hongshutiao"


def check_status(date_str=None):
    """检查指定日期的预处理状态"""
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    date_dir = BASE_DIR / "data" / date_str
    content_dir = BASE_DIR / "content" / date_dir
    assets_dir = BASE_DIR / "assets" / date_dir
    
    checks = {
        "date": date_str,
        "raw_data": (date_dir / "raw.json").exists(),
        "analyzed_data": (date_dir / "analyzed.json").exists(),
        "content": (content_dir / "content.json").exists(),
        "cover_1": (assets_dir / "cover_1.png").exists(),
        "cover_2": (assets_dir / "cover_2.png").exists(),
        "cover_3": (assets_dir / "cover_3.png").exists(),
    }
    
    # 计算整体状态
    all_ready = all(v for k, v in checks.items() if k != "date")
    
    # 确定阶段
    if checks["raw_data"]:
        stage = "数据已采集"
    elif checks["analyzed_data"]:
        stage = "数据已分析"
    elif checks["content"]:
        stage = "内容已生成"
    elif checks["cover_1"] and checks["cover_2"] and checks["cover_3"]:
        stage = "封面已生成"
    else:
        stage = "未开始"
    
    if all_ready:
        stage = "预处理完成，可发布"
    
    # 读取状态文件
    status_file = BASE_DIR / "status" / "pipeline_state.json"
    if status_file.exists():
        with open(status_file) as f:
            state_data = json.load(f)
        checks["pipeline_state"] = state_data.get("state", "unknown")
    
    return {
        "date": date_str,
        "checks": checks,
        "all_ready": all_ready,
        "stage": stage
    }


def print_status(result):
    """打印状态结果"""
    print(f"\n📊 红利日报状态检查 ({result['date']})")
    print("=" * 40)
    
    checks = result["checks"]
    for key, value in checks.items():
        if key == "date" or key == "pipeline_state":
            continue
        status = "✅" if value else "❌"
        print(f"  {status} {key}")
    
    if "pipeline_state" in checks:
        print(f"\n  流水线状态: {checks['pipeline_state']}")
    
    print(f"\n  当前阶段: {result['stage']}")
    print(f"  可发布: {'YES' if result['all_ready'] else 'NO'}")
    print("=" * 40)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="检查预处理状态")
    parser.add_argument("--date", help="指定日期 (YYYY-MM-DD)")
    args = parser.parse_args()
    
    result = check_status(args.date)
    print_status(result)