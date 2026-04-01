#!/usr/bin/env python3
"""红薯条 - 图片生成模块

生成小红书封面图片
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Any

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# 项目路径
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'output')
ASSETS_DIR = os.path.join(PROJECT_ROOT, 'assets')


def generate_cover_image(data: List[Dict[str, Any]], date_str: str = None) -> str:
    """生成小红书封面图片
    
    Args:
        data: 股息率数据列表
        date_str: 日期字符串
        
    Returns:
        生成的图片路径
    """
    if not PIL_AVAILABLE:
        print("❌ PIL 未安装，无法生成图片")
        return None
    
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 图片尺寸 (3:4 比例，适合小红书)
    WIDTH = 1080
    HEIGHT = 1440
    
    # 颜色配置
    BG_COLOR = '#FFF5E6'  # 温暖的米色背景
    TITLE_COLOR = '#D35400'  # 橙色标题
    TEXT_COLOR = '#333333'  # 深灰文字
    ACCENT_COLOR = '#E74C3C'  # 红色强调
    CARD_BG = '#FFFFFF'  # 卡片背景
    
    # 创建图片
    img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # 尝试加载字体
    try:
        # macOS 系统字体
        title_font = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 48)
        subtitle_font = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 32)
        body_font = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 28)
        small_font = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 24)
    except:
        # 备选字体
        try:
            title_font = ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc', 48)
            subtitle_font = ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc', 32)
            body_font = ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc', 28)
            small_font = ImageFont.truetype('/System/Library/Fonts/STHeiti Light.ttc', 24)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            body_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
    
    # 日期
    if not date_str:
        date_str = datetime.now().strftime('%Y年%m月%d日')
    
    weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    weekday = weekday_names[datetime.now().weekday()]
    
    # 绘制标题区域
    y = 60
    
    # Logo/图标区域 (红薯条 emoji)
    draw.text((WIDTH // 2, y), '🍠', font=title_font, fill=TITLE_COLOR, anchor='mm')
    y += 80
    
    # 标题
    draw.text((WIDTH // 2, y), '红利指数日报', font=title_font, fill=TITLE_COLOR, anchor='mm')
    y += 60
    
    # 日期
    draw.text((WIDTH // 2, y), f'{date_str} {weekday}', font=subtitle_font, fill=TEXT_COLOR, anchor='mm')
    y += 80
    
    # 分隔线
    draw.line([(100, y), (WIDTH - 100, y)], fill='#E0E0E0', width=2)
    y += 30
    
    # 数据卡片
    card_width = WIDTH - 100
    card_height = 70
    card_x = 50
    
    for item in data:
        name = item.get('name', '')
        yield_val = item.get('dividend_yield_2')
        percentile = item.get('dividend_yield_percentile')
        
        if yield_val is None:
            continue
        
        # 卡片背景
        draw.rounded_rectangle(
            [(card_x, y), (card_x + card_width, y + card_height)],
            radius=10,
            fill=CARD_BG,
            outline='#E8E8E8',
            width=1
        )
        
        # 指数名称
        draw.text((card_x + 20, y + 20), name, font=body_font, fill=TEXT_COLOR)
        
        # 股息率
        yield_text = f'{yield_val:.2f}%'
        yield_color = ACCENT_COLOR if yield_val >= 5.0 else TITLE_COLOR
        draw.text((card_x + card_width - 200, y + 20), yield_text, font=body_font, fill=yield_color)
        
        # 分位数标签
        if percentile:
            perc_text = f'{percentile:.0f}%'
            perc_color = '#27AE60' if percentile <= 40 else ('#E74C3C' if percentile >= 80 else '#F39C12')
            draw.text((card_x + card_width - 80, y + 25), perc_text, font=small_font, fill=perc_color)
        
        y += card_height + 15
    
    # 观点区域
    y += 30
    draw.line([(100, y), (WIDTH - 100, y)], fill='#E0E0E0', width=2)
    y += 30
    
    # 计算平均分位数
    percentiles = [item.get('dividend_yield_percentile') for item in data if item.get('dividend_yield_percentile')]
    avg_percentile = sum(percentiles) / len(percentiles) if percentiles else 50
    
    # 观点标题
    draw.text((WIDTH // 2, y), '💡 今日观点', font=subtitle_font, fill=TITLE_COLOR, anchor='mm')
    y += 50
    
    # 观点内容
    if avg_percentile >= 80:
        view_text = '估值偏高，注意风险'
        view_color = ACCENT_COLOR
    elif avg_percentile <= 40:
        view_text = '估值偏低，可考虑布局'
        view_color = '#27AE60'
    else:
        view_text = '估值适中，正常定投'
        view_color = TITLE_COLOR
    
    draw.text((WIDTH // 2, y), view_text, font=body_font, fill=view_color, anchor='mm')
    y += 50
    
    # 操作建议
    if avg_percentile >= 80:
        suggestion = '新手：减半定投或观望'
    elif avg_percentile <= 40:
        suggestion = '新手：可适当加仓'
    else:
        suggestion = '新手：正常定投即可'
    
    draw.text((WIDTH // 2, y), suggestion, font=small_font, fill=TEXT_COLOR, anchor='mm')
    
    # 底部信息
    y = HEIGHT - 100
    draw.text((WIDTH // 2, y), '数据来源：中证指数官网', font=small_font, fill='#999999', anchor='mm')
    y += 35
    draw.text((WIDTH // 2, y), '⚠️ 仅供参考，不构成投资建议', font=small_font, fill='#999999', anchor='mm')
    
    # 保存图片
    date_file = datetime.now().strftime('%Y%m%d')
    filename = f'cover_{date_file}.png'
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    img.save(filepath, 'PNG', quality=95)
    print(f"✅ 封面图片已生成: {filepath}")
    
    return filepath


def main():
    """测试图片生成"""
    # 模拟数据
    test_data = [
        {'name': '沪港深红利低波', 'dividend_yield_2': 5.54, 'dividend_yield_percentile': 90},
        {'name': '红利低波', 'dividend_yield_2': 4.98, 'dividend_yield_percentile': 95},
        {'name': '红利低波100', 'dividend_yield_2': 4.90, 'dividend_yield_percentile': 40},
        {'name': '上红低波', 'dividend_yield_2': 4.74, 'dividend_yield_percentile': 95},
        {'name': '300红利低波', 'dividend_yield_2': 4.51, 'dividend_yield_percentile': 95},
        {'name': '东证红利低波', 'dividend_yield_2': 4.43, 'dividend_yield_percentile': 90},
    ]
    
    filepath = generate_cover_image(test_data)
    if filepath:
        print(f"图片路径: {filepath}")


if __name__ == "__main__":
    main()