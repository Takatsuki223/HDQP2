# 水文数据查询程序2（Hydrological data query program2）
一个基于**Python + Playwright + BeautifulSoup + ECharts**的便携化河道水位数据爬取与可视化展示分析程序。  
供**梧州仓码**同事使用，快速查询梧州航道水位信息，为船舶调度提供依据。

## 主要功能

**1.** 爬取广西水运发展中心每日发布的官方航道水情信息。  
**2.** 存储每日的航道水位数据到本地，可持久存储。  
**3.** 将爬取到的航道水位数据可视化展示，并做分析，初步预判近日梧州航道水位变化情况。

## 注意事项

- **在每天上午10点之后运行，以避免数据爬取不全的情况。**
- **一天内，如果已经更新了当天的数据，不需要再次运行。**
- **可视化报告在程序同文件夹内，文件名为water_level_report.html。**
- **为达到最佳展示效果，请将浏览器窗口扩展至全屏查看可视化报告。**

## 本地部署

### 环境要求
- **Python 3.14+**
- **Playwright 1.40+**
- **BeautiifulSoup 4.12+**

### 部署操作

**1. 克隆项目**
```
# 复制以下命令到终端执行
git clone https://gitee.com/takatsuki225/hdqp2.git

#进入目录
cd/
```

**2. 安装依赖**
```
# 安装依赖
pip install -r requirements.txt

# 安装Playwright浏览器驱动
playwright install chromium
```
**3. 启动程序**
```
# 运行脚本
python screenshot.py
```

## 项目架构

