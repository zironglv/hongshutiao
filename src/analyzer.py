"""红薯条 - 数据分析模块

分析股息率数据，生成投资观点
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class DividendAnalyzer:
    """股息率分析器"""

    # 股息率评估标准
    YIELD_LEVELS = {
        'very_high': 5.0,    # 股息率 >= 5% 视为非常高
        'high': 4.5,         # 股息率 >= 4.5% 视为较高
        'medium': 4.0,       # 股息率 >= 4% 视为中等
        'low': 3.5,          # 股息率 < 3.5% 视为较低
    }

    # 分位数评估标准
    PERCENTILE_LEVELS = {
        'very_low': 20,      # 分位数 < 20% 视为历史低位
        'low': 40,           # 分位数 < 40% 视为偏低
        'high': 60,          # 分位数 > 60% 视为偏高
        'very_high': 80,     # 分位数 > 80% 视为历史高位
    }

    def analyze_single(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """分析单个指数
        
        Args:
            data: 指数数据（包含股息率、分位数等）
            
        Returns:
            分析结果
        """
        result = {
            'code': data.get('code'),
            'name': data.get('name'),
            'yield': data.get('dividend_yield_2'),
            'pe': data.get('pe_2'),
            'percentile': data.get('dividend_yield_percentile'),
            'level': None,
            'opportunity': None,
            'suggestion': None,
            'reasons': []
        }
        
        yield_val = data.get('dividend_yield_2')
        percentile = data.get('dividend_yield_percentile')
        
        if yield_val is None:
            result['level'] = 'unknown'
            result['suggestion'] = '数据不足，无法分析'
            return result
        
        # 评估股息率水平
        if yield_val >= self.YIELD_LEVELS['very_high']:
            result['level'] = 'very_high'
            result['reasons'].append(f"股息率 {yield_val:.2f}% 处于较高水平（>5%）")
        elif yield_val >= self.YIELD_LEVELS['high']:
            result['level'] = 'high'
            result['reasons'].append(f"股息率 {yield_val:.2f}% 处于较高水平")
        elif yield_val >= self.YIELD_LEVELS['medium']:
            result['level'] = 'medium'
            result['reasons'].append(f"股息率 {yield_val:.2f}% 处于中等水平")
        else:
            result['level'] = 'low'
            result['reasons'].append(f"股息率 {yield_val:.2f}% 处于较低水平")
        
        # 评估分位数（如果有）
        if percentile is not None:
            if percentile <= self.PERCENTILE_LEVELS['very_low']:
                result['opportunity'] = 'good'
                result['reasons'].append(f"历史分位数 {percentile:.1f}%，处于历史低位，配置机会较好")
            elif percentile <= self.PERCENTILE_LEVELS['low']:
                result['opportunity'] = 'fair'
                result['reasons'].append(f"历史分位数 {percentile:.1f}%，处于偏低位置")
            elif percentile >= self.PERCENTILE_LEVELS['very_high']:
                result['opportunity'] = 'caution'
                result['reasons'].append(f"历史分位数 {percentile:.1f}%，处于历史高位，注意风险")
            elif percentile >= self.PERCENTILE_LEVELS['high']:
                result['opportunity'] = 'wait'
                result['reasons'].append(f"历史分位数 {percentile:.1f}%，处于偏高位置，可观望")
            else:
                result['opportunity'] = 'neutral'
                result['reasons'].append(f"历史分位数 {percentile:.1f}%，处于中间位置")
        
        # 生成建议
        result['suggestion'] = self._generate_suggestion(result)
        
        return result

    def _generate_suggestion(self, analysis: Dict[str, Any]) -> str:
        """生成投资建议"""
        level = analysis.get('level')
        opportunity = analysis.get('opportunity')
        name = analysis.get('name', '该指数')
        
        if opportunity == 'good':
            return f"💎 {name}当前股息率处于历史低位，是不错的配置时机，建议关注。"
        elif opportunity == 'caution':
            return f"⚠️ {name}当前股息率处于历史高位，虽然收益可观，但需注意回调风险。"
        elif opportunity == 'wait':
            return f"👀 {name}当前股息率偏高，建议观望，等待更好时机。"
        elif opportunity == 'fair':
            return f"📊 {name}当前股息率处于偏低位置，可以考虑逢低布局。"
        elif level == 'very_high':
            return f"💰 {name}股息率超过5%，具有较好的配置价值。"
        elif level == 'high':
            return f"📈 {name}股息率较高，值得关注。"
        else:
            return f"📌 {name}股息率适中，可按需配置。"

    def analyze_all(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析所有指数
        
        Returns:
            {
                'date': 日期,
                'summary': 整体摘要,
                'best_opportunity': 最佳机会,
                'analysis': 各指数分析结果,
                'market_view': 市场观点
            }
        """
        analyses = []
        best_yield = None
        best_opportunity = None
        
        for data in data_list:
            analysis = self.analyze_single(data)
            analyses.append(analysis)
            
            # 找出最高股息率
            if best_yield is None or (analysis.get('yield') and analysis.get('yield') > best_yield.get('yield', 0)):
                best_yield = analysis
            
            # 找出最佳配置机会
            if analysis.get('opportunity') == 'good':
                if best_opportunity is None or (analysis.get('percentile') and 
                    analysis.get('percentile') < best_opportunity.get('percentile', 100)):
                    best_opportunity = analysis
        
        # 生成市场整体观点
        market_view = self._generate_market_view(analyses)
        
        # 生成摘要
        summary = self._generate_summary(analyses, best_yield, best_opportunity)
        
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'summary': summary,
            'best_yield': best_yield,
            'best_opportunity': best_opportunity,
            'analysis': analyses,
            'market_view': market_view
        }

    def _generate_market_view(self, analyses: List[Dict[str, Any]]) -> str:
        """生成市场整体观点"""
        # 统计各水平数量
        level_counts = {'very_high': 0, 'high': 0, 'medium': 0, 'low': 0, 'unknown': 0}
        opp_counts = {'good': 0, 'fair': 0, 'neutral': 0, 'wait': 0, 'caution': 0}
        
        for a in analyses:
            if a.get('level'):
                level_counts[a['level']] = level_counts.get(a['level'], 0) + 1
            if a.get('opportunity'):
                opp_counts[a['opportunity']] = opp_counts.get(a['opportunity'], 0) + 1
        
        # 生成观点
        total = len(analyses)
        high_yield_count = level_counts['very_high'] + level_counts['high']
        good_opportunity_count = opp_counts['good'] + opp_counts['fair']
        
        view_parts = []
        
        if high_yield_count >= total * 0.6:
            view_parts.append("红利指数整体股息率处于较高水平")
        elif high_yield_count <= total * 0.3:
            view_parts.append("红利指数整体股息率偏低")
        else:
            view_parts.append("红利指数股息率分化明显")
        
        if good_opportunity_count >= 2:
            view_parts.append("存在较好的配置机会")
        elif opp_counts['caution'] >= 2:
            view_parts.append("部分指数需注意风险")
        
        return "，".join(view_parts) + "。"

    def _generate_summary(self, analyses: List[Dict], best_yield: Dict, best_opp: Dict) -> str:
        """生成每日摘要"""
        date_str = datetime.now().strftime('%Y年%m月%d日')
        
        summary_parts = [f"📅 {date_str} 红利指数日报\n"]
        
        # 最高股息率
        if best_yield and best_yield.get('yield'):
            summary_parts.append(f"📊 最高股息率：{best_yield['name']} ({best_yield['yield']:.2f}%)")
        
        # 最佳机会
        if best_opp:
            summary_parts.append(f"💎 最佳配置：{best_opp['name']} (分位数 {best_opp.get('percentile', 'N/A')}%)")
        
        return "\n".join(summary_parts)

    def analyze_market_trend(self, history_data: List[Dict]) -> Dict:
        """分析市场趋势
        
        Args:
            history_data: 历史数据列表，按日期倒序排列（最新在前）
            
        Returns:
            {
                'daily_change': 日环比变化(基点),
                'weekly_change': 周环比变化(基点),
                'trend_direction': 'up' | 'down' | 'stable',
                'trend_strength': 'strong' | 'moderate' | 'weak'
            }
        """
        result = {
            'daily_change': 0,
            'weekly_change': 0,
            'trend_direction': 'stable',
            'trend_strength': 'weak'
        }
        
        if not history_data or len(history_data) < 2:
            return result
        
        # 计算日环比（最新 vs 上一交易日）
        current_yield = history_data[0].get('avg_yield')
        prev_yield = history_data[1].get('avg_yield') if len(history_data) > 1 else None
        
        if current_yield is not None and prev_yield is not None:
            # 基点 = 百分比差值 * 100
            result['daily_change'] = round((current_yield - prev_yield) * 100, 2)
        
        # 计算周环比（最新 vs 5个交易日前）
        if len(history_data) >= 6:
            week_ago_yield = history_data[5].get('avg_yield')
            if current_yield is not None and week_ago_yield is not None:
                result['weekly_change'] = round((current_yield - week_ago_yield) * 100, 2)
        
        # 判断趋势方向
        if result['daily_change'] > 5:
            result['trend_direction'] = 'up'
            result['trend_strength'] = 'strong'
        elif result['daily_change'] > 2:
            result['trend_direction'] = 'up'
            result['trend_strength'] = 'moderate'
        elif result['daily_change'] < -5:
            result['trend_direction'] = 'down'
            result['trend_strength'] = 'strong'
        elif result['daily_change'] < -2:
            result['trend_direction'] = 'down'
            result['trend_strength'] = 'moderate'
        else:
            result['trend_direction'] = 'stable'
            result['trend_strength'] = 'weak'
        
        return result

    def generate_investment_advice(self, percentile: float, yield_rate: float = None) -> Dict:
        """生成投资建议
        
        Args:
            percentile: 当前分位数
            yield_rate: 当前股息率（可选）
            
        Returns:
            {
                'beginner': {'action': 动作, 'reason': 理由},
                'ongoing': {'action': 动作, 'reason': 理由},
                'stop_profit': 止盈建议
            }
        """
        result = {
            'beginner': {'action': '正常定投', 'reason': '保持定投节奏'},
            'ongoing': {'action': '继续持有', 'reason': '坚持定投计划'},
            'stop_profit': None
        }
        
        if percentile < 20:
            result['beginner'] = {
                'action': '加倍定投',
                'reason': '历史极低位，性价比极高，是黄金配置窗口'
            }
            result['ongoing'] = {
                'action': '加仓定投',
                'reason': '处于历史低位，可适当加大投入'
            }
            result['stop_profit'] = '暂不止盈，低位积累筹码为主'
        elif percentile < 30:
            result['beginner'] = {
                'action': '加倍定投',
                'reason': '历史低位，性价比极高'
            }
            result['ongoing'] = {
                'action': '加大定投',
                'reason': '分位数较低，可适当增加定投金额'
            }
            result['stop_profit'] = '低位区域继续积累'
        elif percentile < 50:
            result['beginner'] = {
                'action': '正常定投',
                'reason': '处于合理估值区间，坚持定投'
            }
            result['ongoing'] = {
                'action': '正常定投',
                'reason': '继续按计划执行'
            }
            result['stop_profit'] = '正常持有，等待更高分位数'
        elif percentile < 60:
            result['beginner'] = {
                'action': '减半定投',
                'reason': '估值偏高，控制投入节奏'
            }
            result['ongoing'] = {
                'action': '维持定投',
                'reason': '可继续定投但需关注止盈'
            }
            result['stop_profit'] = '考虑部分止盈，锁定收益'
        elif percentile < 70:
            result['beginner'] = {
                'action': '减半定投',
                'reason': '估值偏高，谨慎入场'
            }
            result['ongoing'] = {
                'action': '减半定投',
                'reason': '分位数偏高，降低投入'
            }
            result['stop_profit'] = '建议部分止盈（30%-50%）'
        else:
            result['beginner'] = {
                'action': '暂停观望',
                'reason': '历史高位，等待回调后再入场'
            }
            result['ongoing'] = {
                'action': '暂停定投',
                'reason': '高位区域，等待更好时机'
            }
            result['stop_profit'] = '建议止盈（50%-70%），锁定收益'
        
        # 如果有股息率信息，补充到理由中
        if yield_rate:
            if yield_rate >= 5.0:
                result['beginner']['reason'] += f'，当前股息率{yield_rate:.2f}%较优'
        
        return result

    def get_risk_tip(self, day_of_week: int = None) -> str:
        """获取风险提示
        
        Args:
            day_of_week: 星期几 (0=周一, 6=周日)，默认自动获取
            
        Returns:
            风险提示文本
        """
        if day_of_week is None:
            day_of_week = datetime.now().weekday()
        
        risk_tips = {
            0: "⚠️ 周一开盘可能受周末消息面影响，注意开盘波动。红利低波指数虽有防御属性，但仍需关注市场整体情绪。",
            1: "⚠️ 定投需坚持长期主义，不要因短期波动频繁调整策略。历史数据显示，坚持3年以上定投胜率显著提升。",
            2: "⚠️ 关注市场成交量变化，量价配合才是健康走势。若量能不足，反弹持续性存疑。",
            3: "⚠️ 分散投资是降低风险的有效手段。红利低波指数适合作为底仓配置，但不宜全仓押注单一品种。",
            4: "⚠️ 周五收盘前注意周末可能的政策消息。若本周涨幅较大，可考虑部分获利了结。",
            5: "📅 周末休市，是复盘和学习的最佳时机。建议回顾本周持仓表现，调整下周投资计划。",
            6: "📅 周末休市，可以阅读红利投资相关书籍，提升投资认知。记住：认知变现才是投资的根本。"
        }
        
        return risk_tips.get(day_of_week, risk_tips[0])

    def get_knowledge_tip(self, day_of_week: int = None) -> str:
        """获取知识点
        
        Args:
            day_of_week: 星期几 (0=周一, 6=周日)，默认自动获取
            
        Returns:
            知识点文本
        """
        if day_of_week is None:
            day_of_week = datetime.now().weekday()
        
        knowledge_tips = {
            0: "📚 **什么是股息率分位数？**\n股息率分位数表示当前股息率在历史数据中的相对位置。例如分位数30%，意味着历史上有30%的时间股息率比现在低。分位数越低，代表当前股息率越高，投资价值越好。",
            1: "📚 **红利低波指数的选股逻辑是什么？**\n红利低波指数通常选取股息率高、波动率低的股票，兼顾收益和防御。选股标准包括：股息率排名、波动率筛选、流动性筛选等。这类指数适合追求稳定收益的投资者。",
            2: "📚 **为什么分位数低反而好？**\n分位数低意味着当前股息率处于历史高位。股息率 = 股息 / 股价，股息率上升通常是因为股价下跌。所以在低位买入，既能享受较高股息率，又有股价修复空间，双重收益机会。",
            3: "📚 **定投红利指数的最佳周期是多久？**\n建议定投周期至少3-5年。红利指数的特点是稳健分红，短期内可能跑不赢成长风格，但拉长时间看，复利效应明显。历史回测显示，坚持5年定投红利指数，收益稳定性和胜率都较高。",
            4: "📚 **红利指数和债券有什么区别？**\n红利指数投资股票，有股价波动风险，但长期收益潜力更大。债券收益固定但有限。红利指数适合能承受一定波动的投资者，作为'类固收+'配置，追求比债券更高的收益。",
            5: "📚 **什么是TTM股息率？**\nTTM (Trailing Twelve Months) 股息率 = 过去12个月分红总额 / 当前股价。相比静态股息率，TTM更能反映最近一年的实际分红情况，是评估红利投资价值的重要指标。",
            6: "📚 **红利投资的止盈策略**\n建议设置分位数止盈点：当股息率分位数超过80%（即股息率处于历史低位），可考虑分批止盈。止盈不是全仓卖出，而是部分获利了结，保留底仓继续享受分红。"
        }
        
        return knowledge_tips.get(day_of_week, knowledge_tips[0])


if __name__ == "__main__":
    # 测试分析器
    logging.basicConfig(level=logging.INFO)
    
    analyzer = DividendAnalyzer()
    
    # 模拟测试数据
    test_data = [
        {
            'code': 'H30269',
            'name': '红利低波',
            'dividend_yield_2': 5.01,
            'pe_2': 8.07,
            'dividend_yield_percentile': 95
        },
        {
            'code': '930955',
            'name': '红利低波100',
            'dividend_yield_2': 4.88,
            'pe_2': 10.04,
            'dividend_yield_percentile': 45
        }
    ]
    
    result = analyzer.analyze_all(test_data)
    print(result['summary'])
    print("\n市场观点:", result['market_view'])
    
    for a in result['analysis']:
        print(f"\n{a['name']}:")
        print(f"  水平: {a['level']}")
        print(f"  建议: {a['suggestion']}")