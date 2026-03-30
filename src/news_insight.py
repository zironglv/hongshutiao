#!/usr/bin/env python3
"""红薯条 - 新闻观点提炼模块

从新闻中提炼有价值的市场观点
"""

import json
import logging
import os
import re
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')


class NewsInsightExtractor:
    """从新闻中提炼观点"""

    # 关键词映射到观点模板
    INSIGHT_RULES = {
        # 上涨信号
        '涨': {
            'pattern': r'涨[0-9.]+%',
            'template': '📈 市场信号：红利资产表现活跃，{match}显示资金关注度提升',
            'type': 'positive',
        },
        '上涨': {
            'pattern': r'上涨[0-9.]+%',
            'template': '📈 市场信号：红利指数{match}，防御属性受青睐',
            'type': 'positive',
        },
        
        # 下跌信号
        '跌': {
            'pattern': r'跌[0-9.]+%',
            'template': '📉 市场信号：红利资产短期调整，{match}',
            'type': 'negative',
        },
        
        # 份额变化
        '份额增': {
            'pattern': r'份额增[0-9.]+',
            'template': '💰 资金动向：红利ETF份额增加，资金持续流入',
            'type': 'positive',
        },
        '份额减': {
            'pattern': r'份额减[0-9.]+',
            'template': '⚠️ 资金动向：部分红利ETF份额减少，注意资金流向',
            'type': 'neutral',
        },
        
        # 防御属性
        '防御': {
            'pattern': r'防御',
            'template': '🛡️ 市场观点：红利资产防御属性凸显，适合震荡市配置',
            'type': 'positive',
        },
        
        # 高股息
        '高股息': {
            'pattern': r'高股息',
            'template': '💎 投资价值：高股息策略持续受关注，稳健收益属性明显',
            'type': 'positive',
        },
        
        # 分红
        '分红': {
            'pattern': r'分红',
            'template': '💰 公司动态：上市公司分红数据亮眼，红利策略基本面支撑强',
            'type': 'positive',
        },
        
        # 净值/收益
        '超额收益': {
            'pattern': r'超额收益',
            'template': '📊 基金表现：红利基金实现超额收益，策略有效性验证',
            'type': 'positive',
        },
        
        # 机构观点
        '机构': {
            'pattern': r'机构.*称|机构.*观点',
            'template': '🏛️ 机构观点：{match}',
            'type': 'neutral',
        },
        
        # 缩水/赎回
        '缩水': {
            'pattern': r'缩水|赎回超',
            'template': '⚠️ 资金动向：部分红利基金规模缩减，市场存在分歧',
            'type': 'negative',
        },
    }

    def __init__(self):
        self.cache_file = os.path.join(DATA_DIR, 'news_insight.json')

    def extract_insights(self, news_list: List[Dict[str, Any]], max_insights: int = 3) -> List[Dict[str, Any]]:
        """从新闻中提炼观点

        Args:
            news_list: 新闻列表
            max_insights: 最大观点数量

        Returns:
            观点列表，每条包含 content, type, source_news
        """
        insights = []
        seen_types = set()  # 避免重复类型的观点

        for news in news_list:
            title = news.get('title', '')
            summary = news.get('summary', '')
            content = title + ' ' + summary

            # 尝试匹配规则
            for keyword, rule in self.INSIGHT_RULES.items():
                if keyword in content:
                    pattern = rule['pattern']
                    match = re.search(pattern, content)
                    
                    if match:
                        insight_type = rule['type']
                        
                        # 避免重复类型（但允许不同来源的同类观点）
                        if insight_type not in seen_types or len(insights) < 2:
                            match_text = match.group(0)
                            
                            # 替换模板中的占位符
                            template = rule['template']
                            if '{match}' in template:
                                insight_content = template.replace('{match}', match_text)
                            else:
                                insight_content = template

                            insights.append({
                                'content': insight_content,
                                'type': insight_type,
                                'source': news.get('source', ''),
                                'source_title': title[:50],
                            })

                            seen_types.add(insight_type)

                            if len(insights) >= max_insights:
                                break

            if len(insights) >= max_insights:
                break

        # 如果没提取到观点，生成默认观点
        if not insights and news_list:
            insights.append({
                'content': '📰 市场动态：红利指数相关新闻持续更新，建议关注资金流向变化',
                'type': 'neutral',
                'source': '综合',
                'source_title': '',
            })

        return insights

    def generate_summary(self, news_list: List[Dict[str, Any]], dividend_data: Dict[str, Any] = None) -> str:
        """生成综合观点摘要

        Args:
            news_list: 新闻列表
            dividend_data: 股息率数据（可选）

        Returns:
            观点摘要文本
        """
        insights = self.extract_insights(news_list, max_insights=3)

        # 统计观点类型
        positive_count = sum(1 for i in insights if i['type'] == 'positive')
        negative_count = sum(1 for i in insights if i['type'] == 'negative')

        # 生成情绪判断
        if positive_count > negative_count:
            sentiment = '整体偏积极'
        elif negative_count > positive_count:
            sentiment = '存在谨慎信号'
        else:
            sentiment = '多空交织'

        # 构建摘要
        lines = []
        lines.append(f"**{sentiment}**")
        lines.append("")
        
        for insight in insights:
            lines.append(insight['content'])
            if insight['source']:
                lines.append(f"   _来源: {insight['source']}_")
            lines.append("")
        
        return '\n'.join(lines)


def extract_news_insights(news_list: List[Dict[str, Any]], max_insights: int = 3) -> List[Dict[str, Any]]:
    """便捷函数"""
    extractor = NewsInsightExtractor()
    return extractor.extract_insights(news_list, max_insights)


def generate_news_summary(news_list: List[Dict[str, Any]], dividend_data: Dict[str, Any] = None) -> str:
    """便捷函数"""
    extractor = NewsInsightExtractor()
    return extractor.generate_summary(news_list, dividend_data)


if __name__ == '__main__':
    # 测试
    import sys
    sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))
    from news_tavily import TavilyNewsFetcher

    logging.basicConfig(level=logging.INFO)

    fetcher = TavilyNewsFetcher()
    news = fetcher.fetch_news(5)

    print(f"\n获取到 {len(news)} 条新闻")
    print("\n" + "="*50)
    print("提炼的观点:")
    print("="*50)

    extractor = NewsInsightExtractor()
    insights = extractor.extract_insights(news)

    for i, insight in enumerate(insights, 1):
        print(f"\n{i}. {insight['content']}")
        print(f"   类型: {insight['type']} | 来源: {insight['source']}")

    print("\n" + "="*50)
    print("综合摘要:")
    print("="*50)
    print(extractor.generate_summary(news))