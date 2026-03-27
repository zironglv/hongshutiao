# 🍠 红薯条 - Hongshutiao

> 红利低波指数 TTM 股息率监控助手

## 简介

红薯条是一个红利低波指数监控工具，每个工作日自动采集主流红利指数的 TTM 股息率数据，生成可视化报告。

- 🌐 **在线访问**: [https://zironglv.github.io/hongshutiao/](https://zironglv.github.io/hongshutiao/)

## 监控指数

| 代码 | 名称 |
|------|------|
| 930740 | 300红利低波 |
| 930955 | 红利低波100 |
| 931446 | 东证红利低波 |
| H30269 | 红利低波 |
| H50040 | 上红低波 |
| 930992 | 沪港深红利低波 |

## 功能

- ✅ 自动采集中证指数官网的 TTM 股息率数据
- ✅ 历史数据积累与分位数计算
- ✅ GitHub Pages 网站展示
- ✅ 小红书内容生成（半自动）
- ✅ 钉钉消息推送

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 本地运行

```bash
python src/main.py
```

### 输出文件

```
hongshutiao/
├── data/                    # 历史数据
│   ├── accumulated.json     # 累积数据
│   └── history/             # 每日数据
├── output/                  # 输出内容
│   ├── post_*.json          # 小红书帖子
│   └── push_*.txt           # 推送消息
└── docs/                    # GitHub Pages
    └── data/latest.json     # 网站数据
```

## 自动化

项目使用 GitHub Actions 实现自动化：

- **触发时间**: 每个工作日早上 7:00（北京时间）
- **流程**: 数据采集 → 分析 → 生成内容 → 更新网站

## 数据来源

- 中证指数官网: [https://www.csindex.com.cn/](https://www.csindex.com.cn/)

## 免责声明

⚠️ 本项目数据仅供参考，不构成投资建议。投资有风险，入市需谨慎。

## License

MIT