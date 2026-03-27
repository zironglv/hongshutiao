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