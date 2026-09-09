from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime


def load_data():
    """从JSON文件加载历史数据"""
    try:
        with open('water_level_data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []


def save_data(data):
    """保存数据到JSON文件"""
    with open('water_level_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def generate_html_report(data):
    """生成HTML可视化报告"""
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>水位数据可视化报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>
    <style>
        body {{
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            max-width: 1350px;
            min-width: 1350px;
            margin: 0 auto;
            background-color: white;
            padding: 5px 20px;
            border-radius: 10px;
            box-shadow: 2px 2px 3px 3px rgba(0,0,0,0.3);
        }}
        h1 {{
            text-align: center;
            color: #333;
            margin: 0px;
        }}
        .chart-section {{
            margin-bottom: 0px;
        }}
        .chart-container {{
            position: relative;
            height: 400px;
            margin-bottom: 0px;
        }}
        .table-section {{
            margin-top: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: center;
        }}
        th {{
            background-color: #3a71cb;
            color: white;
            font-weight: bold;
            font-size: 18px;
        }}
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        tr:hover {{
            background-color: #f1f1f1;
        }}
        .timestamp {{
            text-align: right;
            color: #666;
            font-size: 14px;
            margin-top: 20px;
        }}
        .status-section {{
            background-color: #f8f9fa;
            padding: 10px 10px;
            border-radius: 10px;
            margin: 10px 0;
            border: 2px solid #ddd;
            display: flex;
            justify-content: flex-start;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }}
        .status-item {{
            align-items: self-end;
        }}
        .status-label {{
            font-size: 20px;
            color: #666;
            font-weight: bold;
        }}
        .status-value {{
            font-size: 40px;
            font-weight: bold;
        }}
        .warningStatus-value {{
            font-size: 28px;
            font-weight: bold;
            color: red;
        }}
        .status-red {{
            color: red;
        }}
        .status-blue {{
            color: #007bff;
        }}
        .image-section {{
            max-width: 90%;
            margin: 0px auto;
            text-align: center;
            position: relative;
            border-radius: 10px;
            box-shadow: 2px 2px 2px 2px rgba(0,0,0,0.3);
        }}
        .image-section img {{
            max-width: 100%;
            height: auto;
            display: block;
            border-radius: 10px;
            margin: 0 auto;
        }}
        .image-overlay-text {{
            transform: translateX(-50%);
            font-size: 250%;
            font-weight: bold;
            z-index: 10;
            white-space: nowrap;
        }}
        .wz {{
            position: absolute;
            top: 52%;
            left: 92.5%;
        }}
        .jk {{
            position: absolute;
            top: 52%;
            left: 68%;  
        }}
        .wx {{
            position: absolute;
            top: 10%;
            left: 40%;
        }}
        .lb {{
            position: absolute;
            top: 10%;
            left: 11%;
        }}
        .lc {{
            position: absolute;
            top: 55%;
            left: 13%;
        }}
        .gg {{
            position: absolute;
            top: 55%;
            left: 47%;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>西江流域水位数据可视化报告</h1>
        
        <div class="chart-section">
            <div class="chart-container">
                <canvas id="waterLevelChart"></canvas>
            </div>
        </div>
"""

    # 按时间排序数据
    sorted_data = sorted(data, key=lambda x: x['时间'])

    # 测试输出
    #print(sorted_data)

    # 获取最新数据的上游状态、所有站点状态
    if sorted_data:
        latest_upstream_color = sorted_data[-1].get('上游情况', {}).get('颜色', 'blue')
        latest_upstream_desc = sorted_data[-1].get('上游情况', {}).get('描述', '暂无数据')
        latest_upstream_change = sorted_data[-1].get('上游情况', {}).get('总变化和', '0')

        latest_wuzhou_color = sorted_data[-1].get('站点数据',{}).get('梧州', {}).get('颜色', 'blue')
        latest_wuzhou_desc = sorted_data[-1].get('站点数据',{}).get('梧州', {}).get('情况', '暂无数据')
        latest_wuzhou_data = sorted_data[-1].get('站点数据',{}).get('梧州', {}).get('水位', '0')
        latest_wuzhou_change = sorted_data[-1].get('站点数据',{}).get('梧州', {}).get('变化值', '0')

        latest_jiangkou_color = sorted_data[-1].get('站点数据',{}).get('江口', {}).get('颜色', 'blue')
        latest_jiangkou_desc = sorted_data[-1].get('站点数据',{}).get('江口', {}).get('情况', '暂无数据')
        latest_jiangkou_data = sorted_data[-1].get('站点数据',{}).get('江口', {}).get('水位', '0')
        latest_jiangkou_change = sorted_data[-1].get('站点数据',{}).get('江口', {}).get('变化值', '0')

        latest_wuxuan_color = sorted_data[-1].get('站点数据',{}).get('武宣', {}).get('颜色', 'blue')
        latest_wuxuan_desc = sorted_data[-1].get('站点数据',{}).get('武宣', {}).get('情况', '暂无数据')
        latest_wuxuan_data = sorted_data[-1].get('站点数据',{}).get('武宣', {}).get('水位', '0')
        latest_wuxuan_change = sorted_data[-1].get('站点数据',{}).get('武宣', {}).get('变化值', '0')

        latest_laibing_color = sorted_data[-1].get('站点数据',{}).get('来宾', {}).get('颜色', 'blue')
        latest_laibing_desc = sorted_data[-1].get('站点数据',{}).get('来宾', {}).get('情况', '暂无数据')
        latest_laibing_data = sorted_data[-1].get('站点数据',{}).get('来宾', {}).get('水位', '0')
        latest_laibing_change = sorted_data[-1].get('站点数据',{}).get('来宾', {}).get('变化值', '0')

        latest_luancheng_color = sorted_data[-1].get('站点数据',{}).get('峦城', {}).get('颜色', 'blue')
        latest_luancheng_desc = sorted_data[-1].get('站点数据',{}).get('峦城', {}).get('情况', '暂无数据')
        latest_luancheng_data = sorted_data[-1].get('站点数据',{}).get('峦城', {}).get('水位', '0')
        latest_luancheng_change = sorted_data[-1].get('站点数据',{}).get('峦城', {}).get('变化值', '0')

        latest_guigang_color = sorted_data[-1].get('站点数据',{}).get('贵港', {}).get('颜色', 'blue')
        latest_guigang_desc = sorted_data[-1].get('站点数据',{}).get('贵港', {}).get('情况', '暂无数据')
        latest_guigang_data = sorted_data[-1].get('站点数据',{}).get('贵港', {}).get('水位', '0')
        latest_guigang_change = sorted_data[-1].get('站点数据',{}).get('贵港', {}).get('变化值', '0')

        latest_datengxia_data = sorted_data[-1].get('枢纽数据',{}).get('大藤峡枢纽', {}).get('上游水位', '0')
        latest_datengxia_fs = sorted_data[-1].get('枢纽数据',{}).get('大藤峡枢纽', {}).get('是否放水', '0')

        latest_guiping_data = sorted_data[-1].get('枢纽数据',{}).get('桂平船闸', {}).get('上游水位', '0')
        latest_guiping_fs = sorted_data[-1].get('枢纽数据',{}).get('桂平船闸', {}).get('是否放水', '0')

        latest_changzhou_data = sorted_data[-1].get('枢纽数据',{}).get('长洲船闸', {}).get('上游水位', '0')
        latest_changzhou_fs = sorted_data[-1].get('枢纽数据',{}).get('长洲船闸', {}).get('是否放水', '0')

    #计算预报值 如果变化幅度过小就上下略微波动 否则梧州预计变化值在上游最新总变化值0.35到0.65之间
    latest_wuzhou_data_float = float(latest_wuzhou_data)  # 转换为浮点数
    if latest_upstream_change <= 0.5 and latest_upstream_change >= -0.5:
        latest_wuzhou_p1 = format(latest_wuzhou_data_float - latest_upstream_change*0.9, '.2f')
        latest_wuzhou_p2 = format(latest_wuzhou_data_float + latest_upstream_change*0.9, '.2f')
    else:
        latest_wuzhou_p1 = format(latest_wuzhou_data_float + latest_upstream_change*0.35, '.2f')
        latest_wuzhou_p2 = format(latest_wuzhou_data_float + latest_upstream_change*0.65, '.2f')

    # 计算预报颜色样式 如果上游变化幅度过小或水位下降就用蓝色 否则用红色
    if latest_upstream_change <= 0.5:
        latest_wuzhou_pColor = 'blue'
    else:
        latest_wuzhou_pColor = 'red'

    #计算预报程度描述 如果上游变化幅度绝对值小于0.5为“变化不大”，绝对值在0.5和2直接为“略微”，绝对值在2和4直接为“明显”，绝对值大于4为“大幅”
    if abs(latest_upstream_change) < 0.5:
        latest_wuzhou_pDesc = '变化不大 '
        latest_upstream_des = '微微'
    elif abs(latest_upstream_change) < 2:
        latest_wuzhou_pDesc = '略微'
        latest_upstream_des = '略微'
    elif abs(latest_upstream_change) < 4:
        latest_wuzhou_pDesc = '明显'
        latest_upstream_des = '明显'
    else:
        latest_wuzhou_pDesc = '大幅'
        latest_upstream_des = '大幅'

    #计算预报上升或下降，如果上游变化幅度大于0.5为“上升”，小于-0.5为“下降”，否则为“小幅波动”
    if latest_upstream_change > 0.5:
        latest_wuzhou_pDirection = '上升'
    elif latest_upstream_change < -0.5:
        latest_wuzhou_pDirection = '下降'
    else:
        latest_wuzhou_pDirection = '上下小幅波动'

    #计算预报情况符号，如果上游变化幅度在0.5和2之间用↗︎，在2和4之间用▲，在4以上用⏫︎；如果上游变化幅度在-0.5和-2之间用↘︎，在-2和-4之间用▼，在-4以上用⏬︎，否则用〰︎
    if latest_upstream_change > 0.5 and latest_upstream_change < 2:
        latest_wuzhou_pSymbol = '↗︎'
        latest_upstream_Symbol = '↗︎'
    elif latest_upstream_change > 2 and latest_upstream_change < 4:
        latest_wuzhou_pSymbol = '▲'
        latest_upstream_Symbol = '▲'
    elif latest_upstream_change > 4:
        latest_wuzhou_pSymbol = '⏫︎'
        latest_upstream_Symbol = '⏫︎'
    elif latest_upstream_change < -0.5 and latest_upstream_change > -2:
        latest_wuzhou_pSymbol = '↘︎'
        latest_upstream_Symbol = '↘︎'
    elif latest_upstream_change < -2 and latest_upstream_change > -4:
        latest_wuzhou_pSymbol = '▼'
        latest_upstream_Symbol = '▼'
    elif latest_upstream_change < -4:
        latest_wuzhou_pSymbol = '⏬︎'
        latest_upstream_Symbol = '⏬︎'
    elif latest_upstream_change > 0 and latest_upstream_change <= 0.5:
        latest_upstream_Symbol = '↗︎'
        latest_wuzhou_pSymbol = '  '
    elif latest_upstream_change < 0 and latest_upstream_change >= -0.5:
        latest_upstream_Symbol = '↘︎'
        latest_wuzhou_pSymbol = '  '
    else:
        latest_wuzhou_pSymbol = '  '

    #站点告警文字
    station_warning = ' '

    #站点是否需要警告符号
    latest_wuzhou_wSymbol = ' '
    latest_jiangkou_wSymbol = ' '
    latest_wuxuan_wSymbol = ' '
    latest_laibing_wSymbol = ' '
    latest_luancheng_wSymbol = ' '
    latest_guigang_wSymbol = ' '

    #站点是否需要超警戒线警告
    s1 = 0
    if float(latest_wuzhou_data) >= 18.5:
        latest_wuzhou_wSymbol = '🚨'
        station_warning += '梧州'
        s1 = 1

    if float(latest_jiangkou_data) >= 31.7:
        latest_jiangkou_wSymbol = '🚨'
        if s1 != 0:
            station_warning += '、'
        station_warning += '江口'
        s1 = 1

    if float(latest_guigang_data) >= 41.2:
        latest_guigang_wSymbol = '🚨'
        if s1 != 0:
            station_warning += '、'
        station_warning += '贵港'
        s1 = 1

    if float(latest_luancheng_data) >= 64.2:
        latest_luancheng_wSymbol = '🚨'
        if s1 != 0:
            station_warning += '、'
        station_warning += '峦城'
        s1 = 1

    if float(latest_wuxuan_data) >= 61.4:
        latest_wuxuan_wSymbol = '🚨'
        if s1 != 0:
            station_warning += '、'
        station_warning += '武宣'
        s1 = 1

    if float(latest_laibing_data) >= 62:
        latest_laibing_wSymbol = '🚨'
        if s1 != 0:
            station_warning += '、'
        station_warning += '来宾'
        s1 = 1

    if s1 != 0:
        station_warning += '水位超警！'


    if float(latest_wuzhou_data) >= 12 and float(latest_wuzhou_data) < 18.5:
        latest_wuzhou_wSymbol = '⚠️'
        station_warning += '梧州水位较高，'

    if float(latest_jiangkou_data) >= 26 and float(latest_jiangkou_data) < 31.7:
        latest_jiangkou_wSymbol = '⚠️'
        station_warning += '江口水位较高，'

    #站点是否需要水位快速上涨警告
    s3 = 0
    if float(latest_wuzhou_change) > 2:
        latest_wuzhou_wSymbol = '🚨'
        station_warning += '梧州'
        s3 = 1

    if float(latest_jiangkou_change) > 2:
        latest_jiangkou_wSymbol = '🚨'
        if s3 != 0:
            station_warning += '、'
        station_warning += '江口'
        s3 = 1

    if float(latest_wuxuan_change) > 2:
        latest_wuxuan_wSymbol = '🚨'
        if s3 != 0:
            station_warning += '、'
        station_warning += '武宣'
        s3 = 1

    if float(latest_laibing_change) > 2:
        latest_laibing_wSymbol = '🚨'
        if s3 != 0:
            station_warning += '、'
        station_warning += '来宾'
        s3 = 1

    if float(latest_luancheng_change) > 2:
        latest_luancheng_wSymbol = '🚨'
        if s3 != 0:
            station_warning += '、'
        station_warning += '峦城'
        s3 = 1

    if float(latest_guigang_change) > 2:
        latest_guigang_wSymbol = '🚨'
        if s3 != 0:
            station_warning += '、'
        station_warning += '贵港'
        s3 = 1

    if s3 != 0:
        station_warning += '水位快速上涨！'

    if station_warning != ' ':
        station_warning += '请及时注意水位变化，加强船舶调度！'

    #水库预警文字
    reservoir_warning = ' '

    latest_datengxia_wSymbol = ' '
    latest_guiping_wSymbol = ' '
    latest_changzhou_wSymbol = ' '
    latest_datengxia_color = 'blue'
    latest_guiping_color = 'blue'
    latest_changzhou_color = 'blue'
 
    #水库是否需要开闸预警
    r2 = 0
    if float(latest_datengxia_fs) == 1:
        latest_datengxia_wSymbol += '🌊'
        reservoir_warning += '大藤峡枢纽'
        r2 = 1
    if float(latest_guiping_fs) == 1:
        latest_guiping_wSymbol += '🌊'
        if r2 != 0:
            reservoir_warning += '、'
        reservoir_warning += '桂平枢纽'
        r2 = 1
    if float(latest_changzhou_fs) == 1:
        latest_changzhou_wSymbol += '🌊'
        if r2 != 0:
            reservoir_warning += '、'
        reservoir_warning += '长洲枢纽'
        r2 = 1
    if r2 != 0:
        reservoir_warning += '出库流量更大，可能正在放水。'

     #水库是否需要水位警告符号
    r1 = 0
    if float(latest_datengxia_data) >= 60:
        latest_datengxia_wSymbol += '🚨'
        reservoir_warning += '大藤峡枢纽'
        latest_datengxia_color = 'red'
        r1 = 1
    if float(latest_guiping_data) >= 31.5:
        latest_guiping_wSymbol += '🚨'
        if r1 != 0:
            reservoir_warning += '、'
        reservoir_warning += '桂平枢纽'
        latest_guiping_color = 'red'
        r1 = 1
    if float(latest_changzhou_data) >= 30:
        latest_changzhou_wSymbol += '🚨'
        if r1 != 0:
            reservoir_warning += '、'
        reservoir_warning += '长洲枢纽'
        latest_changzhou_color = 'red'
        r1 = 1
    if r1 != 0:
        reservoir_warning += '水位高，可能开闸放水！'

    if latest_datengxia_wSymbol == ' ':
        latest_datengxia_wSymbol += '正常'

    if latest_guiping_wSymbol == ' ':
        latest_guiping_wSymbol += '正常'

    if latest_changzhou_wSymbol == ' ':
        latest_changzhou_wSymbol += '正常'
    
    if reservoir_warning != ' ':
        reservoir_warning += '请及时注意水位变化，加强船舶调度！'
    
    # 添加状态显示区域
    html_content += f"""
        
        <div class="status-section">
            <div class="status-item">
                <span class="status-label">上游整体情况：</span>
                <span class="status-value status-{latest_upstream_color}">
                    水位{latest_upstream_des}{latest_upstream_desc}
                </span>
            </div>
            <div class="status-item">
                <span class="status-label">今日梧州水位：</span>
                <span class="status-value status-{latest_wuzhou_color}">
                    {latest_wuzhou_data}m{latest_wuzhou_desc}
                </span>
            </div>
            <div class="status-item">
                <span class="status-label">近2天梧州水位预报：</span>
                <span class="status-value status-{latest_wuzhou_pColor}">
                    {latest_wuzhou_p1}m~{latest_wuzhou_p2}m 预计水位{latest_wuzhou_pDesc}{latest_wuzhou_pDirection}{latest_wuzhou_pSymbol}  
                </span>
            </div>
        </div>
        <div class="status-section">
            <div class="status-item">
                <span class="status-label">🚨水库预警：</span>
                <span class="warningStatus-value">
                    {reservoir_warning}
                </span>
            </div>
            <div class="status-item">
                <span class="status-label">🚨站点预警：</span>
                <span class="warningStatus-value">
                    {station_warning}
                </span>
            </div>
        </div>
        
        <div class="image-section">
            <div class="image-overlay-text wz status-{latest_wuzhou_color}">{latest_wuzhou_data}m{latest_wuzhou_desc}</div>
            <div class="image-overlay-text status-{latest_wuzhou_color}" style="position: absolute;top: 41.25%;left: 86.7%;">====</div>
            <div class="image-overlay-text jk status-{latest_jiangkou_color}">{latest_jiangkou_data}m{latest_jiangkou_desc}</div>
            <div class="image-overlay-text status-{latest_jiangkou_color}" style="position: absolute; top: 41.4%; left: 64%;">==</div>
            <div class="image-overlay-text wx status-{latest_wuxuan_color}">{latest_wuxuan_data}m{latest_wuxuan_desc}</div>
            <div class="image-overlay-text status-{latest_wuxuan_color}" style="position: absolute; top: 18.9%; left: 23.2%;">===========</div>
            <div class="image-overlay-text lb status-{latest_laibing_color}">{latest_laibing_data}m{latest_laibing_desc}</div>
            <div class="image-overlay-text status-{latest_laibing_color}" style="position: absolute; top: 18.9%; left: 4%;">===</div>
            <div class="image-overlay-text lc status-{latest_luancheng_color}">{latest_luancheng_data}m{latest_luancheng_desc}</div>
            <div class="image-overlay-text status-{latest_luancheng_color}" style="position: absolute; top: 63.8%; left: 6%;">====</div>
            <div class="image-overlay-text gg status-{latest_guigang_color}">{latest_guigang_data}m{latest_guigang_desc}</div>
            <div class="image-overlay-text status-{latest_guigang_color}" style="position: absolute; top: 63.8%; left: 28.5%;">============</div>
            <div class="image-overlay-text" style="position: absolute; top: 42.5%; left: 86.5%;font-size:200%">{latest_wuzhou_wSymbol}</div>
            <div class="image-overlay-text" style="position: absolute; top: 42.5%; left: 69.67%;font-size:200%">{latest_jiangkou_wSymbol}</div>
            <div class="image-overlay-text" style="position: absolute; top: 20%; left: 37.9%;font-size:200%">{latest_wuxuan_wSymbol}</div>
            <div class="image-overlay-text" style="position: absolute; top: 20%; left: 8.6%;font-size:200%">{latest_laibing_wSymbol}</div>
            <div class="image-overlay-text" style="position: absolute; top: 65%; left: 12%;font-size:200%">{latest_luancheng_wSymbol}</div>
            <div class="image-overlay-text" style="position: absolute; top: 65%; left: 45%;font-size:200%">{latest_guigang_wSymbol}</div>
            <div class="image-overlay-text" style="position: absolute;top: 17%;left: 53.75%;font-size: 180%;writing-mode: vertical-rl;text-orientation: mixed;justify-content: center;align-items: center;display: flex;height: 20%;color:blue">{latest_datengxia_wSymbol}</div>
            <div class="image-overlay-text" style="position: absolute; top: 59.9%;left: 56.1%;font-size: 180%;writing-mode: vertical-rl;text-orientation: mixed;justify-content: center;align-items: center;display: flex;height: 20%;color:blue">{latest_guiping_wSymbol}</div>
            <div class="image-overlay-text" style="position: absolute; top: 39%; left: 79%;font-size: 180%;writing-mode: vertical-rl;text-orientation: mixed;justify-content: center;align-items: center;display: flex; height: 20%;color:blue">{latest_changzhou_wSymbol}</div>
            <div class="image-overlay-text status-{latest_datengxia_color}" style="position: absolute;top: -0.5%;left: 53.8%;font-size: 180%;">{latest_datengxia_data}m</div>
            <div class="image-overlay-text status-{latest_guiping_color}" style="position: absolute;top: 88%;left: 56%;font-size: 180%;">{latest_guiping_data}m</div>
            <div class="image-overlay-text status-{latest_changzhou_color}" style="position: absolute;top: 3%;left: 79%;font-size: 180%;">{latest_changzhou_data}m</div>
            <img src="river.jpg" alt="西江流域图">
        </div>
        
        <div class="table-section">
            <h2>历史数据总表</h2>
            <table>
                <thead>
                    <tr>
                        <th>时间</th>
                        <th>梧州</th>
                        <th>江口</th>
                        <th>贵港</th>
                        <th>武宣</th>
                        <th>来宾</th>
                        <th>峦城</th>
                    </tr>
                </thead>
                <tbody>
"""

    # 添加表格数据
    for record in sorted_data:
        station_data = record.get('站点数据', {})
        html_content += f"""
                    <tr>
                        <td>{record['时间']}</td>
                        <td>{station_data.get('梧州', {}).get('水位', '-')}{station_data.get('梧州', {}).get('情况', ' ')}</td>
                        <td>{station_data.get('江口', {}).get('水位', '-')}{station_data.get('江口', {}).get('情况', ' ')}</td>
                        <td>{station_data.get('贵港', {}).get('水位', '-')}{station_data.get('贵港', {}).get('情况', ' ')}</td>
                        <td>{station_data.get('武宣', {}).get('水位', '-')}{station_data.get('武宣', {}).get('情况', ' ')}</td>
                        <td>{station_data.get('来宾', {}).get('水位', '-')}{station_data.get('来宾', {}).get('情况', ' ')}</td>
                        <td>{station_data.get('峦城', {}).get('水位', '-')}{station_data.get('峦城', {}).get('情况', ' ')}</td>
                    </tr>
"""

    # 准备图表数据
    labels = [record['时间'] for record in sorted_data]
    stations = ['梧州', '江口', '贵港', '武宣', '来宾', '峦城']
    colors = [
        'rgb(255, 99, 132)',
        'rgb(54, 162, 235)',
        'rgb(255, 205, 86)',
        'rgb(75, 192, 192)',
        'rgb(153, 102, 255)',
        'rgb(255, 159, 64)'
    ]

    datasets = []
    for i, station in enumerate(stations):
        water_levels = []
        for record in sorted_data:
            station_data = record.get('站点数据', {})
            water_level = station_data.get(station, {}).get('水位', 0)
            # 尝试转换为浮点数，如果失败则使用0
            try:
                water_levels.append(float(water_level))
            except (ValueError, TypeError):
                water_levels.append(0)
        
        datasets.append(f"""
                {{
                    label: '{station}',
                    data: {water_levels},
                    borderColor: '{colors[i]}',
                    backgroundColor: '{colors[i]}',
                    tension: 0.1,
                    fill: false
                }}""")

    html_content += f"""
                </tbody>
            </table>
        </div>
        
        <div class="timestamp">
            报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            数据记录数: {len(data)} 条
        </div>
    </div>
    
    <script>
        const ctx = document.getElementById('waterLevelChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {json.dumps(labels)},
                datasets: [{','.join(datasets)}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: '各站点水位变化趋势图',
                        font: {{
                            size: 18
                        }}
                    }},
                    legend: {{
                        position: 'top'
                    }}
                }},
                scales: {{
                    y: {{
                        title: {{
                            display: true,
                            text: '水位 (米)'
                        }}
                    }},
                    x: {{
                        title: {{
                            display: true,
                            text: '时间'
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

    with open('water_level_report.html', 'w', encoding='utf-8') as f:
        f.write(html_content)


def parse_water_level_data(html_content, publish_date):
    """解析水位数据"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 目标站点
    target_stations = ['梧州', '江口', '贵港', '武宣', '来宾', '峦城']
    
    # 查找所有表格
    tables = soup.find_all('table')
    
    results = {}
    
    for table in tables:
        rows = table.find_all('tr')
        
        # 跳过表头行
        for row in rows[3:]:  # 前3行是表头
            cells = row.find_all('td')
            if len(cells) >= 4:
                station_name = cells[0].get_text(strip=True)
                
                # 检查是否为目标站点
                if station_name in target_stations:
                    observation_time = cells[1].get_text(strip=True)
                    water_level = cells[2].get_text(strip=True)
                    change_value = cells[3].get_text(strip=True)
                    
                    # 将变化值转换为数字：1表示上升，0表示持平或下降
                    try:
                        change_num = float(change_value)
                        if change_num > 0 and change_num < 2:
                            change_value_num = 1  # 上升
                            change_des = "▲"
                            color = "red"
                        elif change_num >= 2:
                            change_value_num = 0  # 大幅上升
                            change_des = "⏫︎"
                            color = "red"
                        elif change_num <= 0 and change_num > -2:
                            change_value_num = 0  # 持平或下降
                            change_des = "▼"
                            color = "blue"
                        else:
                            change_value_num <= -2# 大幅下降
                            change_des = "⏬︎"
                            color = "blue"
                    except (ValueError, TypeError):
                        change_value_num = 0  # 无法解析时默认为0
                    
                    # 组合完整日期时间
                    full_datetime = f"{publish_date} {observation_time}"
                    
                    # 使用字典存储，站名为键，重复的会自动覆盖
                    results[station_name] = {
                        '站名': station_name,
                        '水位': water_level,
                        '变化值': change_value,
                        '变化': change_value_num,
                        '情况': change_des,
                        '颜色': color,
                        '时间': full_datetime
                    }
    
    return results


def parse_reservoir_data(html_content, publish_date):
    """解析水库/船闸数据"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 目标枢纽
    target_reservoirs = ['大藤峡枢纽', '桂平船闸', '长洲船闸']
    
    # 查找所有表格
    tables = soup.find_all('table')
    
    results = {}
    
    for table in tables:
        rows = table.find_all('tr')
        
        # 寻找通航建筑物流量信息表
        table_found = False
        for row_index, row in enumerate(rows):
            cells = row.find_all('td')
            if len(cells) >= 1 and '通航建筑物流量信息表' in cells[0].get_text():
                # 找到了正确的表格，从该行开始解析数据（跳过表头行）
                table_found = True
                # 从表头之后开始解析数据行
                for data_row in rows[row_index + 1:]:  # 跳过表头和可能的第二行表头
                    data_cells = data_row.find_all('td')
                    if len(data_cells) >= 6:
                        reservoir_name = data_cells[0].get_text(strip=True)
                        
                        # 检查是否为目标枢纽
                        if reservoir_name in target_reservoirs:
                            observation_time = data_cells[1].get_text(strip=True)
                            upstream_level = data_cells[2].get_text(strip=True)
                            downstream_level = data_cells[3].get_text(strip=True)
                            inflow = data_cells[4].get_text(strip=True)
                            outflow = data_cells[5].get_text(strip=True)
                            
                            # 计算是否放水：出库流量 >= 入库流量则为1，否则为0
                            try:
                                inflow_float = float(inflow)
                                outflow_float = float(outflow)
                                is_releasing = 1 if outflow_float >= inflow_float else 0
                            except (ValueError, TypeError):
                                is_releasing = 0
                            
                            # 组合完整日期时间
                            full_datetime = f"{publish_date} {observation_time}"
                            
                            # 使用字典存储，站名为键，重复的会自动覆盖
                            results[reservoir_name] = {
                                '站名': reservoir_name,
                                '时间': full_datetime,
                                '上游水位': upstream_level,
                                '入库流量': inflow,
                                '出库流量': outflow,
                                '是否放水': is_releasing
                            }
                break
        if table_found:
            break  # 找到表格后就停止搜索其他表格
    
    return results


def main():
    import sys
    import os
    import shutil

    # 打包后的exe处理chromium路径
    if getattr(sys, 'frozen', False):
        # 打包后的exe
        base_path = sys._MEIPASS
        packed_chromium = os.path.join(base_path, 'ms-playwright', 'chromium-1234')

        # Playwright期望的chromium路径
        temp_dir = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'ms-playwright')
        target_chromium = os.path.join(temp_dir, 'chromium-1234')

        # 如果打包了chromium，且目标位置不存在，则复制过去
        if os.path.exists(packed_chromium) and not os.path.exists(target_chromium):
            print("正在复制chromium浏览器驱动...")
            try:
                os.makedirs(temp_dir, exist_ok=True)
                shutil.copytree(packed_chromium, target_chromium)
                print("chromium浏览器驱动复制完成！")
            except Exception as e:
                print(f"复制chromium失败: {e}")

        # 设置Playwright浏览器路径
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = temp_dir

    with sync_playwright() as p:
        # 启动浏览器，headless=False 表示浏览器窗口可见
        browser = p.chromium.launch(headless=False)
        
        # 创建浏览器上下文
        context = browser.new_context()
        
        # 创建页面
        page = context.new_page()
        
        # 访问目标网站
        print("正在打开网站...")
        page.goto("https://www.gxghj.cn/c/fw/slcx")
        
        # 等待页面加载完成
        print("等待页面加载...")
        page.wait_for_load_state("networkidle")
        
        # 截图保存列表页
        screenshot_path = "screenshot_list.png"
        page.screenshot(path=screenshot_path)
        print(f"列表页截图已保存到: {screenshot_path}")
        
        # 获取前4条新闻链接
        links = page.locator('.newsList li')
        link_count = links.count()
        
        # 只处理前4条或实际存在的链接数
        num_links = min(4, link_count)
        
        # 使用字典存储所有数据，站名为键
        all_water_data = {}
        
        # 使用字典存储水库数据，枢纽名为键
        all_reservoir_data = {}
        
        for i in range(num_links):
            # 重新获取列表（避免stale element）
            current_links = page.locator('.newsList li')
            link = current_links.nth(i)
            
            # 获取链接标题
            link_title = link.locator('.newsTitle').inner_text()
            print(f"\n{'='*50}")
            print(f"正在处理第 {i+1} 条链接: {link_title}")
            print(f"{'='*50}")
            
            # 点击链接
            link.locator('a').click()
            
            # 等待详情页加载完成
            print("等待详情页加载...")
            page.wait_for_load_state("networkidle")
            
            # 截图保存详情页
            screenshot_detail_path = f"screenshot_detail_{i+1}.png"
            page.screenshot(path=screenshot_detail_path)
            print(f"详情页截图已保存到: {screenshot_detail_path}")
            
            # 获取发布日期
            publish_date_info = page.locator('.info').inner_text()
            date_match = re.search(r'发布日期：(\d{4}-\d{2}-\d{2})', publish_date_info)
            if date_match:
                publish_date = date_match.group(1)
            else:
                publish_date = "未知日期"
            
            # 获取页面HTML内容
            page_html = page.content()
            
            # 解析水位数据
            water_data = parse_water_level_data(page_html, publish_date)
            # 合并到总数据中，重复站点会自动覆盖
            all_water_data.update(water_data)
            
            # 解析水库/船闸数据
            reservoir_data = parse_reservoir_data(page_html, publish_date)
            # 合并到水库数据中，重复枢纽会自动覆盖
            all_reservoir_data.update(reservoir_data)
            
            # 返回列表页
            print("返回列表页...")
            page.goto("https://www.gxghj.cn/c/fw/slcx")
            page.wait_for_load_state("networkidle")
            
            time.sleep(1)
        
        # 输出所有爬取的数据
        print("\n\n")
        print("=" * 60)
        print("所有水位数据汇总")
        print("=" * 60)
        
        for station_name in sorted(all_water_data.keys()):
            data = all_water_data[station_name]
            change_desc = "上升" if data['变化'] == 1 else "持平或下降"
            print(f"站名: {data['站名']}")
            print(f"水位: {data['水位']} 米")
            print(f"变化: {data['变化']} ({change_desc})")
            print(f"变化值: {data['变化值']}")
            print(f"情况: {data['情况']}")
            print(f"颜色: {data['颜色']}")
            print(f"时间: {data['时间']}")
            print("-" * 60)
        
        # 输出所有爬取的水库数据
        print("\n\n")
        print("=" * 60)
        print("水库/船闸数据汇总")
        print("=" * 60)
        
        for reservoir_name in sorted(all_reservoir_data.keys()):
            data = all_reservoir_data[reservoir_name]
            releasing_status = "放水中" if data['是否放水'] == 1 else "未放水"
            print(f"站名: {data['站名']}")
            print(f"时间: {data['时间']}")
            print(f"上游水位: {data['上游水位']} 米")
            print(f"入库流量: {data['入库流量']} m³/s")
            print(f"出库流量: {data['出库流量']} m³/s")
            print(f"是否放水: {data['是否放水']} ({releasing_status})")
            print("-" * 60)
        
        # 加载历史数据
        print("\n正在加载历史数据...")
        historical_data = load_data()
        
        # 检查是否已存在相同时间的数据
        new_data_time = list(all_water_data.values())[0]['时间'] if all_water_data else None
        existing_index = -1
        if new_data_time:
            for i, record in enumerate(historical_data):
                if record['时间'] == new_data_time:
                    existing_index = i
                    break
        
        # 添加或更新数据
        if new_data_time:
            # 计算上游整体情况（来宾、武宣、贵港、峦城、江口）
            upstream_stations = ['来宾', '武宣', '贵港', '峦城', '江口']
            upstream_change_sum = 0
            up_change_value_sum = 0
            for station in upstream_stations:
                if station in all_water_data:
                    upstream_change_sum += all_water_data[station]['变化']
                    up_change_value_sum += float(all_water_data[station]['变化值'])

            
            # 根据上游变化和值决定整体情况
            if upstream_change_sum == 0:
                upstream_status = "下降⏬︎"
                upstream_color = "blue"
            elif upstream_change_sum == 1:
                upstream_status = "下降▼"
                upstream_color = "blue"
            elif upstream_change_sum == 2:
                upstream_status = "上升↗︎"
                upstream_color = "red"
            elif upstream_change_sum == 3:
                upstream_status = "上升▲"
                upstream_color = "red"
            else:  # 4或5
                upstream_status = "上升⏫︎"
                upstream_color = "red"
            
            record_data = {
                '时间': new_data_time,
                '站点数据': all_water_data,
                '枢纽数据': all_reservoir_data,
                '上游情况': {
                    '描述': upstream_status,
                    '颜色': upstream_color,
                    '变化和': upstream_change_sum,
                    '总变化和': up_change_value_sum
                }
            }
            
            print(f"\n上游整体情况: {upstream_status} 变化和: {upstream_change_sum} 总变化和: {up_change_value_sum}")
            
            if existing_index >= 0:
                print(f"更新时间 {new_data_time} 的数据")
                historical_data[existing_index] = record_data
            else:
                print(f"添加新的时间数据: {new_data_time}")
                historical_data.append(record_data)
        
        # 保存数据
        save_data(historical_data)
        print(f"数据已保存，当前共有 {len(historical_data)} 条记录")
        
        # 生成HTML报告
        print("\n正在生成HTML可视化报告...")
        generate_html_report(historical_data)
        print("报告已生成: water_level_report.html")
        
        # 等待几秒查看效果
        time.sleep(3)
        
        # 关闭浏览器
        browser.close()


if __name__ == "__main__":
    main()
