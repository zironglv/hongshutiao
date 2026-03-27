"""红薯条 - 红利低波指数监控配置"""

import os

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 中证指数 Excel 文件基础 URL
EXCEL_BASE_URL = "https://oss-ch.csindex.com.cn/static/html/csindex/public/uploads/file/autofile/indicator"

# 监控的指数列表
INDICES = {
    "930740": {
        "name": "300红利低波",
    },
    "930955": {
        "name": "红利低波100",
    },
    "931446": {
        "name": "东证红利低波",
    },
    "H30269": {
        "name": "红利低波",
    },
    "H50040": {
        "name": "上红低波",
    },
    "930992": {
        "name": "沪港深红利低波",
    },
}

def get_excel_url(code: str) -> str:
    """获取指数 Excel 文件的 URL"""
    return f"{EXCEL_BASE_URL}/{code}indicator.xls"

# 请求超时时间（秒）
REQUEST_TIMEOUT = 30

# 数据存储路径
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')