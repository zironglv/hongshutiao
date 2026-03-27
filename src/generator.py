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
        """生成小红书帖子内容（优化版）
        
        优化要点：
        1. 标题轮换使用多种模板，包含吸引眼球的元素
        2. 内容结构：吸睛开头 → 核心数据 → 深度观点 → 操作建议 → 知识科普 → 互动引导
        3. 添加互动元素：评论区问题、点赞收藏引导
        
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
        weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        weekday = weekday_names[datetime.now().weekday()]
        analyses = analysis_result.get('analysis', [])
        market_view = analysis_result.get('market_view', '')
        
        # 计算平均分位数
        total_percentile = 0
        valid_count = 0
        for a in analyses:
            if a.get('percentile') is not None:
                total_percentile += a['percentile']
                valid_count += 1
        avg_percentile = total_percentile / valid_count if valid_count > 0 else 50
        
        # 计算最高股息率
        best_yield = analysis_result.get('best_yield', {})
        max_yield = best_yield.get('yield', 0) if best_yield else 0
        
        # 生成标题（轮换使用多种模板）
        title = self._generate_title_v2(date_str, avg_percentile, max_yield, best_yield)
        
        # 生成正文（优化结构）
        market_view = analysis_result.get('market_view', '')
        content = self._generate_content_v2(analysis_result, market_view, avg_percentile)
        
        # 生成标签
        tags = self._generate_tags()
        
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

    def _generate_title_v2(self, date_str: str, avg_percentile: float, max_yield: float, best_yield: Dict) -> str:
        """生成小红书标题（优化版，轮换多种模板）"""
        import random
        
        templates = [
            # 模板1：突出股息率数字
            lambda: f"🍠 {date_str}红利日报｜股息率突破{max_yield:.1f}%！",
            # 模板2：突出分位数
            lambda: f"🍠 定投必看｜红利指数分位数{avg_percentile:.0f}%，该加仓还是止盈？",
            # 模板3：投资日记风格
            lambda: f"🍠 红利投资日记｜{date_str}股息率出炉，新手定投指南",
            # 模板4：紧迫感风格
            lambda: f"🍠 紧急更新｜红利股息率{max_yield:.1f}%！这个信号要注意",
            # 模板5：数据盘点风格
            lambda: f"🍠 {date_str}红利盘点｜{len('indices')}大指数全复盘，建议收藏"
        ]
        
        # 基于日期选择模板（保证同一天标题一致）
        import hashlib
        idx = int(hashlib.md5(date_str.encode()).hexdigest(), 16) % len(templates)
        return templates[idx]()
    
    def _generate_content_v2(self, analysis_result: Dict[str, Any],
                             market_view: str, avg_percentile: float,
                             investment_advice: Dict = None, knowledge_tip: str = None) -> str:
        """生成小红书正文（优化版）"""
        analyses = analysis_result.get('analysis', [])
        date_str = datetime.now().strftime('%Y年%m月%d日')
        weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        weekday = weekday_names[datetime.now().weekday()]
        
        lines = []
        
        # 1. 吸睛开头
        if avg_percentile < 40:
            lines.append(f"🔥 {date_str} {weekday}｜红利指数进入低估区！")
            lines.append("姐妹们，今天的股息率数据很漂亮，可能是加仓的好时机！")
        elif avg_percentile > 70:
            lines.append(f"⚠️ {date_str} {weekday}｜红利指数估值偏高，注意风险！")
            lines.append("今天的股息率数据出来了，需要谨慎操作～")
        else:
            lines.append(f"📊 {date_str} {weekday}｜红利指数日报来了！")
            lines.append("每天早上一份，帮你把握红利投资节奏～")
        lines.append("")
        
        # 2. 核心数据
        lines.append("📊 **今日股息率数据**：")
        lines.append("─" * 16)
        for a in analyses:
            emoji = "🔥" if a.get('yield', 0) >= 5 else "📈" if a.get('percentile', 50) < 50 else "⚠️"
            lines.append(f"{emoji} {a['name']}: {a.get('yield', 0):.2f}% (分位: {a.get('percentile', 50):.0f}%)")
        lines.append("─" * 16)
        lines.append("")
        
        # 3. 深度观点
        lines.append("💡 **今日观点**：")
        lines.append(market_view if market_view else "红利指数整体股息率处于合理区间，坚持定投即可。")
        lines.append("")
        
        # 4. 操作建议
        lines.append("💰 **操作建议**：")
        if investment_advice:
            beginner = investment_advice.get('beginner', {})
            lines.append(f"• 新手：{beginner.get('action', '正常定投')} - {beginner.get('reason', '坚持定投')}")
        else:
            if avg_percentile < 40:
                lines.append("• 新手：加倍定投，把握低估值机会")
            elif avg_percentile > 70:
                lines.append("• 新手：减半定投或暂停观望")
            else:
                lines.append("• 新手：正常定投，不用择时")
        lines.append("")
        
        # 5. 知识科普
        if knowledge_tip:
            lines.append("📚 **今日知识点**：")
            lines.append(knowledge_tip[:100] + "..." if len(knowledge_tip) > 100 else knowledge_tip)
            lines.append("")
        
        # 6. 互动引导
        lines.append("💬 **互动话题**：")
        lines.append("你定投红利多久了？收益如何？评论区聊聊～")
        lines.append("")
        lines.append("📌 觉得有用请点赞收藏，每天早上准时更新！")
        lines.append("")
        lines.append("⚠️ 免责声明：以上内容仅供参考，不构成投资建议")
        
        return "\n".join(lines)
    
    def _generate_tags(self) -> List[str]:
        """生成小红书标签"""
        return [
            "#红利指数", "#红利低波", "#股息率", 
            "#投资理财", "#稳健投资", "#定投",
            "#ETF投资", "#基金定投", "#理财小白"
        ]

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

    def generate_daily_report(self, analysis_result: Dict[str, Any], 
                             market_trend: Dict[str, Any] = None,
                             investment_advice: Dict[str, Any] = None,
                             risk_tip: str = None,
                             knowledge_tip: str = None,
                             history_data: List[Dict] = None) -> str:
        """生成日报（按 DAILY_REPORT_TEMPLATE.md 结构）
        
        Args:
            analysis_result: 分析结果
            market_trend: 市场趋势数据（日环比、周环比等）
            investment_advice: 投资建议
            risk_tip: 风险提示
            knowledge_tip: 知识点
            history_data: 历史数据（用于计算平均股息率等）
            
        Returns:
            日报文本内容
        """
        analyses = analysis_result.get('analysis', [])
        date_str = datetime.now().strftime('%Y年%m月%d日')
        weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        weekday = weekday_names[datetime.now().weekday()]
        
        lines = []
        
        # 标题
        lines.append(f"# 📅 {date_str} {weekday} 红利指数日报")
        lines.append("")
        lines.append("> 红薯条每日监控，助力稳健投资")
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # ==================== 数据总览 ====================
        lines.append("## 📊 今日数据总览")
        lines.append("")
        lines.append("| 指数名称 | 代码 | TTM股息率 | 历史分位数 | 评级 |")
        lines.append("|----------|------|-----------|------------|------|")
        
        total_yield = 0
        total_percentile = 0
        valid_count = 0
        
        for a in analyses:
            name = a.get('name', 'N/A')
            code = a.get('code', 'N/A')
            yield_val = a.get('yield')
            percentile = a.get('percentile')
            
            # 格式化数据
            yield_str = f"{yield_val:.2f}%" if yield_val else "N/A"
            perc_str = f"{percentile:.0f}%" if percentile else "N/A"
            
            # 计算评级（星星）
            if percentile is not None:
                if percentile <= 30:
                    rating = "⭐⭐⭐⭐⭐"
                elif percentile <= 50:
                    rating = "⭐⭐⭐⭐"
                elif percentile <= 70:
                    rating = "⭐⭐⭐"
                else:
                    rating = "⭐⭐"
            else:
                rating = "N/A"
            
            lines.append(f"| {name} | {code} | {yield_str} | {perc_str} | {rating} |")
            
            # 累计统计
            if yield_val:
                total_yield += yield_val
                valid_count += 1
            if percentile:
                total_percentile += percentile
        
        lines.append("")
        
        # 平均值
        avg_yield = total_yield / valid_count if valid_count > 0 else 0
        avg_percentile = total_percentile / valid_count if valid_count > 0 else 0
        lines.append(f"**平均股息率**：{avg_yield:.2f}%")
        lines.append(f"**平均分位数**：{avg_percentile:.0f}%")
        lines.append("")
        
        # ==================== 市场解读 ====================
        lines.append("---")
        lines.append("")
        lines.append("## 📈 市场解读")
        lines.append("")
        
        # 整体观点
        lines.append("### 整体观点")
        market_view = analysis_result.get('market_view', '')
        lines.append(market_view if market_view else "当前红利指数整体表现稳定，建议持续关注。")
        lines.append("")
        
        # 趋势分析
        lines.append("### 趋势分析")
        if market_trend:
            daily_change = market_trend.get('daily_change', 0)
            weekly_change = market_trend.get('weekly_change', 0)
            trend_direction = market_trend.get('trend_direction', 'stable')
            trend_strength = market_trend.get('trend_strength', 'weak')
            
            # 日环比
            if daily_change > 0:
                daily_str = f"较上个交易日 **上升 {abs(daily_change):.1f} 个基点** 📈"
            elif daily_change < 0:
                daily_str = f"较上个交易日 **下降 {abs(daily_change):.1f} 个基点** 📉"
            else:
                daily_str = "与上个交易日 **持平** ➡️"
            
            # 周环比
            if weekly_change > 0:
                weekly_str = f"较上周同期 **上升 {abs(weekly_change):.1f} 个基点** 📈"
            elif weekly_change < 0:
                weekly_str = f"较上周同期 **下降 {abs(weekly_change):.1f} 个基点** 📉"
            else:
                weekly_str = "与上周同期 **持平** ➡️"
            
            lines.append(f"- **日环比变化**：{daily_str}")
            lines.append(f"- **周环比变化**：{weekly_str}")
            lines.append(f"- **分位数位置**：当前处于历史 **{avg_percentile:.0f}% 分位**，意味着历史上有 {avg_percentile:.0f}% 的时间股息率比现在低")
        else:
            lines.append("- **日环比变化**：暂无历史数据")
            lines.append("- **周环比变化**：暂无历史数据")
            lines.append(f"- **分位数位置**：当前处于历史 **{avg_percentile:.0f}% 分位**")
        lines.append("")
        
        # 主要解读
        lines.append("### 主要解读")
        if avg_percentile <= 30:
            lines.append("- 🔥 当前股息率处于历史低位区间，投资性价比较高")
            lines.append("- 💎 分位数较低意味着股息率较高，是较好的配置时机")
        elif avg_percentile <= 50:
            lines.append("- 📊 当前股息率处于合理区间，适合正常定投")
            lines.append("- 🔄 建议保持定投节奏，不必过于关注短期波动")
        elif avg_percentile <= 70:
            lines.append("- ⚠️ 当前股息率偏高，需注意控制仓位")
            lines.append("- 📉 建议减少定投金额或部分止盈")
        else:
            lines.append("- ⚠️ 当前股息率处于历史高位，谨慎投资")
            lines.append("- 🛑 建议暂停定投或考虑止盈")
        lines.append("")
        
        # ==================== 定投建议 ====================
        lines.append("---")
        lines.append("")
        lines.append("## 💰 定投建议")
        lines.append("")
        
        lines.append("### 🟢 新手投资者")
        lines.append("")
        lines.append("| 当前分位数 | 建议 | 理由 |")
        lines.append("|------------|------|------|")
        lines.append("| < 30% | **加倍定投** | 历史低位，性价比极高 |")
        lines.append("| 30-50% | **正常定投** | 处于合理区间，坚持定投 |")
        lines.append("| 50-70% | **减半定投** | 偏高位，控制节奏 |")
        lines.append("| > 70% | **暂停观望** | 历史高位，等待回调 |")
        lines.append("")
        
        # 今日建议
        if investment_advice and 'beginner' in investment_advice:
            beginner_advice = investment_advice['beginner']
            lines.append(f"**今日建议**：**{beginner_advice['action']}** - {beginner_advice['reason']}")
        else:
            if avg_percentile <= 30:
                lines.append("**今日建议**：**加倍定投** - 历史低位，性价比极高")
            elif avg_percentile <= 50:
                lines.append("**今日建议**：**正常定投** - 处于合理区间，坚持定投")
            elif avg_percentile <= 70:
                lines.append("**今日建议**：**减半定投** - 偏高位，控制节奏")
            else:
                lines.append("**今日建议**：**暂停观望** - 历史高位，等待回调")
        lines.append("")
        
        lines.append("### 🟡 定投中的朋友")
        lines.append("")
        lines.append("| 场景 | 建议 |")
        lines.append("|------|------|")
        lines.append("| 已定投 < 6个月 | 继续坚持，不用在意短期波动 |")
        lines.append("| 已定投 6-12个月 | 关注分位数变化，适时调整 |")
        lines.append("| 已定投 > 1年 | 考虑部分止盈，锁定收益 |")
        lines.append("")
        
        if investment_advice and 'ongoing' in investment_advice:
            ongoing_advice = investment_advice['ongoing']
            lines.append(f"**当前建议**：{ongoing_advice['action']} - {ongoing_advice['reason']}")
        lines.append("")
        
        # 止盈策略
        lines.append("### 🔴 止盈策略")
        lines.append("")
        if investment_advice and 'stop_profit' in investment_advice:
            lines.append(investment_advice['stop_profit'])
        else:
            lines.append("当分位数超过80%时，考虑分批止盈30%-50%。")
        lines.append("")
        
        # ==================== 风险提示 ====================
        lines.append("---")
        lines.append("")
        lines.append("## ⚠️ 风险提示")
        lines.append("")
        if risk_tip:
            lines.append(risk_tip)
        else:
            lines.append("投资有风险，入市需谨慎。本日报仅供参考，不构成投资建议。")
        lines.append("")
        
        # ==================== 知识点 ====================
        lines.append("---")
        lines.append("")
        lines.append("## 📚 今日知识点")
        lines.append("")
        if knowledge_tip:
            lines.append(knowledge_tip)
        else:
            lines.append("股息率 = 年度分红 / 股价 × 100%。股息率越高，投资回报越好。")
        lines.append("")
        
        # ==================== 免责声明 ====================
        lines.append("---")
        lines.append("")
        lines.append("## 📝 免责声明")
        lines.append("")
        lines.append("本日报内容仅供参考，不构成任何投资建议。")
        lines.append("投资有风险，入市需谨慎。请根据自身情况做出投资决策。")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("*📊 数据来源：指数公司官方披露 *")
        lines.append("*🍠 红薯条 - 让红利投资更简单 *")
        
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