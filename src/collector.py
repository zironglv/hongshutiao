"""红薯条 - 数据采集模块

从中证指数官网获取红利低波指数的 TTM 股息率数据
"""

import requests
import pandas as pd
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import os
import json

from config import INDICES, REQUEST_TIMEOUT, DATA_DIR, get_excel_url

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DividendCollector:
    """股息率数据采集器"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/vnd.ms-excel, application/octet-stream, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.csindex.com.cn/',
        })

    def fetch_excel(self, code: str) -> Optional[bytes]:
        """下载指数 Excel 文件
        
        Args:
            code: 指数代码
            
        Returns:
            Excel 文件内容 (bytes)，失败返回 None
        """
        url = get_excel_url(code)
        try:
            logger.info(f"开始下载 {code} 指数数据: {url}")
            response = self.session.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            logger.info(f"下载成功，文件大小: {len(response.content)} bytes")
            return response.content
            
        except Exception as e:
            logger.error(f"下载 {code} 指数数据失败: {e}")
            return None

    def parse_excel(self, content: bytes, code: str) -> Optional[pd.DataFrame]:
        """解析 Excel 文件，提取股息率数据
        
        Args:
            content: Excel 文件内容 (bytes 或文件路径)
            code: 指数代码
            
        Returns:
            包含股息率数据的 DataFrame
        """
        try:
            import io
            # 读取 Excel 文件
            if isinstance(content, bytes):
                df = pd.read_excel(io.BytesIO(content), engine='xlrd')
            else:
                df = pd.read_excel(content, engine='xlrd')
            logger.info(f"解析 Excel 成功，共 {len(df)} 行数据")
            logger.info(f"列名: {df.columns.tolist()}")
            
            return df
            
        except Exception as e:
            logger.error(f"解析 {code} Excel 文件失败: {e}")
            return None

    def extract_dividend_data(self, df: pd.DataFrame, code: str) -> Optional[Dict[str, Any]]:
        """从 DataFrame 中提取股息率数据
        
        根据 DATA_SOURCES_ANALYSIS.md 文档，Excel 包含以下关键字段：
        - 日期Date
        - 股息率1（总股本）D/P1
        - 股息率2（计算用股本）D/P2
        - 市盈率1（总股本）P/E1
        - 市盈率2（计算用股本）P/E2
        
        Args:
            df: 解析后的 DataFrame
            code: 指数代码
            
        Returns:
            股息率数据字典
        """
        try:
            result = {
                'code': code,
                'name': INDICES.get(code, {}).get('name', '未知'),
                'fetch_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            }
            
            # 标准化列名
            df.columns = df.columns.str.strip()
            logger.info(f"标准化后列名: {df.columns.tolist()}")
            
            # 查找日期列
            date_col = None
            for col in df.columns:
                if '日期' in str(col) or 'Date' in str(col):
                    date_col = col
                    break
            
            if date_col is None:
                logger.warning(f"未找到日期列，使用第一列作为日期列")
                date_col = df.columns[0]
            
            # 查找股息率列
            dp1_col = None
            dp2_col = None
            pe1_col = None
            pe2_col = None
            
            for col in df.columns:
                col_str = str(col)
                if '股息率1' in col_str or 'D/P1' in col_str:
                    dp1_col = col
                elif '股息率2' in col_str or 'D/P2' in col_str:
                    dp2_col = col
                elif '市盈率1' in col_str or 'P/E1' in col_str:
                    pe1_col = col
                elif '市盈率2' in col_str or 'P/E2' in col_str:
                    pe2_col = col
            
            logger.info(f"找到的列: 日期={date_col}, D/P1={dp1_col}, D/P2={dp2_col}, P/E1={pe1_col}, P/E2={pe2_col}")
            
            # 获取最新一行数据
            if len(df) > 0:
                latest = df.iloc[-1]
                
                result['latest_date'] = str(latest[date_col]) if date_col else None
                result['dividend_yield_1'] = float(latest[dp1_col]) if dp1_col and pd.notna(latest[dp1_col]) else None
                result['dividend_yield_2'] = float(latest[dp2_col]) if dp2_col and pd.notna(latest[dp2_col]) else None
                result['pe_1'] = float(latest[pe1_col]) if pe1_col and pd.notna(latest[pe1_col]) else None
                result['pe_2'] = float(latest[pe2_col]) if pe2_col and pd.notna(latest[pe2_col]) else None
                
                # 获取历史数据（用于计算分位数）
                if dp2_col:
                    result['history_dp2'] = df[dp2_col].dropna().tolist()[-30:]  # 最近30天
                if pe2_col:
                    result['history_pe2'] = df[pe2_col].dropna().tolist()[-30:]
                
                # 计算当前股息率在历史中的分位数
                if dp2_col and result['dividend_yield_2']:
                    history = df[dp2_col].dropna()
                    if len(history) > 1:
                        percentile = (history <= result['dividend_yield_2']).sum() / len(history) * 100
                        result['dividend_yield_percentile'] = round(percentile, 2)
            
            return result
            
        except Exception as e:
            logger.error(f"提取 {code} 股息率数据失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def collect_one(self, code: str) -> Optional[Dict[str, Any]]:
        """采集单个指数的数据
        
        Args:
            code: 指数代码
            
        Returns:
            指数数据字典
        """
        logger.info(f"\n{'='*50}")
        logger.info(f"开始采集: {INDICES.get(code, {}).get('name', code)} ({code})")
        
        # 下载 Excel
        content = self.fetch_excel(code)
        if not content:
            return None
        
        # 解析 Excel
        df = self.parse_excel(content, code)
        if df is None:
            return None
        
        # 提取股息率数据
        result = self.extract_dividend_data(df, code)
        return result

    def collect_all(self) -> List[Dict[str, Any]]:
        """采集所有指数的数据
        
        Returns:
            所有指数数据的列表
        """
        results = []
        
        for code in INDICES:
            result = self.collect_one(code)
            if result:
                results.append(result)
                logger.info(f"✅ 采集成功: {code} - {result.get('name')}")
            else:
                logger.warning(f"❌ 采集失败: {code}")
        
        return results

    def save_results(self, results: List[Dict[str, Any]], filename: str = None) -> str:
        """保存采集结果
        
        Args:
            results: 采集结果
            filename: 文件名（不含路径）
            
        Returns:
            保存的文件路径
        """
        if not filename:
            filename = f"dividend_data_{datetime.now().strftime('%Y%m%d')}.json"
        
        os.makedirs(DATA_DIR, exist_ok=True)
        filepath = os.path.join(DATA_DIR, filename)
        
        # 添加采集时间戳
        output = {
            'fetch_date': datetime.now().strftime('%Y-%m-%d'),
            'fetch_time': datetime.now().strftime('%H:%M:%S'),
            'data_count': len(results),
            'indices': results
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2, default=str)
        
        logger.info(f"📁 数据已保存到: {filepath}")
        return filepath

    def print_summary(self, results: List[Dict[str, Any]]):
        """打印采集结果摘要"""
        print("\n" + "="*60)
        print("🍠 红薯条 - 股息率数据采集摘要")
        print("="*60)
        print(f"采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"成功采集: {len(results)}/{len(INDICES)} 个指数")
        print("-"*60)
        
        for r in results:
            print(f"\n📊 {r['name']} ({r['code']})")
            print(f"   日期: {r.get('latest_date', 'N/A')}")
            if r.get('dividend_yield_2'):
                print(f"   股息率(D/P2): {r['dividend_yield_2']:.4f}%")
            if r.get('dividend_yield_percentile'):
                print(f"   历史分位数: {r['dividend_yield_percentile']}%")
            if r.get('pe_2'):
                print(f"   市盈率(P/E2): {r['pe_2']:.2f}")
        
        print("\n" + "="*60)


def main():
    """主函数 - 测试采集"""
    collector = DividendCollector()
    
    # 测试全部采集
    results = collector.collect_all()
    collector.print_summary(results)
    collector.save_results(results)


if __name__ == "__main__":
    main()