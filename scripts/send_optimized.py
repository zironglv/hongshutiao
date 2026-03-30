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


def send_optimized_report(date, indices_data, insights, best_yield, market_view):
    """发送优化版日报
    
    Args:
        date: 日期
        indices_data: 指数数据列表 [{name, yield, percentile, opportunity}]
        insights: 提炼的观点列表 [{insight, source}]
        best_yield: 最高股息率 {name, yield}
        market_view: 整体观点
    """
    
    # 构建指数列表
    opp_emoji = {'fair': '🟢', 'neutral': '🟡', 'caution': '🟠', 'wait': '🔴'}
    indices_lines = []
    for idx in indices_data:
        emoji = opp_emoji.get(idx.get('opportunity', 'neutral'), '⚪')
        indices_lines.append(f"{emoji} **{idx['name']}**: {idx['yield']}% ({idx['percentile']}%分位)")
    
    indices_text = '\n'.join(indices_lines)
    
    # 构建观点部分
    insights_text = "\n## 📰 市场观点（AI提炼）\n\n"
    for i, ins in enumerate(insights, 1):
        insights_text += f"**{i}. {ins['insight']}**\n"
        if ins.get('source'):
            insights_text += f"   _来源：{ins['source']}_\n"
        insights_text += "\n"
    
    # 构建完整消息
    content = f"""{KEYWORD}

## 📅 红利指数日报

**{date}**

---

{indices_text}

---

📈 **整体观点**: {market_view}

🏆 **最高股息率**: {best_yield['name']} (**{best_yield['yield']}%**)

{insights_text}

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
    
    print(f"✅ 已标记为处理完成: {processed_file}")


if __name__ == '__main__':
    # 示例调用
    if len(sys.argv) > 1:
        # 从命令行参数读取 JSON
        data = json.loads(sys.argv[1])
        send_optimized_report(
            date=data['date'],
            indices_data=data['indices'],
            insights=data['insights'],
            best_yield=data['best_yield'],
            market_view=data['market_view']
        )
        mark_processed(data['date'])
    else:
        print("用法: python send_optimized.py '<json_data>'")
        print("示例数据格式:")
        print(json.dumps({
            'date': '2026-03-30',
            'indices': [
                {'name': '红利低波100', 'yield': 4.84, 'percentile': 25, 'opportunity': 'fair'},
            ],
            'insights': [
                {'insight': '📈 红利ETF资金流入增加', 'source': '新浪财经'},
            ],
            'best_yield': {'name': '沪港深红利低波', 'yield': 5.47},
            'market_view': '红利指数整体股息率处于较高水平'
        }, ensure_ascii=False, indent=2))