#!/usr/bin/env python3
"""
红利指数日报封面生成器
按照 hongshutiao/templates/daily_v2_*.html 模板风格
尺寸：1080 x 1440 (小红书封面)
"""

from PIL import Image, ImageDraw, ImageFont
import os
import json
from datetime import datetime

# 路径配置
HONGSHUTIAO_DIR = os.path.expanduser("~/.copaw/workspaces/qwq-automation/hongshutiao")
DATA_DIR = os.path.join(HONGSHUTIAO_DIR, "data")
HISTORY_DIR = os.path.join(DATA_DIR, "history")
OUTPUT_DIR = os.path.expanduser("~/projects/xhs-account-growth/assets")

# 尺寸配置 (小红书封面 3:4)
WIDTH = 1080
HEIGHT = 1440

# 颜色配置 (橙色主题)
COLORS = {
    'bg': (255, 245, 230),           # #FFF5E6 背景色
    'primary': (211, 84, 0),          # #D35400 主色橙
    'primary_light': (230, 126, 34),  # #E67E22 橙色渐变
    'white': (255, 255, 255),
    'text_dark': (51, 51, 51),        # #333
    'text_gray': (102, 102, 102),     # #666
    'text_light': (136, 136, 136),    # #888
    'green': (39, 174, 96),           # #27AE60 低分位数(好)
    'red': (231, 76, 60),             # #E74C3C 高分位数(注意)
    'light_green_bg': (232, 245, 233), # #E8F5E9 浅绿背景
    'light_orange_bg': (255, 243, 224), # #FFF3E0 浅橙背景
}

def get_font(size, bold=False):
    """获取字体"""
    font_paths = [
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    return ImageFont.load_default()

def draw_rounded_rect(draw, coords, radius, fill):
    """绘制圆角矩形"""
    x1, y1, x2, y2 = coords
    draw.rectangle([x1+radius, y1, x2-radius, y2], fill=fill)
    draw.rectangle([x1, y1+radius, x2, y2-radius], fill=fill)
    d = radius * 2
    draw.ellipse([x1, y1, x1+d, y1+d], fill=fill)
    draw.ellipse([x2-d, y1, x2, y1+d], fill=fill)
    draw.ellipse([x1, y2-d, x1+d, y2], fill=fill)
    draw.ellipse([x2-d, y2-d, x2, y2], fill=fill)

def load_today_data():
    """加载今日分析数据"""
    analysis_file = os.path.join(DATA_DIR, "analysis_latest.json")
    with open(analysis_file, 'r') as f:
        return json.load(f)

def load_history_data(days=7):
    """加载历史数据用于趋势图"""
    history_files = sorted(os.listdir(HISTORY_DIR), reverse=True)
    history_files = [f for f in history_files if f.startswith('dividend_') and f.endswith('.json')]
    
    history_data = []
    for f in history_files[:days]:
        filepath = os.path.join(HISTORY_DIR, f)
        with open(filepath, 'r') as file:
            data = json.load(file)
            date_str = f.replace('dividend_', '').replace('.json', '')
            indices = data.get('indices', data.get('data', []))
            history_data.append({
                'date': date_str,
                'indices': indices
            })
    
    return list(reversed(history_data))  # 按时间正序

def create_cover_1(today_data):
    """第一张：概览 - 平均股息率 + 各指数数据"""
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    # 字体
    font_title = get_font(42, bold=True)
    font_date = get_font(24)
    font_big = get_font(48, bold=True)
    font_medium = get_font(22)
    font_yield = get_font(24, bold=True)
    font_small = get_font(16)
    
    # === Header ===
    y = 50
    draw.text((WIDTH//2, y), "🍠", font=get_font(50), fill=COLORS['primary'], anchor="mm")
    y += 45
    draw.text((WIDTH//2, y), "红利指数日报", font=font_title, fill=COLORS['primary'], anchor="mm")
    y += 50
    
    # 日期
    date_str = today_data['date']
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][dt.weekday()]
    draw.text((WIDTH//2, y), f"📅 {dt.year}年{dt.month:02d}月{dt.day:02d}日 {weekday}", 
              font=font_date, fill=COLORS['text_gray'], anchor="mm")
    
    # === 计算汇总数据 ===
    indices = today_data['analysis']
    avg_yield = sum(i['yield'] for i in indices) / len(indices)
    avg_percentile = sum(i['percentile'] for i in indices) / len(indices)
    
    # 判断配置机会
    if avg_percentile < 30:
        opportunity_text = "最佳配置时机"
        opportunity_color = COLORS['green']
    elif avg_percentile > 70:
        opportunity_text = "建议观望"
        opportunity_color = COLORS['red']
    else:
        opportunity_text = "存在配置机会"
        opportunity_color = COLORS['primary']
    
    # === 汇总卡片 ===
    y += 60
    card_x = 50
    card_width = WIDTH - 100
    draw_rounded_rect(draw, (card_x, y, card_x + card_width, y + 120), 16, COLORS['primary'])
    
    draw.text((WIDTH//2, y + 25), "平均股息率", font=get_font(22), fill=COLORS['white'], anchor="mm")
    draw.text((WIDTH//2, y + 65), f"{avg_yield:.2f}%", font=font_big, fill=COLORS['white'], anchor="mm")
    draw.text((WIDTH//2, y + 105), f"平均分位数 {avg_percentile:.0f}% · {opportunity_text}", 
              font=get_font(18), fill=(255, 255, 255, 230), anchor="mm")
    
    # === 数据列表 ===
    y += 145
    draw.text((62, y), "📊 今日股息率数据", font=get_font(24), fill=COLORS['text_dark'])
    y += 15
    
    # 按股息率排序
    sorted_indices = sorted(indices, key=lambda x: x['yield'], reverse=True)
    
    for idx in sorted_indices:
        y += 12
        # 数据行背景
        draw_rounded_rect(draw, (50, y, WIDTH - 50, y + 50), 8, COLORS['white'])
        
        # 名称
        name = idx['name']
        if '沪港深' in name:
            display_name = "🔥 " + name
        elif idx['percentile'] < 30:
            display_name = "💎 " + name
        else:
            display_name = "   " + name
        
        draw.text((65, y + 15), display_name, font=font_medium, fill=COLORS['text_dark'])
        
        # 股息率和分位数
        yield_text = f"{idx['yield']:.2f}%"
        draw.text((WIDTH - 65, y + 12), yield_text, font=font_yield, fill=COLORS['primary'], anchor="rt")
        
        # 分位数颜色
        if idx['percentile'] < 30:
            perc_color = COLORS['green']
            perc_text = f"分位 {idx['percentile']:.0f}%"
        elif idx['percentile'] > 70:
            perc_color = COLORS['red']
            perc_text = f"分位 {idx['percentile']:.0f}%"
        else:
            perc_color = COLORS['text_light']
            perc_text = f"分位 {idx['percentile']:.0f}%"
        
        draw.text((WIDTH - 65, y + 38), perc_text, font=font_small, fill=perc_color, anchor="rt")
        y += 50
    
    # === Footer ===
    y = HEIGHT - 70
    draw.text((WIDTH//2, y), "数据来源：指数公司官方披露", font=get_font(18), fill=COLORS['text_light'], anchor="mm")
    
    return img

def create_cover_2(today_data, history_data):
    """第二张：趋势图 - 近7日股息率变化"""
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    # 字体
    font_title = get_font(42, bold=True)
    
    # === Header ===
    y = 50
    draw.text((WIDTH//2, y), "🍠", font=get_font(50), fill=COLORS['primary'], anchor="mm")
    y += 45
    draw.text((WIDTH//2, y), "红利指数日报", font=font_title, fill=COLORS['primary'], anchor="mm")
    
    # === 趋势图区域 ===
    y += 80
    draw_rounded_rect(draw, (50, y, WIDTH - 50, y + 500), 16, COLORS['white'])
    
    draw.text((62, y + 20), "📈 近7日平均股息率趋势", font=get_font(24), fill=COLORS['text_dark'])
    
    # 绘制趋势图
    if len(history_data) >= 2:
        chart_left = 80
        chart_right = WIDTH - 80
        chart_top = y + 70
        chart_bottom = y + 420
        chart_height = chart_bottom - chart_top
        chart_width = chart_right - chart_left
        
        # 计算每日平均股息率
        avg_yields = []
        dates = []
        for day_data in history_data[-7:]:  # 取最近7天
            indices = day_data['indices']
            avg = sum(i['dividend_yield_2'] for i in indices) / len(indices)
            avg_yields.append(avg)
            dates.append(day_data['date'])
        
        if avg_yields:
            min_yield = min(avg_yields) - 0.2
            max_yield = max(avg_yields) + 0.2
            
            # 绘制坐标轴
            draw.line([(chart_left, chart_bottom), (chart_right, chart_bottom)], 
                     fill=COLORS['text_light'], width=2)
            draw.line([(chart_left, chart_top), (chart_left, chart_bottom)], 
                     fill=COLORS['text_light'], width=2)
            
            # Y轴标签
            y_steps = 5
            for i in range(y_steps + 1):
                val = min_yield + (max_yield - min_yield) * i / y_steps
                y_pos = chart_bottom - (chart_height * i / y_steps)
                draw.text((chart_left - 10, y_pos), f"{val:.1f}%", 
                         font=get_font(14), fill=COLORS['text_light'], anchor="rt")
            
            # 绘制柱状图
            bar_count = len(avg_yields)
            bar_width = chart_width // (bar_count + 1)
            
            for i, (yield_val, date_str) in enumerate(zip(avg_yields, dates)):
                x = chart_left + bar_width * (i + 1)
                
                # 柱子高度
                bar_height = (yield_val - min_yield) / (max_yield - min_yield) * chart_height
                
                # 绘制柱子
                draw_rounded_rect(draw, 
                    (x - 25, chart_bottom - bar_height, x + 25, chart_bottom - 2),
                    4, COLORS['primary'])
                
                # 数值
                draw.text((x, chart_bottom - bar_height - 15), f"{yield_val:.2f}%",
                         font=get_font(14), fill=COLORS['primary'], anchor="mm")
                
                # 日期
                date_label = f"{date_str[4:6]}/{date_str[6:8]}"
                draw.text((x, chart_bottom + 15), date_label,
                         font=get_font(14), fill=COLORS['text_gray'], anchor="mm")
    
    # === 趋势说明 ===
    y += 520
    draw_rounded_rect(draw, (50, y, WIDTH - 50, y + 100), 12, COLORS['light_green_bg'])
    
    # 计算趋势
    if len(avg_yields) >= 2:
        trend = avg_yields[-1] - avg_yields[0]
        if trend > 0:
            trend_text = f"📈 近7日股息率上升 {trend:.2f}%"
            trend_desc = "股息率上升意味着股价下跌，可能是布局好时机"
        else:
            trend_text = f"📉 近7日股息率下降 {abs(trend):.2f}%"
            trend_desc = "股息率下降意味着股价上涨，可考虑逢高减仓"
    else:
        trend_text = "📊 趋势数据不足"
        trend_desc = "需要更多历史数据"
    
    draw.text((62, y + 20), trend_text, font=get_font(20), fill=COLORS['green'])
    draw.text((62, y + 55), trend_desc, font=get_font(18), fill=COLORS['text_dark'])
    
    # === 图例 ===
    y += 120
    draw.text((WIDTH//2, y), "💡 分位数越低 = 股息率相对越高 = 越值得买入", 
              font=get_font(18), fill=COLORS['text_gray'], anchor="mm")
    
    return img

def create_cover_3(today_data):
    """第三张：观点 + 操作建议"""
    img = Image.new('RGB', (WIDTH, HEIGHT), COLORS['bg'])
    draw = ImageDraw.Draw(img)
    
    # 字体
    font_title = get_font(42, bold=True)
    
    # === Header ===
    y = 50
    draw.text((WIDTH//2, y), "🍠", font=get_font(50), fill=COLORS['primary'], anchor="mm")
    y += 45
    draw.text((WIDTH//2, y), "红利指数日报", font=font_title, fill=COLORS['primary'], anchor="mm")
    
    # === 观点区域 ===
    y += 80
    draw_rounded_rect(draw, (50, y, WIDTH - 50, y + 350), 16, COLORS['white'])
    draw.text((62, y + 20), "💡 今日观点", font=get_font(26), fill=COLORS['text_dark'])
    
    # 观点内容
    y_content = y + 60
    
    # 最高股息率
    best_yield = today_data['best_yield']
    draw_rounded_rect(draw, (65, y_content, WIDTH - 65, y_content + 75), 10, COLORS['light_orange_bg'])
    draw.text((80, y_content + 15), "🔥", font=get_font(28), fill=COLORS['primary'])
    draw.text((120, y_content + 18), f"最高股息率：{best_yield['name']}", 
              font=get_font(22), fill=COLORS['primary'])
    draw.text((80, y_content + 50), f"股息率 {best_yield['yield']}% · 分位数 {best_yield['percentile']:.0f}%",
              font=get_font(18), fill=COLORS['text_gray'])
    
    y_content += 90
    
    # 最佳配置
    best_opp = today_data['best_opportunity']
    draw_rounded_rect(draw, (65, y_content, WIDTH - 65, y_content + 75), 10, COLORS['light_green_bg'])
    draw.text((80, y_content + 15), "💎", font=get_font(28), fill=COLORS['green'])
    draw.text((120, y_content + 18), f"最佳配置：{best_opp['name']}", 
              font=get_font(22), fill=COLORS['green'])
    draw.text((80, y_content + 50), f"股息率 {best_opp['yield']}% · 分位数 {best_opp['percentile']:.0f}%（历史低位）",
              font=get_font(18), fill=COLORS['text_gray'])
    
    y_content += 90
    
    # 投资建议
    avg_percentile = sum(i['percentile'] for i in today_data['analysis']) / len(today_data['analysis'])
    if avg_percentile < 30:
        suggest_title = "✅ 建议加仓定投"
        suggest_desc = "当前股息率处于历史低位，是不错的配置时机"
        suggest_color = COLORS['green']
    elif avg_percentile > 70:
        suggest_title = "⏸️ 建议暂停观望"
        suggest_desc = "当前股息率偏高，可等待更好时机"
        suggest_color = COLORS['red']
    else:
        suggest_title = "📊 建议正常定投"
        suggest_desc = "当前处于中等水平，保持正常节奏即可"
        suggest_color = COLORS['primary']
    
    draw_rounded_rect(draw, (65, y_content, WIDTH - 65, y_content + 75), 10, COLORS['white'])
    draw.text((80, y_content + 15), suggest_title, font=get_font(22), fill=suggest_color)
    draw.text((80, y_content + 50), suggest_desc, font=get_font(18), fill=COLORS['text_gray'])
    
    # === 重点提示 ===
    y += 370
    draw_rounded_rect(draw, (50, y, WIDTH - 50, y + 200), 16, COLORS['light_green_bg'])
    draw.text((62, y + 20), "📌 操作建议", font=get_font(22), fill=COLORS['green'])
    
    tips = [
        "• 分位数 < 30%：股息率历史低位，是配置好时机",
        "• 分位数 > 70%：股息率历史高位，可考虑减仓",
        "• 定投策略：坚持长期定投，波动中积累筹码",
        "• 分散配置：可同时配置多只红利指数基金"
    ]
    
    y_tip = y + 55
    for tip in tips:
        draw.text((70, y_tip), tip, font=get_font(18), fill=COLORS['text_dark'])
        y_tip += 35
    
    # === 互动话题 ===
    y += 220
    draw_rounded_rect(draw, (50, y, WIDTH - 50, y + 120), 12, COLORS['light_orange_bg'])
    draw.text((62, y + 20), "💬 今日话题", font=get_font(20), fill=COLORS['primary'])
    draw.text((62, y + 55), "你持有哪只红利指数基金？收益如何？", 
              font=get_font(18), fill=COLORS['text_dark'])
    draw.text((62, y + 85), "评论区分享你的投资经验~", 
              font=get_font(16), fill=COLORS['text_gray'])
    
    # === Footer ===
    y = HEIGHT - 70
    draw.text((WIDTH//2, y), "⚠️ 仅供参考，不构成投资建议", 
              font=get_font(14), fill=COLORS['text_light'], anchor="mm")
    draw.text((WIDTH//2, y + 25), "🍠 红薯条 · 红利投资分析", 
              font=get_font(18), fill=COLORS['primary'], anchor="mm")
    
    return img

def main():
    """主函数"""
    print("📊 加载数据...")
    today_data = load_today_data()
    history_data = load_history_data(7)
    
    print(f"📅 日期: {today_data['date']}")
    print(f"📈 历史数据天数: {len(history_data)}")
    
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 生成三张封面
    print("\n🎨 生成封面图...")
    
    print("  1️⃣ 概览图...")
    img1 = create_cover_1(today_data)
    img1.save(os.path.join(OUTPUT_DIR, "xhs_cover_1.png"))
    
    print("  2️⃣ 趋势图...")
    img2 = create_cover_2(today_data, history_data)
    img2.save(os.path.join(OUTPUT_DIR, "xhs_cover_2.png"))
    
    print("  3️⃣ 观点图...")
    img3 = create_cover_3(today_data)
    img3.save(os.path.join(OUTPUT_DIR, "xhs_cover_3.png"))
    
    print(f"\n✅ 封面图已生成:")
    print(f"   {OUTPUT_DIR}/xhs_cover_1.png")
    print(f"   {OUTPUT_DIR}/xhs_cover_2.png")
    print(f"   {OUTPUT_DIR}/xhs_cover_3.png")

if __name__ == "__main__":
    main()