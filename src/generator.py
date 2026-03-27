"""红薯条 - 内容生成模块

生成小红书内容和图片
"""

import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

logger = logging.getLogger(__name__)

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 输出目录
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')
ASSETS_DIR = os.path.join(PROJECT_ROOT, 'assets')


class ContentGenerator:
    """内容生成器"""

    def __init__(self):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(ASSETS_DIR, exist_ok=True)

    def generate_xiaohongshu_post(self, analysis_result: Dict[str, Any], 
                                   news: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """生成小红书帖子内容
        
        Args:
            analysis_result: 分析结果
            news: 相关新闻
            
        Returns:
            {
                'title': 标题,
                'content': 正文内容,
                'tags': 标签列表,
                'image_data': 图片数据
            }
        """
        date_str = datetime.now().strftime('%m月%d日')
        analyses = analysis_result.get('analysis', [])
        market_view = analysis_result.get('market_view', '')
        
        # 生成标题
        title = self._generate_title(analysis_result)
        
        # 生成正文
        content = self._generate_content(analysis_result, news)
        
        # 生成标签
        tags = [
            '#红利指数', '#红利低波', '#股息率', '#投资理财',
            '#稳健投资', '#被动收入', '#ETF投资', '#基金定投'
        ]
        
        return {
            'title': title,
            'content': content,
            'tags': tags,
            'date': datetime.now().strftime('%Y-%m-%d'),
            'time': datetime.now().strftime('%H:%M')
        }

    def _generate_title(self, analysis_result: Dict[str, Any]) -> str:
        """生成吸引人的标题"""
        best_yield = analysis_result.get('best_yield')
        best_opp = analysis_result.get('best_opportunity')
        date_str = datetime.now().strftime('%m月%d日')
        
        if best_yield and best_yield.get('yield'):
            yield_val = best_yield['yield']
            if yield_val >= 5.0:
                return f"🍠 {date_str}红利日报｜股息率突破{yield_val:.1f}%！"
            else:
                return f"🍠 {date_str}红利日报｜{best_yield['name']}领先"
        
        return f"🍠 {date_str}红利指数日报｜股息率监控"

    def _generate_content(self, analysis_result: Dict[str, Any], 
                          news: List[Dict[str, Any]] = None) -> str:
        """生成正文内容"""
        analyses = analysis_result.get('analysis', [])
        market_view = analysis_result.get('market_view', '')
        date_str = datetime.now().strftime('%Y年%m月%d日')
        
        lines = []
        
        # 开头
        lines.append(f"📅 {date_str} 红薯条红利日报")
        lines.append("")
        lines.append("大家好，我是红薯条🍠，每天早上准时带来红利指数股息率监控！")
        lines.append("")
        
        # 数据表格
        lines.append("📊 今日股息率数据：")
        lines.append("─" * 20)
        
        for a in analyses:
            yield_val = a.get('yield')
            percentile = a.get('percentile')
            name = a.get('name')
            
            yield_str = f"{yield_val:.2f}%" if yield_val else "N/A"
            perc_str = f"{percentile:.0f}%" if percentile else "N/A"
            
            # 添加表情
            if yield_val and yield_val >= 5.0:
                emoji = "🔥"
            elif percentile and percentile <= 20:
                emoji = "💎"
            elif percentile and percentile >= 80:
                emoji = "⚠️"
            else:
                emoji = "📈"
            
            lines.append(f"{emoji} {name}: {yield_str} (分位: {perc_str})")
        
        lines.append("─" * 20)
        lines.append("")
        
        # 市场观点
        lines.append("💡 今日观点：")
        lines.append(market_view)
        lines.append("")
        
        # 配置建议
        best_opp = analysis_result.get('best_opportunity')
        if best_opp:
            lines.append(f"📌 今日推荐关注：{best_opp['name']}")
            if best_opp.get('suggestion'):
                lines.append(best_opp['suggestion'])
            lines.append("")
        
        # 新闻摘要（如果有）
        if news and len(news) > 0:
            lines.append("📰 相关资讯：")
            for n in news[:3]:
                lines.append(f"• {n['title']}")
            lines.append("")
        
        # 持仓分享（可以后续添加真实数据）
        lines.append("💼 我的持仓分享：")
        lines.append("当前持有红利低波ETF，坚持定投中~")
        lines.append("（以上为个人操作分享，不构成投资建议）")
        lines.append("")
        
        # 免责声明
        lines.append("⚠️ 免责声明：")
        lines.append("本内容仅供参考，不构成投资建议。投资有风险，入市需谨慎。")
        
        return "\n".join(lines)

    def generate_image_data(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """生成图片数据（用于后续绑图）"""
        analyses = analysis_result.get('analysis', [])
        date_str = datetime.now().strftime('%Y年%m月%d日')
        
        # 准备图片数据
        image_data = {
            'date': date_str,
            'title': '红利指数股息率监控',
            'subtitle': '红薯条日报',
            'indices': []
        }
        
        for a in analyses:
            image_data['indices'].append({
                'name': a.get('name'),
                'code': a.get('code'),
                'yield': a.get('yield'),
                'percentile': a.get('percentile'),
                'pe': a.get('pe'),
                'level': a.get('level'),
                'opportunity': a.get('opportunity')
            })
        
        return image_data

    def save_content(self, post: Dict[str, Any], filename: str = None) -> str:
        """保存生成的内容"""
        if not filename:
            filename = f"post_{datetime.now().strftime('%Y%m%d')}.json"
        
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(post, f, ensure_ascii=False, indent=2)
        
        logger.info(f"内容已保存: {filepath}")
        return filepath

    def generate_push_message(self, post: Dict[str, Any]) -> str:
        """生成推送消息（用于钉钉等）"""
        lines = []
        lines.append("🍠 红薯条日报已生成")
        lines.append(f"📅 {post['date']} {post['time']}")
        lines.append("")
        lines.append(f"📝 标题：{post['title']}")
        lines.append("")
        lines.append("请复制以下内容发布到小红书：")
        lines.append("─" * 30)
        lines.append(post['content'])
        lines.append("─" * 30)
        lines.append("")
        lines.append(" ".join(post['tags']))
        
        return "\n".join(lines)


if __name__ == "__main__":
    # 测试内容生成
    logging.basicConfig(level=logging.INFO)
    
    generator = ContentGenerator()
    
    # 模拟分析结果
    test_analysis = {
        'analysis': [
            {'name': '红利低波', 'code': 'H30269', 'yield': 5.01, 'percentile': 95, 'pe': 8.07, 'level': 'very_high', 'opportunity': 'caution'},
            {'name': '红利低波100', 'code': '930955', 'yield': 4.88, 'percentile': 45, 'pe': 10.04, 'level': 'high', 'opportunity': 'neutral'},
        ],
        'market_view': '红利指数整体股息率处于较高水平，存在较好的配置机会。',
        'best_yield': {'name': '红利低波', 'yield': 5.01},
        'best_opportunity': {'name': '红利低波100', 'suggestion': '当前处于中等位置'}
    }
    
    post = generator.generate_xiaohongshu_post(test_analysis)
    
    print("="*50)
    print(post['title'])
    print("="*50)
    print(post['content'])
    print("="*50)
    print(" ".join(post['tags']))