"""红薯条 - 数据存储模块

负责历史数据的存储和读取，支持数据积累
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

from config import DATA_DIR as CONFIG_DATA_DIR
# 使用配置中的路径
if CONFIG_DATA_DIR and os.path.isabs(CONFIG_DATA_DIR):
    DATA_DIR = CONFIG_DATA_DIR

logger = logging.getLogger(__name__)

# 历史数据目录
HISTORY_DIR = os.path.join(DATA_DIR, "history")


class DataStorage:
    """数据存储管理器"""

    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(HISTORY_DIR, exist_ok=True)

    def save_daily_data(self, data: List[Dict[str, Any]], date: str = None) -> str:
        """保存每日数据
        
        Args:
            data: 采集的数据列表
            date: 日期字符串，默认今天
            
        Returns:
            保存的文件路径
        """
        if not date:
            date = datetime.now().strftime('%Y-%m-%d')
        
        # 保存到日期文件
        filename = f"dividend_{date.replace('-', '')}.json"
        filepath = os.path.join(HISTORY_DIR, filename)
        
        output = {
            'date': date,
            'fetch_time': datetime.now().strftime('%H:%M:%S'),
            'data_count': len(data),
            'indices': data
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"📁 数据已保存: {filepath}")
        
        # 更新累积数据
        self._update_accumulated(data, date)
        
        return filepath

    def _update_accumulated(self, data: List[Dict[str, Any]], date: str):
        """更新累积历史数据"""
        acc_file = os.path.join(DATA_DIR, "accumulated.json")
        
        # 读取已有数据
        accumulated = {}
        if os.path.exists(acc_file):
            with open(acc_file, 'r', encoding='utf-8') as f:
                accumulated = json.load(f)
        
        # 更新每个指数的数据
        for item in data:
            code = item.get('code')
            if not code:
                continue
                
            if code not in accumulated:
                accumulated[code] = {
                    'name': item.get('name'),
                    'history': []
                }
            
            # 添加当日数据
            history_entry = {
                'date': date,
                'dividend_yield': item.get('dividend_yield_2'),
                'pe': item.get('pe_2'),
                'percentile': item.get('dividend_yield_percentile')
            }
            
            # 检查是否已有该日期的数据
            existing = [h for h in accumulated[code]['history'] if h['date'] == date]
            if existing:
                accumulated[code]['history'].remove(existing[0])
            
            accumulated[code]['history'].append(history_entry)
            
            # 按日期排序
            accumulated[code]['history'].sort(key=lambda x: x['date'])
            
            # 只保留最近 365 天的数据
            if len(accumulated[code]['history']) > 365:
                accumulated[code]['history'] = accumulated[code]['history'][-365:]
        
        # 保存
        with open(acc_file, 'w', encoding='utf-8') as f:
            json.dump(accumulated, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📊 累积数据已更新，共 {len(accumulated)} 个指数")

    def get_accumulated(self) -> Dict[str, Any]:
        """获取累积历史数据"""
        acc_file = os.path.join(DATA_DIR, "accumulated.json")
        
        if os.path.exists(acc_file):
            with open(acc_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {}

    def get_recent_data(self, days: int = 30) -> Dict[str, List[Dict]]:
        """获取最近 N 天的数据"""
        accumulated = self.get_accumulated()
        
        result = {}
        for code, info in accumulated.items():
            history = info.get('history', [])
            result[code] = history[-days:] if len(history) > days else history
        
        return result

    def get_latest_data(self) -> List[Dict[str, Any]]:
        """获取最新一天的完整数据"""
        today = datetime.now().strftime('%Y%m%d')
        filename = f"dividend_{today}.json"
        filepath = os.path.join(HISTORY_DIR, filename)
        
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('indices', [])
        
        return []

    def calculate_trend(self, code: str) -> Optional[Dict[str, Any]]:
        """计算指定指数的趋势
        
        Returns:
            {
                'code': 指数代码,
                'name': 指数名称,
                'current_yield': 当前股息率,
                'change_7d': 7日变化,
                'change_30d': 30日变化,
                'avg_30d': 30日平均,
                'max_30d': 30日最高,
                'min_30d': 30日最低,
                'trend': 'up' / 'down' / 'stable'
            }
        """
        accumulated = self.get_accumulated()
        
        if code not in accumulated:
            return None
        
        history = accumulated[code].get('history', [])
        if len(history) < 2:
            return None
        
        # 最近30天数据
        recent = history[-30:] if len(history) >= 30 else history
        
        yields = [h['dividend_yield'] for h in recent if h.get('dividend_yield')]
        if not yields:
            return None
        
        current = yields[-1]
        avg = sum(yields) / len(yields)
        max_y = max(yields)
        min_y = min(yields)
        
        # 计算变化
        change_7d = None
        change_30d = None
        
        if len(yields) >= 7:
            change_7d = current - yields[-7]
        if len(yields) >= 30:
            change_30d = current - yields[0]
        
        # 判断趋势
        if change_7d is not None:
            if change_7d > 0.1:
                trend = 'up'
            elif change_7d < -0.1:
                trend = 'down'
            else:
                trend = 'stable'
        else:
            trend = 'unknown'
        
        return {
            'code': code,
            'name': accumulated[code].get('name'),
            'current_yield': round(current, 4),
            'change_7d': round(change_7d, 4) if change_7d else None,
            'change_30d': round(change_30d, 4) if change_30d else None,
            'avg_30d': round(avg, 4),
            'max_30d': round(max_y, 4),
            'min_30d': round(min_y, 4),
            'trend': trend
        }


if __name__ == "__main__":
    # 测试存储模块
    storage = DataStorage()
    
    # 模拟一些测试数据
    test_data = [
        {
            'code': '930955',
            'name': '红利低波100',
            'dividend_yield_2': 4.88,
            'pe_2': 10.04,
            'dividend_yield_percentile': 45
        }
    ]
    
    storage.save_daily_data(test_data)
    print("累积数据:", json.dumps(storage.get_accumulated(), ensure_ascii=False, indent=2))