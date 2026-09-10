# 水文数据查询程序2（Hydrological data query program2）
一个基于**Python + Playwright + BeautifulSoup + ECharts**的便携化河道水位数据爬取与可视化展示分析程序。  
供**梧州仓码**同事使用，快速查询梧州航道水位信息，为船舶调度提供依据。

## 主要功能

**1.** 爬取广西水运发展中心每日发布的官方航道水情信息，涵盖梧州仓码上游西江流域内6个水文站点与3个通航水利枢纽的水位相关数据。  
**2.** 存储每日的航道水位与水利枢纽相关数据到本地，本地化持久存储。  
**3.** 将爬取到的航道水位数据可视化展示，并做分析，初步预判近日梧州航道水位变化情况。   
**4.** 对爬取到的水位数据进行分析，并进行相关预警信息的显示，比如高水位、水位超警、放水预警。   
**5.** 支持将.py文件打包为.exe程序，可以在其他电脑更方便的使用。

## 使用说明

**下载后（或本地部署成果执行打包指令之后），仅在“西江水位查看分析”文件夹内操作使用即可**  
**1.** 打开文件夹后（西江水位查看分析文件夹），**双击运行“水位数据爬取.exe”文件。**  
**2.** 会打开一个终端页面，**请耐心等待10秒左右**，然后程序会开始自动运行。    
**3.** 程序开始自动运行后，**终端页面会输出水位信息以及运行情况**，可以通过终端判断是否运行正常。   
**4. 程序自动运行时会自动打开一个浏览器窗口，是自动爬虫窗口，请不要进行任何操作，运行结束后会在5秒内自动关闭！**   
**5.** 运行完成后，终端会自动关闭。并且**会在程序同文件夹内生成一个“water_level_report.html”网页文件，双击打开（用浏览器打开）即可查看可视化报告。**

## 注意事项

- **在每天上午10点之后运行，以避免数据爬取不全的情况。**
- **一天内，如果已经更新了当天的数据，不需要再次运行。**
- **可视化报告在程序同文件夹内，文件名为water_level_report.html。**
- **为达到最佳展示效果，请将浏览器窗口扩展至全屏查看可视化报告。**
- **数据缺失问题：数据源链接为https://www.gxghj.cn/c/fw/slcx   打开后看到的前4条链接中，只要缺少南宁、柳州、梧州的3个航道水情信息的任意一个链接，就会影响数据爬取，导致数据缺少。**

## 联系方式

### 如果您在使用时有问题或建议，欢迎联系我
- **电子邮箱；liufuyu01@sinotrans.com**

## 程序架构
### 此为打包后的文件夹结构（本地部署执行打包指令后的dist文件夹需和此结构保持一致）
```
西江水位查看分析/
├── 水位数据爬取.exe            # 主程序（双击运行，用于爬取、解析、存储、生成报告，勿动！）
├── water_level_data.json      # 水位与枢纽历史数据（本地持久化存储，勿动,改动会影响可视化报告！）
├── water_level_report.html    # 可视化分析报告（双击查看，程序运行后生成，勿动！）
├── river.jpg                  # 流域示意图（报告内嵌图片，勿动，删除会影响可视化报告！）
├── screenshot_list.png        # 列表页截图
├── screenshot_detail_1.png    # 详情页截图1
├── screenshot_detail_2.png    # 详情页截图2
├── screenshot_detail_3.png    # 详情页截图3
├── screenshot_detail_4.png    # 详情页截图4
└── 使用说明.txt                # 程序说明文档
```

## 本地部署

### 环境要求
- **Python 3.14+**
- **Playwright 1.40+**
- **BeautiifulSoup 4.12+**
- **pyinstaller 6.22.2（如有打包需求才需要配置）**

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

**4. 打包为程序**
```
#打包成exe程序
python -m PyInstaller screenshot.spec
```
## 项目架构

```
psw3/
├── screenshot.py              # 主程序脚本（爬取、解析、存储、生成报告）
├── screenshot.spec            # PyInstaller 打包配置文件
├── requirements.txt           # Python 依赖列表
├── water_level_data.json      # 水位与枢纽历史数据（本地持久化存储）
├── water_level_report.html    # 可视化分析报告（程序运行后生成）
├── river.jpg                  # 流域示意图（报告内嵌图片）
├── screenshot_list.png        # 列表页截图
├── screenshot_detail_1.png    # 详情页截图1
├── screenshot_detail_2.png    # 详情页截图2
├── screenshot_detail_3.png    # 详情页截图3
├── screenshot_detail_4.png    # 详情页截图4
└── README.md                  # 项目说明文档
```

