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
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }}
        .chart-section {{
            margin-bottom: 40px;
        }}
        .chart-container {{
            position: relative;
            height: 400px;
            margin-bottom: 30px;
        }}
        .table-section {{
            margin-top: 40px;
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
            background-color: #4CAF50;
            color: white;
            font-weight: bold;
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

    # 按时间排序数据
    sorted_data = sorted(data, key=lambda x: x['时间'])

    # 添加表格数据
    for record in sorted_data:
        station_data = record.get('站点数据', {})
        html_content += f"""
                    <tr>
                        <td>{record['时间']}</td>
                        <td>{station_data.get('梧州', {}).get('水位', '-')}</td>
                        <td>{station_data.get('江口', {}).get('水位', '-')}</td>
                        <td>{station_data.get('贵港', {}).get('水位', '-')}</td>
                        <td>{station_data.get('武宣', {}).get('水位', '-')}</td>
                        <td>{station_data.get('来宾', {}).get('水位', '-')}</td>
                        <td>{station_data.get('峦城', {}).get('水位', '-')}</td>
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
                        if change_num > 0:
                            change_value_num = 1  # 上升
                        else:
                            change_value_num = 0  # 持平或下降
                    except (ValueError, TypeError):
                        change_value_num = 0  # 无法解析时默认为0
                    
                    # 组合完整日期时间
                    full_datetime = f"{publish_date} {observation_time}"
                    
                    # 使用字典存储，站名为键，重复的会自动覆盖
                    results[station_name] = {
                        '站名': station_name,
                        '水位': water_level,
                        '变化': change_value_num,
                        '时间': full_datetime
                    }
    
    return results


def main():
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
        
        # 只处理前3条或实际存在的链接数
        num_links = min(4, link_count)
        
        # 使用字典存储所有数据，站名为键
        all_water_data = {}
        
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
            print(f"时间: {data['时间']}")
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
            record_data = {
                '时间': new_data_time,
                '站点数据': all_water_data
            }
            
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
