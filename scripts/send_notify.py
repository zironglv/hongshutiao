#!/usr/bin/env python3
import requests

webhook = 'https://oapi.dingtalk.com/robot/send?access_token=2b9b77312e004ab329d64fbdddec83230b4ff95871032418aaff833edbad138f'

data = {
    'msgtype': 'text',
    'text': {
        'content': '''📊 红利日报待审核（2026-04-07）

靑枫_QwQ 请确认以下内容：

【标题】🍠 04月07日红利盘点｜建议收藏

【今日数据摘要】
💰 最高股息率：沪港深红利低波 5.48%
💎 最佳配置：红利低波100 分位20%

【封面图】已生成3张封面图

【操作】
✅ 回复「确认发布」或「发布」
❌ 如有问题请指出'''
    }
}

response = requests.post(webhook, json=data)
print(response.text)