#!/usr/bin/env python3
"""红薯条 - 主程序

整合数据采集、分析、内容生成流程
"""

import logging
import sys
import os
import json
from datetime import datetime

# 切换到项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

from config import INDICES, DATA_DIR
from collector import DividendCollector
from storage import DataStorage
from analyzer import DividendAnalyzer
from generator import ContentGenerator
from news_fetcher import NewsFetcher

# 输出目录
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_daily_task():
    """执行每日任务"""
    logger.info("="*60)
    logger.info("🍠 红薯条 - 开始执行每日任务")
    logger.info(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60)
    
    # 1. 数据采集
    logger.info("\n📥 Step 1: 数据采集")
    collector = DividendCollector()
    raw_data = collector.collect_all()
    
    if not raw_data:
        logger.error("❌ 数据采集失败，任务终止")
        return None
    
    logger.info(f"✅ 成功采集 {len(raw_data)} 个指数数据")
    
    # 2. 数据存储
    logger.info("\n💾 Step 2: 数据存储")
    storage = DataStorage()
    storage.save_daily_data(raw_data)
    logger.info("✅ 数据存储完成")
    
    # 3. 数据分析
    logger.info("\n📊 Step 3: 数据分析")
    analyzer = DividendAnalyzer()
    analysis_result = analyzer.analyze_all(raw_data)
    logger.info(f"✅ 分析完成: {analysis_result['market_view']}")
    
    # 保存分析结果
    analysis_file = os.path.join(DATA_DIR, "analysis_latest.json")
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=2, default=str)
    logger.info(f"📁 分析结果已保存: {analysis_file}")
    
    # 4. 获取新闻（可选，失败不影响主流程）
    logger.info("\n📰 Step 4: 获取新闻")
    news_fetcher = NewsFetcher()
    try:
        news = news_fetcher.fetch_finance_news()
        logger.info(f"✅ 获取到 {len(news)} 条新闻")
    except Exception as e:
        logger.warning(f"⚠️ 新闻获取失败: {e}，跳过")
        news = []
    
    # 5. 生成内容
    logger.info("\n✍️ Step 5: 生成内容")
    content_gen = ContentGenerator()
    post = content_gen.generate_xiaohongshu_post(analysis_result, news)
    content_gen.save_content(post)
    logger.info("✅ 内容生成完成")
    
    # 6. 输出推送消息
    logger.info("\n📤 Step 6: 生成推送消息")
    push_msg = content_gen.generate_push_message(post)
    
    # 保存推送消息
    push_file = os.path.join(OUTPUT_DIR, f"push_{datetime.now().strftime('%Y%m%d')}.txt")
    with open(push_file, 'w', encoding='utf-8') as f:
        f.write(push_msg)
    logger.info(f"✅ 推送消息已保存: {push_file}")
    
    # 7. 更新网站数据
    logger.info("\n🌐 Step 7: 更新网站数据")
    try:
        import update_web
        update_web.update_website_data()
        logger.info("✅ 网站数据更新完成")
    except Exception as e:
        logger.warning(f"⚠️ 网站数据更新失败: {e}")
    
    # 打印结果
    print("\n" + "="*60)
    print(push_msg)
    print("="*60)
    
    return {
        'raw_data': raw_data,
        'analysis': analysis_result,
        'news': news,
        'post': post,
        'push_message': push_msg
    }


def main():
    """主入口"""
    try:
        result = run_daily_task()
        if result:
            logger.info("\n🎉 每日任务执行成功！")
            return 0
        else:
            logger.error("\n❌ 每日任务执行失败")
            return 1
    except Exception as e:
        logger.error(f"\n❌ 任务执行异常: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())