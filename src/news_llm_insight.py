#!/usr/bin/env python3
"""红薯条 - LLM 观点提炼模块

使用 DashScope API（Qwen/DeepSeek）从新闻中提炼有价值的市场观点
"""

import json
import logging
import os
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

# DashScope API 配置（OpenAI 兼容模式）
DASHSCOPE_API_KEY = os.environ.get('DASHSCOPE_API_KEY', '')
DASHSCOPE_BASE_URL = os.environ.get('DASHSCOPE_BASE_URL', 'https://coding.dashscope.aliyuncs.com/v1')

# 使用 Qwen3.5 Plus 模型（性价比高）
MODEL_NAME = "qwen3.5-plus"


class LLMInsightExtractor:
    """使用 LLM 提炼新闻观点"""

    def __init__(self):
        self.cache_file = os.path.join(DATA_DIR, 'llm_insight.json')

    def extract_insights(
        self,
        news_list: List[Dict[str, Any]],
        dividend_data: Dict[str, Any] = None,
        max_insights: int = 3
    ) -> List[Dict[str, Any]]:
        """使用 LLM 从新闻中提炼观点

        Args:
            news_list: 新闻列表
            dividend_data: 股息率数据（可选）
            max_insights: 最大观点数量

        Returns:
            观点列表
        """
        if not DASHSCOPE_API_KEY:
            logger.warning("未设置 DASHSCOPE_API_KEY，使用规则提取")
            return self._fallback_extract(news_list, max_insights)

        if not news_list:
            return []

        # 构建提示词
        prompt = self._build_prompt(news_list, dividend_data)

        # 调用 LLM
        try:
            response = self._call_llm(prompt)
            insights = self._parse_response(response)
            
            # 缓存结果
            self._save_cache(insights)
            
            return insights[:max_insights]
        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            return self._fallback_extract(news_list, max_insights)

    def _build_prompt(self, news_list: List[Dict], dividend_data: Dict = None) -> str:
        """构建提示词"""
        # 新闻摘要
        news_text = ""
        for i, news in enumerate(news_list[:5], 1):
            title = news.get('title', '')
            summary = news.get('summary', '')[:150]
            source = news.get('source', '')
            news_text += f"{i}. 【{source}】{title}\n   摘要：{summary}\n\n"

        # 股息率数据（如果有）
        dividend_text = ""
        if dividend_data:
            avg_yield = dividend_data.get('avg_yield', '4.8%')
            avg_percentile = dividend_data.get('avg_percentile', '63%')
            best = dividend_data.get('best_yield', {})
            dividend_text = f"""
当前红利指数数据：
- 平均股息率：{avg_yield}
- 平均分位数：{avg_percentile}
- 最高股息率指数：{best.get('name', '沪港深红利低波')} ({best.get('yield', '5.47')}%)
"""

        # 使用普通字符串拼接，避免 f-string 格式化问题
        prompt = """你是一位红利投资分析师。请从以下新闻中提炼3条有价值的市场观点，用于日报推送。

要求：
1. 每条观点要简洁有力（不超过30字）
2. 观点要有实际投资参考价值，不要泛泛而谈
3. 使用专业但易懂的表达
4. 格式：emoji + 观点内容（如：📈 红利ETF资金流入增加）

""" + dividend_text + """

近期新闻：
""" + news_text + """

请输出JSON格式（每条观点不超过30字）：
```json
[
  {"insight": "观点内容", "type": "positive/neutral/negative", "source": "来源媒体"}
]
```
"""
        return prompt

    def _call_llm(self, prompt: str) -> str:
        """调用 DashScope API"""
        headers = {
            "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,  # 低温度，更稳定
            "max_tokens": 500,
        }

        response = requests.post(
            f"{DASHSCOPE_BASE_URL}/chat/completions",
            headers=headers,
            json=payload,
            timeout=60  # 增加超时时间
        )

        if response.status_code != 200:
            logger.error(f"API 错误: {response.status_code} - {response.text}")
            raise Exception(f"API 调用失败: {response.status_code}")

        data = response.json()
        content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
        
        logger.info(f"LLM 响应: {content[:100]}...")
        return content

    def _parse_response(self, response: str) -> List[Dict]:
        """解析 LLM 响应"""
        # 尝试提取 JSON
        try:
            # 清理响应（可能包含 markdown 代码块）
            if '```json' in response:
                response = response.split('```json')[1].split('```')[0]
            elif '```' in response:
                response = response.split('```')[1].split('```')[0]
            
            insights = json.loads(response.strip())
            
            # 验证格式
            for insight in insights:
                if 'insight' not in insight:
                    insight['insight'] = '📰 市场动态值得关注'
                if 'type' not in insight:
                    insight['type'] = 'neutral'
                if 'source' not in insight:
                    insight['source'] = ''
            
            return insights
        except json.JSONDecodeError:
            logger.warning(f"JSON 解析失败，尝试文本提取")
            # 从文本中提取观点
            lines = response.strip().split('\n')
            insights = []
            for line in lines:
                if any(emoji in line for emoji in ['📈', '📉', '💰', '🛡️', '📊', '⚠️', '✅']):
                    insights.append({
                        'insight': line.strip(),
                        'type': 'neutral',
                        'source': ''
                    })
            return insights[:3]

    def _fallback_extract(self, news_list: List[Dict], max_insights: int) -> List[Dict]:
        """规则提取（备用方案）"""
        import re
        
        insights = []
        rules = [
            (r'涨[0-9.]+%', '📈 红利ETF表现活跃，资金关注度提升', 'positive'),
            (r'份额增', '💰 红利ETF份额增加，资金持续流入', 'positive'),
            (r'份额减', '⚠️ 红利ETF份额缩减，注意资金流向', 'negative'),
            (r'防御', '🛡️ 红利资产防御属性凸显', 'positive'),
            (r'高股息', '📊 高股息策略持续受关注', 'positive'),
            (r'超额收益', '✅ 红利基金实现超额收益', 'positive'),
        ]
        
        seen = set()
        for news in news_list:
            content = news.get('title', '') + ' ' + news.get('summary', '')
            for pattern, insight, type_ in rules:
                if re.search(pattern, content) and insight not in seen:
                    insights.append({
                        'insight': insight,
                        'type': type_,
                        'source': news.get('source', '')
                    })
                    seen.add(insight)
                    if len(insights) >= max_insights:
                        break
            if len(insights) >= max_insights:
                break
        
        if not insights:
            insights.append({
                'insight': '📰 关注红利指数市场动态',
                'type': 'neutral',
                'source': ''
            })
        
        return insights

    def _save_cache(self, insights: List[Dict]):
        """缓存结果"""
        data = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'fetch_time': datetime.now().strftime('%H:%M:%S'),
            'insights': insights,
        }
        
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_cache(self) -> Optional[List[Dict]]:
        """加载缓存"""
        if not os.path.exists(self.cache_file):
            return None
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查是否今天的缓存
            if data.get('date') == datetime.now().strftime('%Y-%m-%d'):
                return data.get('insights', [])
        except:
            pass
        
        return None


def extract_insights_with_llm(
    news_list: List[Dict[str, Any]],
    dividend_data: Dict[str, Any] = None,
    max_insights: int = 3
) -> List[Dict[str, Any]]:
    """便捷函数"""
    extractor = LLMInsightExtractor()
    
    # 先检查缓存
    cached = extractor.load_cache()
    if cached:
        logger.info(f"使用缓存的 LLM 观点")
        return cached[:max_insights]
    
    return extractor.extract_insights(news_list, dividend_data, max_insights)


if __name__ == '__main__':
    # 测试
    import sys
    sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))
    from news_tavily import TavilyNewsFetcher

    logging.basicConfig(level=logging.INFO)

    # 获取新闻
    fetcher = TavilyNewsFetcher()
    news = fetcher.fetch_news(5)
    
    # 获取股息率数据
    try:
        with open(os.path.join(DATA_DIR, 'analysis_latest.json'), 'r') as f:
            dividend_data = json.load(f)
    except:
        dividend_data = None

    print(f"\n获取到 {len(news)} 条新闻")
    
    # 提炼观点
    print("\n" + "="*50)
    print("使用 LLM 提炼观点:")
    print("="*50)
    
    insights = extract_insights_with_llm(news, dividend_data)
    
    for i, insight in enumerate(insights, 1):
        print(f"\n{i}. {insight['insight']}")
        print(f"   类型: {insight['type']} | 来源: {insight.get('source', '')}")