#!/usr/bin/env python3
"""红薯条 - 发送优化版日报到钉钉

由 AI Agent 提炼观点后调用此脚本发送
"""

import json
import os
import requests
import sys

WEBHOOK_URL = os.environ.get('DINGTALK_WEBHOOK', '')
KEYWORD = '靑枫_QwQ'


def calculate_sentiment(indices_data, insights):
    """计算市场情绪热度
    
    基于以下因素：
    - 机会评级分布（fair多=积极，caution/wait多=谨慎）
    - 观点类型（positive=积极，negative=谨慎）
    - 分位数水平（低分位=布局机会，高分位=风险）
    
    Returns:
        sentiment: 情绪值 (0-100)
        label: 情绪标签
        description: 情绪描述
    """
    
    # 1. 从机会评级计算基础情绪
    opp_scores = {'fair': 80, 'neutral': 50, 'caution': 30, 'wait': 20}
    
    opp_counts = {'fair': 0, 'neutral': 0, 'caution': 0, 'wait': 0}
    total_score = 0
    
    for idx in indices_data:
        opp = idx.get('opportunity', 'neutral')
        opp_counts[opp] = opp_counts.get(opp, 0) + 1
        total_score += opp_scores.get(opp, 50)
    
    avg_score = total_score / len(indices_data) if indices_data else 50
    
    # 2. 从观点调整情绪
    insight_adjust = 0
    for ins in insights:
        text = ins.get('insight', '')
        if '📈' in text or '涨' in text or '流入' in text or '增加' in text:
            insight_adjust += 5
        elif '📉' in text or '跌' in text or '流出' in text or '缩水' in text or '减少' in text:
            insight_adjust -= 5
        elif '⚠️' in text:
            insight_adjust -= 3
    
    # 3. 综合计算
    sentiment = min(100, max(0, avg_score + insight_adjust))
    
    # 4. 确定标签
    if sentiment >= 70:
        label = '🔥 偏热'
        description = '市场关注度高，资金流入明显'
    elif sentiment >= 50:
        label = '🟡 中性'
        description = '多空交织，按需配置'
    elif sentiment >= 30:
        label = '🟠 偏冷'
        description = '市场观望情绪较浓'
    else:
        label = '❄️ 冷清'
        description = '资金流出明显，谨慎观望'
    
    return sentiment, label, description


def send_optimized_report(date, indices_data, insights, best_yield, market_view):
    """发送优化版日报
    
    Args:
        date: 日期
        indices_data: 指数数据列表 [{name, yield, percentile, opportunity}]
        insights: 提炼的观点列表 [{insight, source}]
        best_yield: 最高股息率 {name, yield}
        market_view: 整体观点
    """
    
    # 计算情绪热度
    sentiment, sentiment_label, sentiment_desc = calculate_sentiment(indices_data, insights)
    
    # 统计评级分布
    opp_counts = {'fair': 0, 'neutral': 0, 'caution': 0, 'wait': 0}
    for idx in indices_data:
        opp = idx.get('opportunity', 'neutral')
        opp_counts[opp] = opp_counts.get(opp, 0) + 1
    
    # 构建指数列表（按机会评级排序）
    opp_order = ['fair', 'neutral', 'caution', 'wait']
    opp_emoji = {'fair': '🟢', 'neutral': '🟡', 'caution': '🟠', 'wait': '🔴'}
    opp_label = {'fair': '可布局', 'neutral': '中性', 'caution': '谨慎', 'wait': '观望'}
    
    sorted_indices = sorted(indices_data, key=lambda x: opp_order.index(x.get('opportunity', 'neutral')))
    
    # 按评级分组展示
    indices_text = ""
    for opp in opp_order:
        group = [idx for idx in sorted_indices if idx.get('opportunity', 'neutral') == opp]
        if group:
            indices_text += f"\n**{opp_emoji[opp]} {opp_label[opp]} ({len(group)}个)**\n"
            for idx in group:
                indices_text += f"- {idx['name']}: {idx['yield']}% ({idx['percentile']}%分位)\n"
    
    # 构建观点部分
    insights_text = ""
    for i, ins in enumerate(insights, 1):
        insights_text += f"**{i}. {ins['insight']}**\n"
        if ins.get('source'):
            insights_text += f"_来源：{ins['source']}_\n"
        insights_text += "\n"
    
    # 构建完整消息
    content = f"""{KEYWORD}

## 📅 红利指数日报 · {date}

---

### 📊 情绪热度

**{sentiment_label}** ({sentiment}/100)

{sentiment_desc}

---

### 📈 指数概览

{indices_text}

---

### 💡 今日观点

{insights_text}

**🏆 最高股息率**: {best_yield['name']} ({best_yield['yield']}%)

---

[查看完整报告 →](https://zironglv.github.io/hongshutiao/)
"""
    
    payload = {
        "msgtype": "markdown",
        "markdown": {
            "title": f"红利日报 {date}",
            "text": content
        }
    }
    
    return send_message(payload)


def send_actioncard(date, sentiment_label, best_yield, opp_counts):
    """发送 ActionCard 精简版"""
    
    stats_text = f"🟢{opp_counts.get('fair',0)} 🟡{opp_counts.get('neutral',0)} 🟠{opp_counts.get('caution',0)} 🔴{opp_counts.get('wait',0)}"
    
    text = f"""{KEYWORD}

**红利指数日报 · {date}**

📊 情绪: {sentiment_label}

🏆 最高: {best_yield['name']} {best_yield['yield']}%

{stats_text}

"""
    
    payload = {
        "msgtype": "actionCard",
        "actionCard": {
            "title": "红利日报",
            "text": text,
            "btnOrientation": "0",
            "singleTitle": "查看详情",
            "singleURL": "https://zironglv.github.io/hongshutiao/"
        }
    }
    
    return send_message(payload)


def send_message(payload):
    """发送消息"""
    if not WEBHOOK_URL:
        print("错误: 未设置 DINGTALK_WEBHOOK")
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
            print("✅ 消息发送成功")
            return True
        else:
            print(f"❌ 发送失败: {result}")
            return False
    except Exception as e:
        print(f"❌ 发送异常: {e}")
        return False


def mark_processed(date):
    """标记为已处理"""
    data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    processed_file = os.path.join(data_dir, f'processed_{date}.json')
    
    data = {
        'date': date,
        'processed_time': os.popen('date +"%Y-%m-%d %H:%M:%S"').read().strip(),
        'status': 'completed'
    }
    
    with open(processed_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 已标记为处理完成")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        data = json.loads(sys.argv[1])
        
        # 计算情绪
        sentiment, sentiment_label, sentiment_desc = calculate_sentiment(
            data['indices'], data['insights']
        )
        
        # 统计评级
        opp_counts = {'fair': 0, 'neutral': 0, 'caution': 0, 'wait': 0}
        for idx in data['indices']:
            opp = idx.get('opportunity', 'neutral')
            opp_counts[opp] = opp_counts.get(opp, 0) + 1
        
        # 发送 Markdown 版
        send_optimized_report(
            date=data['date'],
            indices_data=data['indices'],
            insights=data['insights'],
            best_yield=data['best_yield'],
            market_view=data.get('market_view', '')
        )
        
        # 发送 ActionCard 精简版
        send_actioncard(
            date=data['date'],
            sentiment_label=sentiment_label,
            best_yield=data['best_yield'],
            opp_counts=opp_counts
        )
        
        mark_processed(data['date'])
    else:
        print("用法: python send_optimized.py '<json_data>'")