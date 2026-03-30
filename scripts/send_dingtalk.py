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


def send_markdown_message(data):
    """发送 Markdown 格式消息"""
    
    date = data['date']
    market_view = data.get('market_view', '暂无观点')
    best_yield = data['best_yield']
    analysis = data['analysis']
    
    indices_list = build_indices_list(analysis)
    
    # 构建消息
    content = f"""{KEYWORD}

## 📅 红利指数日报

**{date}**

---

{indices_list}

---

📈 **观点**: {market_view}

🏆 **最高股息率**: {best_yield['name']} (**{best_yield['yield']}%**)

{best_yield['suggestion']}

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


def send_actioncard_message(data):
    """发送 ActionCard 格式消息（精简版）"""
    
    date = data['date']
    market_view = data.get('market_view', '暂无观点')
    best_yield = data['best_yield']
    stats = get_opportunity_stats(data['analysis'])
    
    text = f"""{KEYWORD}

**{date} 红利指数日报**

📊 最高: {best_yield['name']} **{best_yield['yield']}%**

📈 观点: {market_view}

🟢可布局: {stats['fair']} | 🟡中性: {stats['neutral']} | 🟠谨慎: {stats['caution']} | 🔴观望: {stats['wait']}
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
    
    # 发送 Markdown 消息
    print("\n📤 发送 Markdown 消息...")
    md_payload = send_markdown_message(data)
    send_message(md_payload)
    
    # 发送 ActionCard 消息
    print("\n📤 发送 ActionCard 消息...")
    ac_payload = send_actioncard_message(data)
    send_message(ac_payload)
    
    print("\n✅ 日报推送完成")


if __name__ == '__main__':
    main()