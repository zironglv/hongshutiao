# 代码修改指南

## analyzer.py 需要添加的方法

```python
class DividendAnalyzer:

    def analyze_market_trend(self, history_data: List[Dict]) -> Dict:
        """分析市场趋势
        
        Returns:
            {
                'daily_change': 日环比变化(基点),
                'weekly_change': 周环比变化(基点),
                'trend_direction': 'up' | 'down' | 'stable',
                'trend_strength': 'strong' | 'moderate' | 'weak'
            }
        """
        pass

    def analyze_cross_index(self, current_data: List[Dict]) -> Dict:
        """跨指数对比分析
        
        Returns:
            {
                'best_value': {'name': xxx, 'yield': xxx, 'percentile': xxx},
                'worst_value': {...},
                'spread': 最高最低差值,
                'correlation': 相关性分析
            }
        """
        pass

    def generate_investment_advice(self, percentile: float, yield_rate: float) -> Dict:
        """生成投资建议
        
        Returns:
            {
                'beginner': {'action': '加倍/正常/减半/暂停', 'reason': '...'},
                'holder': {'action': '加仓/持有/止盈', 'reason': '...'},
                'signal': 'buy' | 'hold' | 'sell'
            }
        """
        # 分位数逻辑
        if percentile < 30:
            return {
                'beginner': {'action': '加倍定投', 'reason': '历史低位，性价比极高'},
                'holder': {'action': '加仓', 'reason': '股息率高于历史70%的时间'},
                'signal': 'buy'
            }
        elif percentile < 50:
            return {
                'beginner': {'action': '正常定投', 'reason': '处于合理区间'},
                'holder': {'action': '持有', 'reason': '继续定投即可'},
                'signal': 'hold'
            }
        # ... 以此类推

    def get_risk_alert(self, day_of_week: int) -> str:
        """获取风险提示"""
        alerts = {
            0: "红利指数虽然波动较小，但仍有下跌风险...",
            1: "股息率高的股票可能面临分红减少的风险...",
            # ...
        }
        return alerts.get(day_of_week, "投资有风险，请根据自身情况决策")

    def get_knowledge_tip(self, day_of_week: int) -> Dict:
        """获取知识点"""
        tips = {
            0: {
                'title': '什么是股息率？',
                'content': '股息率 = 每股年度分红 / 每股股价 × 100%',
                'example': '某股票价格10元，每年分红0.5元，股息率=0.5/10=5%',
                'tip': '股息率越高，分红相对于股价越划算'
            },
            # ...
        }
        return tips.get(day_of_week, tips[0])
```

## generator.py 需要修改的方法

```python
class ContentGenerator:

    def generate_daily_report(self, analysis: Dict, trend: Dict, advice: Dict) -> str:
        """生成完整日报（Markdown格式）"""
        template = self._load_template('daily_report.md')
        return template.format(
            data_table=self._format_data_table(analysis),
            market_interpretation=self._generate_market_text(trend),
            investment_advice=self._format_advice(advice),
            risk_alert=advice.get('risk'),
            knowledge=advice.get('knowledge')
        )

    def generate_xiaohongshu_post(self, analysis: Dict) -> Dict:
        """生成小红书内容"""
        # 优化标题生成
        titles = [
            f"🍠 {self._get_month_day()}红利日报｜股息率{analysis['avg_yield']:.2f}%，这个信号要注意！",
            f"🍠 定投必看｜红利指数分位数{analysis['avg_percentile']:.0f}%，该加仓还是止盈？",
            f"🍠 红利投资日记｜今日股息率出炉，新手定投指南"
        ]
        
        return {
            'title': self._choose_best_title(titles, analysis),
            'content': self._generate_xhs_content(analysis),
            'tags': ['#红利指数', '#定投', '#股息率', '#理财小白', '#基金投资']
        }
```

## main.py 修改

```python
def main():
    # 1. 采集数据
    collector = DataCollector()
    current_data = collector.fetch_all()
    
    # 2. 深度分析（新增）
    analyzer = DividendAnalyzer()
    analysis = analyzer.analyze_all(current_data)
    trend = analyzer.analyze_market_trend(history_data)  # 新增
    advice = analyzer.generate_investment_advice(...)     # 新增
    
    # 3. 生成内容（修改）
    generator = ContentGenerator()
    daily_report = generator.generate_daily_report(analysis, trend, advice)  # 丰富版
    xhs_post = generator.generate_xiaohongshu_post(analysis)  # 优化版
    
    # 4. 存储 & 推送
    storage.save(current_data)
    dingtalk.send(daily_report)
```

## 测试命令

修改完成后，运行测试：

```bash
cd ~/.copaw/workspaces/qwq-automation/hongshutiao
python src/main.py --dry-run  # 本地测试，不推送
```

---

**修改完成后，把生成的日报内容发给我审核！**