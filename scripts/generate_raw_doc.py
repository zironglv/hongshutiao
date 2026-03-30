#!/usr/bin/env python3
"""红薯条 - 原始数据文档生成器

生成包含所有原始数据的 markdown 文档，供 AI Agent 提炼观点
"""

import json
import os
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')


def generate_raw_document():
    """生成原始数据文档"""
    
    # 读取股息率数据
    analysis_path = os.path.join(DATA_DIR, 'analysis_latest.json')
    with open(analysis_path, 'r', encoding='utf-8') as f:
        analysis = json.load(f)
    
    # 读取新闻数据
    news_path = os.path.join(DATA_DIR, 'news_cache.json')
    try:
        with open(news_path, 'r', encoding='utf-8') as f:
            news_data = json.load(f)
            news_list = news_data.get('news', [])
    except:
        news_list = []
    
    date = analysis.get('date', datetime.now().strftime('%Y-%m-%d'))
    
    # 构建 markdown 文档
    doc = f"""# 红利指数日报 - 原始数据

> 日期: {date}
> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> 此文档供 AI Agent 提炼观点和优化日报

---

## 一、股息率数据

### 各指数详情

| 指数名称 | 代码 | TTM股息率 | 历史分位数 | 评级 | 机会评级 | 建议 |
|----------|------|-----------|------------|------|----------|------|
"""
    
    for item in analysis.get('analysis', []):
        name = item.get('name', '')
        code = item.get('code', '')
        yield_val = item.get('yield', 0)
        percentile = item.get('percentile', 0)
        level = item.get('level', '')
        opportunity = item.get('opportunity', '')
        suggestion = item.get('suggestion', '')
        
        doc += f"| {name} | {code} | {yield_val}% | {percentile}% | {level} | {opportunity} | {suggestion[:30]}... |\n"
    
    doc += f"""

### 汇总数据

- **平均股息率**: {analysis.get('avg_yield', 'N/A')}
- **平均分位数**: {analysis.get('avg_percentile', 'N/A')}
- **整体观点**: {analysis.get('market_view', '暂无')}

### 最高股息率指数

- **名称**: {analysis.get('best_yield', {}).get('name', '')}
- **股息率**: {analysis.get('best_yield', {}).get('yield', '')}%
- **分位数**: {analysis.get('best_yield', {}).get('percentile', '')}%
- **建议**: {analysis.get('best_yield', {}).get('suggestion', '')}

---

## 二、相关资讯

> 共 {len(news_list)} 条新闻，来源: Tavily API

"""
    
    for i, news in enumerate(news_list, 1):
        title = news.get('title', '')
        source = news.get('source', '')
        summary = news.get('summary', '')
        url = news.get('url', '')
        score = news.get('score', 0)
        
        doc += f"""### 新闻 {i}

**标题**: {title}

**来源**: {source} | **相关度**: {score:.2f}

**摘要**: {summary}

**链接**: {url}

---

"""
    
    doc += """## 三、待提炼内容

请 AI Agent 从以上数据中提炼以下内容：

1. **市场观点**（2-3条）
   - 从新闻中提炼有价值的市场信号
   - 结合股息率数据给出投资建议

2. **资金动向**
   - ETF 份额变化
   - 资金流入流出信号

3. **操作建议**
   - 结合分位数给出定投建议
   - 是否需要调整仓位

---

## 四、输出格式参考

提炼后的日报应包含：

```markdown
## 📰 市场观点（提炼自资讯）

1. 📈 观点内容
   _来源：xxx_

2. 💰 观点内容
   _来源：xxx_

3. 📊 观点内容
   _来源：xxx_
```

---
"""
    
    # 保存文档
    output_path = os.path.join(OUTPUT_DIR, f'raw_data_{date}.md')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(doc)
    
    print(f"✅ 原始数据文档已生成: {output_path}")
    
    # 同时生成 latest.json 供网页使用
    generate_latest_json(analysis, news_list)
    
    return output_path


def generate_latest_json(analysis, news_list):
    """生成网页数据文件"""
    
    docs_dir = os.path.join(PROJECT_ROOT, 'docs')
    os.makedirs(docs_dir, exist_ok=True)
    
    # 构建网页数据
    indices = []
    for item in analysis.get('analysis', []):
        indices.append({
            'name': item.get('name', ''),
            'code': item.get('code', ''),
            'yield': item.get('yield', 0),
            'percentile': item.get('percentile', 0),
            'level': item.get('level', ''),
            'opportunity': item.get('opportunity', ''),
            'suggestion': item.get('suggestion', '')
        })
    
    # 构建观点数据
    insights = []
    for news in news_list[:5]:  # 取前5条新闻
        title = news.get('title', '')
        source = news.get('source', '')
        summary = news.get('summary', '')
        
        # 根据标题添加情绪标记
        emoji = '📊'
        if '涨' in title or '流入' in title or '增加' in title:
            emoji = '📈'
        elif '跌' in title or '流出' in title or '减少' in title or '缩水' in title:
            emoji = '📉'
        elif '风险' in title or '谨慎' in title:
            emoji = '⚠️'
        
        insights.append({
            'insight': f"{emoji} {title}",
            'source': source,
            'summary': summary
        })
    
    # 构建历史数据（简化版）
    history = []
    history_path = os.path.join(DATA_DIR, 'history.json')
    try:
        with open(history_path, 'r', encoding='utf-8') as f:
            history = json.load(f)
    except:
        pass
    
    # 如果历史数据中没有今天的记录，添加今天的
    today_record = {
        'date': analysis.get('date', ''),
        'indices': indices
    }
    
    if history and history[-1].get('date') != today_record['date']:
        history.append(today_record)
        # 只保留最近30天
        history = history[-30:]
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    data = {
        'date': analysis.get('date', ''),
        'indices': indices,
        'insights': insights,
        'history': history[-7:],  # 最近7天用于图表
        'avg_yield': analysis.get('avg_yield', ''),
        'market_view': analysis.get('market_view', ''),
        'best_yield': analysis.get('best_yield', {})
    }
    
    latest_path = os.path.join(docs_dir, 'data', 'latest.json')
    os.makedirs(os.path.dirname(latest_path), exist_ok=True)
    with open(latest_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 网页数据已生成: {latest_path}")


if __name__ == '__main__':
    generate_raw_document()