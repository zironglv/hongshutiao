#!/usr/bin/env python3
"""红薯条 - 新闻获取模块（使用 Tavily API）

获取红利指数相关新闻资讯
"""

import logging
import os
import json
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

# Tavily API
TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY', '')
TAVILY_API_URL = "https://api.tavily.com/search"

# 搜索关键词
SEARCH_KEYWORDS = [
    "红利指数 投资",
    "红利低波 ETF",
    "高股息 策略",
    "股息率 投资",
]


class TavilyNewsFetcher:
    """使用 Tavily API 获取新闻"""

    def __init__(self):
        self.cache_file = os.path.join(DATA_DIR, "news_cache.json")
        self.cache_duration = timedelta(hours=6)  # 缓存6小时

    def fetch_news(self, max_results: int = 5) -> List[Dict[str, Any]]:
        """获取红利相关新闻

        Args:
            max_results: 最大返回数量

        Returns:
            新闻列表，每条包含 title, url, summary, source, date
        """
        # 检查缓存
        cached = self._load_cache()
        if cached:
            logger.info(f"使用缓存的新闻数据（{len(cached)}条）")
            return cached[:max_results]

        if not TAVILY_API_KEY:
            logger.warning("未设置 TAVILY_API_KEY，跳过新闻获取")
            return []

        all_news = []

        for keyword in SEARCH_KEYWORDS[:2]:  # 只搜索前2个关键词
            try:
                news = self._search_tavily(keyword, max_results=3)
                all_news.extend(news)
            except Exception as e:
                logger.error(f"Tavily 搜索失败 ({keyword}): {e}")

        # 去重
        seen = set()
        unique_news = []
        for news in all_news:
            if news['title'] not in seen:
                seen.add(news['title'])
                unique_news.append(news)

        # 按相关性排序
        unique_news.sort(key=lambda x: x.get('score', 0), reverse=True)

        # 保存缓存
        if unique_news:
            self._save_cache(unique_news[:10])

        return unique_news[:max_results]

    def _search_tavily(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """调用 Tavily API 搜索"""
        payload = {
            "api_key": TAVILY_API_KEY,
            "query": query,
            "search_depth": "basic",
            "max_results": max_results,
            "include_domains": [
                "eastmoney.com",
                "finance.sina.com.cn",
                "cs.com.cn",
                "cnstock.com",
                "yicai.com",
                "caixin.com",
                "jiemian.com",
            ],
            "exclude_domains": [
                "toutiao.com",
                "baijiahao.baidu.com",
            ],
            "include_answer": False,
            "include_raw_content": False,
            "include_images": False,
            "topic": "news",
            "days": 3,  # 最近3天
        }

        response = requests.post(
            TAVILY_API_URL,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            logger.error(f"Tavily API 错误: {response.status_code} - {response.text}")
            return []

        data = response.json()
        results = data.get('results', [])

        news_list = []
        for item in results:
            news_list.append({
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'summary': item.get('content', '')[:200] if item.get('content') else '',
                'source': self._extract_source(item.get('url', '')),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'score': item.get('score', 0),
            })

        return news_list

    def _extract_source(self, url: str) -> str:
        """从 URL 提取来源名称"""
        domain_map = {
            'eastmoney.com': '东方财富',
            'finance.sina.com.cn': '新浪财经',
            'cs.com.cn': '中证网',
            'cnstock.com': '中国证券网',
            'yicai.com': '第一财经',
            'caixin.com': '财新网',
            'jiemian.com': '界面新闻',
        }

        for domain, name in domain_map.items():
            if domain in url:
                return name

        return '财经媒体'

    def _load_cache(self) -> Optional[List[Dict[str, Any]]]:
        """加载缓存的新闻"""
        if not os.path.exists(self.cache_file):
            return None

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 检查缓存是否过期
            cache_time = datetime.strptime(
                f"{data.get('date', '2000-01-01')} {data.get('fetch_time', '00:00:00')}",
                '%Y-%m-%d %H:%M:%S'
            )

            if datetime.now() - cache_time > self.cache_duration:
                logger.info("新闻缓存已过期")
                return None

            return data.get('news', [])
        except Exception as e:
            logger.warning(f"加载新闻缓存失败: {e}")
            return None

    def _save_cache(self, news: List[Dict[str, Any]]):
        """保存新闻缓存"""
        now = datetime.now()
        data = {
            'date': now.strftime('%Y-%m-%d'),
            'fetch_time': now.strftime('%H:%M:%S'),
            'source': 'tavily',
            'news': news,
        }

        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        logger.info(f"新闻缓存已保存（{len(news)}条）")


def fetch_dividend_news(max_results: int = 5) -> List[Dict[str, Any]]:
    """获取红利相关新闻的便捷函数"""
    fetcher = TavilyNewsFetcher()
    return fetcher.fetch_news(max_results)


if __name__ == '__main__':
    # 测试
    logging.basicConfig(level=logging.INFO)
    news = fetch_dividend_news()
    print(f"\n获取到 {len(news)} 条新闻:")
    for i, n in enumerate(news, 1):
        print(f"\n{i}. {n['title']}")
        print(f"   来源: {n['source']} | 相关度: {n.get('score', 0):.2f}")
        print(f"   摘要: {n['summary'][:100]}...")