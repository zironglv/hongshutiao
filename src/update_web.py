#!/usr/bin/env python3
"""红薯条 - 网站数据生成脚本

将采集的数据转换为网站所需的 JSON 格式
"""

import json
import os
import glob
import sys
from datetime import datetime

# 路径配置
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
DOCS_DIR = os.path.join(PROJECT_ROOT, 'docs')
WEB_DATA_DIR = os.path.join(DOCS_DIR, 'data')


def update_website_data():
    """更新网站数据"""
    # 创建网站数据目录
    os.makedirs(WEB_DATA_DIR, exist_ok=True)
    
    # 查找最新数据文件 - 从 history 目录
    history_dir = os.path.join(DATA_DIR, 'history')
    pattern = os.path.join(history_dir, 'dividend_*.json')
    data_files = glob.glob(pattern)
    
    if not data_files:
        print("❌ 未找到数据文件")
        return False
    
    # 获取最新的数据文件
    latest_file = sorted(data_files)[-1]
    print(f"📁 读取数据: {latest_file}")
    
    with open(latest_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 读取分析结果
    analysis_file = os.path.join(DATA_DIR, 'analysis_latest.json')
    if os.path.exists(analysis_file):
        with open(analysis_file, 'r', encoding='utf-8') as f:
            analysis = json.load(f)
        data['market_view'] = analysis.get('market_view', '')
    
    # 写入网站数据
    output_file = os.path.join(WEB_DATA_DIR, 'latest.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 网站数据已更新: {output_file}")
    
    # 同时保存历史数据
    history_file = os.path.join(WEB_DATA_DIR, f"data_{datetime.now().strftime('%Y%m%d')}.json")
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return True


def main():
    """主入口"""
    # 切换到项目根目录
    os.chdir(PROJECT_ROOT)
    
    success = update_website_data()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())