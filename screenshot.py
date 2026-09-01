from playwright.sync_api import sync_playwright
import time
from bs4 import BeautifulSoup
import re


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
            if len(cells) >= 3:
                station_name = cells[0].get_text(strip=True)
                
                # 检查是否为目标站点
                if station_name in target_stations:
                    observation_time = cells[1].get_text(strip=True)
                    water_level = cells[2].get_text(strip=True)
                    
                    # 组合完整日期时间
                    full_datetime = f"{publish_date} {observation_time}"
                    
                    # 使用字典存储，站名为键，重复的会自动覆盖
                    results[station_name] = {
                        '站名': station_name,
                        '水位': water_level,
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
        
        # 获取前3条新闻链接
        links = page.locator('.newsList li')
        link_count = links.count()
        
        # 只处理前3条或实际存在的链接数
        num_links = min(3, link_count)
        
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
            print(f"站名: {data['站名']}")
            print(f"水位: {data['水位']} 米")
            print(f"时间: {data['时间']}")
            print("-" * 60)
        
        # 等待几秒查看效果
        time.sleep(3)
        
        # 关闭浏览器
        browser.close()


if __name__ == "__main__":
    main()
