#!/usr/bin/env python3
"""重新生成日报"""

import sys
import os
import json

# 设置路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from generator import ContentGenerator

# 加载分析结果
with open('data/analysis_latest.json') as f:
    analysis = json.load(f)

# 生成内容
gen = ContentGenerator()
result = gen.generate_daily_report(analysis)

# 保存
with open('output/daily_report_20260407.md', 'w') as f:
    f.write(result)

print('日报已生成')