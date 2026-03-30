#!/usr/bin/env python3
"""
发送红利指数日报到钉钉
"""

import json
import os
import requests
import sys

# 钉钉 Webhook URL
WEBHOOK_URL = os.environ.get('DINGTALK_WEBHOOK', '')
# 关键词（必须包含在消息中）
KEYWORD = '靑枫_QwQ'


def load_analysis_data():
    """加载分析数据"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, '..', 'data', 'analysis_latest.json')
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_news_data():
    """加载新闻数据"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, '..', 'data', 'news_cache.json')
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('news', [])
    except:
        return []


def build_indices_list(analysis):
    """构建指数列表字符串"""
    lines = []
    
    opportunity_emoji = {
        'fair': '🟢',      # 可布局
        'neutral': '🟡',   # 中性
        'caution': '🟠',   # 谨慎
        'wait': '🔴',      # 观望
    }
    
    for item in analysis:
        emoji = opportunity_emoji.get(item['opportunity'], '⚪')
        name = item['name']
        yield_val = item['yield']
        percentile = item['percentile']
        
        lines.append(f"{emoji} **{name}**: {yield_val}% ({percentile:.0f}%分位)")
    
    return '\n'.join(lines)


def get_opportunity_stats(analysis):
    """统计各评级数量"""
    stats = {'fair': 0, 'neutral': 0, 'caution': 0, 'wait': 0}
    for item in analysis:
        opp = item.get('opportunity', 'neutral')
        if opp in stats:
            stats[opp] += 1
    return stats


def extract_news_insights(news_list):
    """从新闻中提炼观点（优先使用 LLM，失败时使用规则）"""
    import os
    import sys
    
    # 检查是否有 LLM API Key
    api_key = os.environ.get('DASHSCOPE_API_KEY', '')
    
    if api_key:
        # 尝试使用 LLM 提炼
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
            from news_llm_insight import LLMInsightExtractor
            
            # 加载股息率数据
            try:
                data_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'analysis_latest.json')
                with open(data_path, 'r') as f:
                    dividend_data = json.load(f)
            except:
                dividend_data = None
            
            extractor = LLMInsightExtractor()
            llm_insights = extractor.extract_insights(news_list, dividend_data)
            
            # 转换格式
            result = []
            for ins in llm_insights:
                result.append({
                    'insight': ins.get('insight', ''),
                    'source': ins.get('source', ''),
                    'news_title': '',
                })
            print("✅ 使用 LLM 提炼观点")
            return result
        except Exception as e:
            print(f"⚠️ LLM 提取失败: {e}，使用规则提取")
    
    # 规则提取（备用方案）
    import re
    
    insights = []
    
    # 观点提取规则
    rules = [
        # ETF 表现
        (r'涨[0-9.]+%', '📈 市场信号：红利ETF表现活跃，显示资金关注度提升'),
        (r'份额增[0-9.]+万', '💰 资金动向：红利ETF份额增加，资金持续流入'),
        (r'份额减[0-9.]+万', '⚠️ 资金动向：红利ETF份额缩减，注意资金流向变化'),
        
        # 防御属性
        (r'防御属性|防守', '🛡️ 市场观点：红利资产防御属性凸显，适合震荡市配置'),
        
        # 高股息
        (r'高股息', '📊 投资观点：高股息策略持续受关注，稳健收益属性明显'),
        
        # 分红数据
        (r'分红数据亮眼|分红', '💰 公司动态：上市公司分红数据向好，红利策略基本面支撑'),
        
        # 超额收益
        (r'超额收益', '✅ 业绩表现：红利基金实现超额收益，策略有效性验证'),
        
        # 净值变化
        (r'净值增长', '📊 基金动态：红利基金净值表现值得关注'),
    ]
    
    seen_insights = set()
    
    for news in news_list[:5]:
        title = news.get('title', '')
        summary = news.get('summary', '')
        source = news.get('source', '')
        
        # 合并标题和摘要进行分析
        content = title + ' ' + summary
        
        for pattern, insight in rules:
            if re.search(pattern, content) and insight not in seen_insights:
                insights.append({
                    'insight': insight,
                    'source': source,
                    'news_title': title[:30] + '...' if len(title) > 30 else title,
                })
                seen_insights.add(insight)
    
    # 如果没有提取到观点，生成一个默认观点
    if not insights and news_list:
        insights.append({
            'insight': '📰 资讯动态：关注红利指数相关市场消息',
            'source': '综合资讯',
            'news_title': '',
        })
    
    return insights[:3]  #最多返回3个观点


def build_insights_section(insights):
    """构建观点部分"""
    if not insights:
        return ""
    
    lines = ["\n---\n\n## 📰 市场观点（提炼自资讯）\n"]
    
    for i, insight in enumerate(insights, 1):
        text = insight['insight']
        source = insight.get('source', '')
        
        lines.append(f"**{i}. {text}**")
        if source:
            lines.append(f"   _来源：{source}_")
        lines.append("")
    
    return '\n'.join(lines)


def send_markdown_message(data, news_list):
    """发送 Markdown 格式消息"""
    
    date = data['date']
    market_view = data.get('market_view', '暂无观点')
    best_yield = data['best_yield']
    analysis = data['analysis']
    
    indices_list = build_indices_list(analysis)
    insights = extract_news_insights(news_list)
    insights_section = build_insights_section(insights)
    
    # 构建消息
    content = f"""{KEYWORD}

## 📅 红利指数日报

**{date}**

---

{indices_list}

---

📈 **整体观点**: {market_view}

🏆 **最高股息率**: {best_yield['name']} (**{best_yield['yield']}%**)

{best_yield['suggestion']}
{insights_section}
---

[📊 查看完整报告](https://zironglv.github.io/hongshutiao/)
"""
    
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": f"红利指数日报 {date}",
            "text": content
        }
    }
    
    return payload


def send_actioncard_message(data, news_list):
    """发送 ActionCard 格式消息（精简版）"""
    
    date = data['date']
    market_view = data.get('market_view', '暂无观点')
    best_yield = data['best_yield']
    stats = get_opportunity_stats(data['analysis'])
    
    # 提取新闻观点摘要
    insights = extract_news_insights(news_list)
    insight_hint = ""
    if insights:
        # 取第一个观点的关键部分
        first_insight = insights[0]['insight']
        if len(first_insight) > 20:
            insight_hint = f"\n💡 {first_insight.split('：')[-1][:20]}..."
    
    text = f"""{KEYWORD}

**{date} 红利指数日报**

📊 最高: {best_yield['name']} **{best_yield['yield']}%**

📈 观点: {market_view}

🟢可布局: {stats['fair']} | 🟡中性: {stats['neutral']} | 🟠谨慎: {stats['caution']} | 🔴观望: {stats['wait']}{insight_hint}
"""
    
    payload = {
        "msgtype": "actionCard",
        "actionCard": {
            "title": "红利指数日报",
            "text": text,
            "btnOrientation": "0",
            "singleTitle": "查看完整报告",
            "singleURL": "https://zironglv.github.io/hongshutiao/"
        }
    }
    
    return payload


def send_message(payload):
    """发送消息到钉钉"""
    if not WEBHOOK_URL:
        print("错误: 未设置 DINGTALK_WEBHOOK 环境变量")
        return False
    
    try:
        response = requests.post(
            WEBHOOK_URL,
            headers={'Content-Type': 'application/json'},
            json=payload,
            timeout=10
        )
        result = response.json()
        
        if result.get('errcode') == 0:
            print(f"✅ 消息发送成功")
            return True
        else:
            print(f"❌ 消息发送失败: {result}")
            return False
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return False


def main():
    """主函数"""
    # 加载数据
    try:
        data = load_analysis_data()
        print(f"📅 日报日期: {data['date']}")
    except Exception as e:
        print(f"❌ 加载数据失败: {e}")
        sys.exit(1)
    
    # 加载新闻
    news_list = load_news_data()
    print(f"📰 新闻条数: {len(news_list)}")
    
    # 提取观点
    insights = extract_news_insights(news_list)
    print(f"💡 提炼观点: {len(insights)} 条")
    for i, insight in enumerate(insights, 1):
        print(f"   {i}. {insight['insight']}")
    
    # 发送 Markdown 消息
    print("\n📤 发送 Markdown 消息...")
    md_payload = send_markdown_message(data, news_list)
    send_message(md_payload)
    
    # 发送 ActionCard 消息
    print("\n📤 发送 ActionCard 消息...")
    ac_payload = send_actioncard_message(data, news_list)
    send_message(ac_payload)
    
    print("\n✅ 日报推送完成")


if __name__ == '__main__':
    main()