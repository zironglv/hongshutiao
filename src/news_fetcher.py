"""红薯条 - 新闻获取模块

使用浏览器获取红利指数相关新闻
"""

import logging
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import os

logger = logging.getLogger(__name__)

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据存储目录
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')


class NewsFetcher:
    """新闻获取器"""

    def __init__(self):
        self.news_cache_file = os.path.join(DATA_DIR, "news_cache.json")
        self._browser_started = False

    def fetch_from_eastmoney(self, keywords: List[str] = None) -> List[Dict[str, Any]]:
        """从东方财富获取红利相关新闻
        
        Args:
            keywords: 搜索关键词列表
            
        Returns:
            新闻列表
        """
        if keywords is None:
            keywords = ["红利指数", "红利低波", "高股息"]
        
        news_list = []
        
        try:
            from playwright.sync_api import sync_playwright
            
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                for keyword in keywords:
                    try:
                        # 东方财富搜索
                        search_url = f"https://so.eastmoney.com/news/s?keyword={keyword}"
                        logger.info(f"搜索新闻: {keyword}")
                        
                        page.goto(search_url, timeout=30000)
                        page.wait_for_timeout(2000)
                        
                        # 获取搜索结果
                        items = page.query_selector_all('.news-item')
                        
                        for item in items[:5]:  # 只取前5条
                            try:
                                title_el = item.query_selector('.title a')
                                time_el = item.query_selector('.time')
                                
                                if title_el:
                                    title = title_el.inner_text().strip()
                                    link = title_el.get_attribute('href')
                                    news_time = time_el.inner_text().strip() if time_el else ""
                                    
                                    # 过滤今天和昨天的新闻
                                    if self._is_recent_news(news_time):
                                        news_list.append({
                                            'title': title,
                                            'link': link,
                                            'time': news_time,
                                            'keyword': keyword,
                                            'source': '东方财富'
                                        })
                            except Exception as e:
                                logger.debug(f"解析新闻项失败: {e}")
                                continue
                        
                        page.wait_for_timeout(1000)
                        
                    except Exception as e:
                        logger.warning(f"搜索 {keyword} 失败: {e}")
                        continue
                
                browser.close()
        
        except ImportError:
            logger.warning("未安装 playwright，尝试使用备选方案")
            return self._fetch_from_sina(keywords)
        except Exception as e:
            logger.error(f"获取新闻失败: {e}")
            return self._fetch_from_sina(keywords)
        
        # 去重
        seen = set()
        unique_news = []
        for news in news_list:
            if news['title'] not in seen:
                seen.add(news['title'])
                unique_news.append(news)
        
        logger.info(f"获取到 {len(unique_news)} 条新闻")
        return unique_news[:10]  # 最多返回10条

    def _fetch_from_sina(self, keywords: List[str]) -> List[Dict[str, Any]]:
        """从新浪财经获取新闻（备选方案）"""
        import requests
        
        news_list = []
        
        try:
            # 新浪财经 API
            url = "https://finance.sina.com.cn/7x24/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            # 简单解析，这里可以后续优化
            logger.info("尝试从新浪获取新闻")
            
        except Exception as e:
            logger.warning(f"新浪财经获取失败: {e}")
        
        return news_list

    def _is_recent_news(self, news_time: str) -> bool:
        """判断新闻是否是最近的（今天或昨天）"""
        today = datetime.now().strftime('%m-%d')
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%m-%d')
        
        # 东方财富的时间格式通常是 "MM-DD HH:MM"
        if today in news_time or yesterday in news_time:
            return True
        
        # 或者包含"今天"、"昨天"等关键词
        if any(k in news_time for k in ['今天', '昨天', '刚刚', '小时前']):
            return True
        
        return False

    def fetch_finance_news(self) -> List[Dict[str, Any]]:
        """获取财经新闻（综合多个来源）"""
        logger.info("开始获取财经新闻...")
        
        # 主要从东方财富获取
        news = self.fetch_from_eastmoney()
        
        # 缓存新闻
        self._cache_news(news)
        
        return news

    def _cache_news(self, news: List[Dict[str, Any]]):
        """缓存新闻数据"""
        os.makedirs(DATA_DIR, exist_ok=True)
        
        cache_data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'fetch_time': datetime.now().strftime('%H:%M:%S'),
            'news': news
        }
        
        with open(self.news_cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"新闻已缓存到: {self.news_cache_file}")

    def get_cached_news(self) -> List[Dict[str, Any]]:
        """获取缓存的新闻"""
        if os.path.exists(self.news_cache_file):
            with open(self.news_cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 检查是否是今天的缓存
                if data.get('date') == datetime.now().strftime('%Y-%m-%d'):
                    return data.get('news', [])
        
        return []


if __name__ == "__main__":
    # 测试新闻获取
    logging.basicConfig(level=logging.INFO)
    
    fetcher = NewsFetcher()
    news = fetcher.fetch_finance_news()
    
    print("\n获取到的新闻:")
    for i, n in enumerate(news, 1):
        print(f"\n{i}. {n['title']}")
        print(f"   时间: {n['time']}")
        print(f"   来源: {n['source']}")