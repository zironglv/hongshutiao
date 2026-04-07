# 红利日报预处理流水线

## 流程概述

```
7:00 预处理触发
     ↓
Step 1: 数据采集 (Script)
     ↓
Step 2: 数据分析 (Script)
     ↓
Step 3: 内容生成 (Agent)
     ↓
Step 4: 封面生成 (Script)
     ↓
Step 5: 发送审核通知 (Script)
     ↓
状态: waiting_confirm
     ↓
【发布触发机制】
├── 方式1: 用户在钉钉回复「确认发布」→ Agent 立即响应执行
├── 方式2: 定时检查任务 (9/10/11/14/15点) → 发现 waiting_confirm + 已确认 → 执行发布
└── 方式3: 用户手动触发「发布日报」指令
     ↓
发布执行 (Agent)
```

## 数据目录结构

```
hongshutiao/
├── data/
│   ├── YYYY-MM-DD/
│   │   ├── raw.json           # 原始采集数据
│   │   ├── analyzed.json      # 分析结果
│   │   └── status.json        # 当日状态
│   └── history/
│       └── dividend_*.json    # 历史累积数据
│
├── content/
│   └── YYYY-MM-DD/
│       └── content.json       # 小红书内容（标题+正文+话题）
│
├── assets/
│   └── YYYY-MM-DD/
│       ├── cover_1.png        # 封面图1
│       ├── cover_2.png        # 封面图2
│       ├── cover_3.png        # 封面图3
│
└── status/
    └── pipeline_state.json    # 全局流水线状态
```

## 状态定义

| 状态 | 含义 | 下一步 |
|------|------|--------|
| `pending` | 等待开始 | 执行 Step 1 |
| `collecting` | 正在采集数据 | Step 1 执行中 |
| `collected` | 数据采集完成 | 执行 Step 2 |
| `analyzing` | 正在分析数据 | Step 2 执行中 |
| `analyzed` | 数据分析完成 | 执行 Step 3 |
| `generating_content` | 正在生成内容 | Step 3 执行中 |
| `content_generated` | 内容生成完成 | 执行 Step 4 |
| `generating_cover` | 正在生成封面 | Step 4 执行中 |
| `generated` | 封面生成完成 | 执行 Step 5 |
| `waiting_confirm` | 等待用户确认 | 用户确认 |
| `confirmed` | 用户已确认，待发布 | 执行发布 |
| `publishing` | 正在发布 | 发布执行中 |
| `published` | 已发布成功 | 完成 |
| `failed` | 失败 | 需人工介入 |

## 用户确认机制

用户在钉钉回复以下内容视为确认：
- 「确认发布」
- 「发布」
- 「OK」
- 「可以」

Agent 收到确认后：
1. 更新 `pipeline_state.json` 中 `user_confirmed = true`
2. 状态变为 `confirmed`
3. 检查素材是否 ready
4. 执行发布

## Step 1: 数据采集

**执行方式**: Script
**脚本**: `src/collector.py`
**输入**: 无
**输出**: `data/YYYY-MM-DD/raw.json`

```bash
cd ~/.copaw/workspaces/qwq-automation/hongshutiao/src
python3 collector.py
```

**状态更新**: `pending` → `collecting` → `collected`

## Step 2: 数据分析

**执行方式**: Script
**脚本**: `src/analyzer.py`
**输入**: `data/YYYY-MM-DD/raw.json`, `data/history/*.json`
**输出**: `data/YYYY-MM-DD/analyzed.json`

```bash
cd ~/.copaw/workspaces/qwq-automation/hongshutiao/src
python3 analyzer.py --date YYYY-MM-DD
```

**状态更新**: `collected` → `analyzing` → `analyzed`

**分析输出格式**:
```json
{
  "date": "YYYY-MM-DD",
  "best_yield": { ... },
  "best_opportunity": { ... },
  "analysis": [ ... ]
}
```

## Step 3: 内容生成

**执行方式**: Agent
**输入**: `data/YYYY-MM-DD/analyzed.json`
**输出**: `content/YYYY-MM-DD/content.json`

**Agent Prompt**:
```
请根据今日红利指数数据，生成小红书日报内容。

数据来源: ~/.copaw/workspaces/qwq-automation/hongshutiao/data/YYYY-MM-DD/analyzed.json

要求：
1. 标题：20字以内，吸引眼球，使用 emoji
2. 正文：小红书风格，包含：
   - 日期和问候
   - 股息率数据表格（6个指数）
   - 今日观点
   - 操作建议
   - 互动话题
   - 免责声明
3. 话题：3-5个相关话题标签

输出格式：
{
  "title": "标题",
  "body": "正文内容",
  "tags": ["#话题1", "#话题2", ...]
}

保存到: ~/.copaw/workspaces/qwq-automation/hongshutiao/content/YYYY-MM-DD/content.json
```

**状态更新**: `analyzed` → `generating_content` → `content_generated`

## Step 4: 封面生成

**执行方式**: Script (HTML模板 + Playwright截图)
**模板位置**: `~/.copaw/workspaces/qwq-automation/skills/hongshutiao-daily-cover/templates/`
**脚本**: `~/projects/xhs-account-growth/scripts/html_to_png.py`
**输入**: `data/YYYY-MM-DD/analyzed.json`
**输出**: `assets/YYYY-MM-DD/cover_*.png`

**流程**：
```bash
# 1. 复制模板到 assets 目录
cp ~/.copaw/workspaces/qwq-automation/skills/hongshutiao-daily-cover/templates/cover_*.html ~/projects/xhs-account-growth/assets/

# 2. 更新 HTML 模板中的数据
#    - 日期: date-tag
#    - 情绪热度分数: heat-score
#    - 机会提示: opp-title
#    - 股息率表格数据: yield-val, perc-val, perc-fill width

# 3. 运行 Playwright 截图
cd ~/projects/xhs-account-growth/scripts
python3 html_to_png.py

# 4. 复制封面图到 hongshutiao 目录
cp ~/projects/xhs-account-growth/assets/xhs_cover_*.png ~/.copaw/workspaces/qwq-automation/hongshutiao/assets/YYYY-MM-DD/
```

**状态更新**: `content_generated` → `generating_cover` → `generated`

**封面设计** (Notion 风格，白底 #ffffff，主色 #37352f):
- Cover 1: 概览（情绪热度 + 最佳配置机会 + 数据表格）
- Cover 2: 趋势图（近7日股息率走势）
- Cover 3: 观点（今日观点 + 操作建议）

## Step 5: 发送审核通知

**执行方式**: Script
**脚本**: `scripts/send_preview.py`
**输入**: `content/YYYY-MM-DD/content.json`, `assets/YYYY-MM-DD/*.png`
**输出**: 钉钉消息

```bash
cd ~/.copaw/workspaces/qwq-automation/hongshutiao/scripts
python3 send_preview.py --date YYYY-MM-DD
```

**状态更新**: `generated` → `waiting_confirm`

**钉钉消息格式**:
```
📊 红利日报待审核（YYYY-MM-DD）

【标题】
[标题内容]

【正文预览】
[正文前200字]...

【封面图预览】
![封面1](GitHub Pages URL)
![封面2](GitHub Pages URL)
![封面3](GitHub Pages URL)

【操作】
✅ 回复「确认发布」或「发布」
❌ 如有问题请指出
```

## 发布阶段

**触发条件**: 用户回复「确认发布」或「发布」
**执行方式**: Agent
**输入**: 所有预处理素材

**Agent 操作流程**:
1. 检查 `status = waiting_confirm`
2. 检查所有素材文件存在
3. 打开小红书创作平台
4. 上传三张封面图
5. 填写标题和正文
6. 添加话题标签
7. 点击发布
8. 更新状态为 `published`
9. 发送钉钉通知

## 失败处理

| 失败阶段 | 处理方式 |
|----------|----------|
| Step 1 失败 | 状态=failed，钉钉告警，可手动重试 |
| Step 2 失败 | 同上 |
| Step 3 失败 | Agent 尝试重新生成，最多3次 |
| Step 4 失败 | 检查模板和数据，手动修复 |
| Step 5 失败 | 检查钉钉 webhook，手动发送 |
| 发布失败 | 状态=publish_failed，素材已准备好，可手动发布 |

## 状态检查脚本

```bash
# 检查今日预处理状态
python3 scripts/check_status.py --date YYYY-MM-DD

# 输出：
# 状态: waiting_confirm
# 数据: ✅ ready
# 内容: ✅ ready
# 封面: ✅ ready
# 可以发布: YES
```

---

*最后更新: 2026-04-07*