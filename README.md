 Bilibili UP主视频数据采集工具
一套用于批量采集B站UP主视频数据的Python工具集。支持从UP主空间获取视频BV号、通过官方API采集视频详细信息（播放量、弹幕、点赞等），并导出为Excel文件。所有代码仅供个人学习研究使用。

---
✨ 主要功能
- **UP主列表自动获取**：从文本文件读取UP主昵称，通过B站搜索API或手动补充UID，生成包含 `id` 和 `name` 的JSON文件。
- **BV号批量采集**：使用Selenium模拟浏览器登录，自动翻页并提取指定年份（如2025年）的视频BV号，保存为TXT文件。
- **视频详情数据采集**：基于B站官方API，批量获取视频的播放量、弹幕、点赞、投币、收藏、分享、评论、发布时间、分区等详细信息。
- **数据导出**：将采集结果保存为Excel文件，方便后续统计分析。
- **网页交互界面（可选）**：提供Flask Web应用，用户可输入UID和年份范围，在线获取统计表格。
---

## 📁 项目结构
BiliUP-Video-Info-Crawler/
├── README.md
├── requirements.txt
├── config.py # 配置文件（用户代理、延迟、cookies等）
├── up_list_generator.py # 从昵称列表生成UP主JSON文件
├── get_bvids_selenium.py # 使用Selenium获取BV号（需登录）
├── get_video_details.py # 使用API获取视频详情并生成Excel
├── web_app/ # Flask网页应用（可选）
│ ├── app.py
│ └── templates/
│ ├── index.html
│ └── result.html
├── data/ # 输入输出数据目录
│ ├── up_names.txt # UP主昵称列表（每行一个）
│ ├── up_list.json # 生成的UP主列表（id + 名称）
│ ├── bvids/ # 每个UP主的BV号文件
│ └── video_details.xlsx # 最终视频详情表格
└── logs/ # 错误日志


---

## 🔧 环境要求

- Python 3.8 或更高版本
- 依赖库（见 `requirements.txt`）
- **Selenium模式**需安装Microsoft Edge浏览器及对应版本的[Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)
- （可选）B站账号（用于获取登录cookies，提高API限额）

### 安装依赖
```bash
pip install -r requirements.txt

🚀 使用方法
1. 准备UP主列表
将需要采集的UP主昵称放入 data/up_names.txt，每行一个，支持昵称后跟空格+UID（如已知道UID可加快处理）。例如：
帕梅拉PamelaReif 604003146
英语兔
中国BOY超级大猩猩 562197
...
运行 up_list_generator.py 自动查询缺失的UID并生成 data/up_list.json。
python up_list_generator.py

2. 获取视频BV号（Selenium方式）
在 config.py 中配置 Edge WebDriver 路径（如手动下载）或留空自动下载。
运行 get_bvids_selenium.py，程序将打开浏览器，请扫码登录B站。
登录后按回车，脚本开始依次处理每位UP主，提取指定年份（默认2025）的视频BV号，保存在 data/bvids/ 目录下。
python get_bvids_selenium.py

3. 获取视频详细数据（API方式）
所有BV号收集完毕后，运行 get_video_details.py，程序会读取所有BV号（可从汇总文件 all_bvids_2025.txt 或逐UP主文件读取），调用B站API获取详情，并生成Excel表格。
bash
python get_video_details.py
输出文件为 data/video_details.xlsx，包含标题、播放量、弹幕、点赞、投币等字段。

📊 输出示例
BV号文件（data/bvids/1575718735_保镖的车库_2025.txt）：

text
BV1kCTeziEK8
BV1Fgr6Y9EsZ
BV131WmzhEF9
...
视频详情表格（data/video_details.xlsx）列名包括：
BV号、标题、链接、UP主、UP主ID、播放数、弹幕数、点赞数、投币数、收藏数、分享数、评论数、发布时间、时长(秒)、视频简介、分区、视频aid

⚠️ 重要声明
本工具仅供个人学习研究使用，不得用于任何商业目的或大规模数据爬取。
用户在使用本软件时，应遵守《中华人民共和国网络安全法》及Bilibili平台的相关服务条款，合理、合法地使用互联网资源。
开发者对因使用本工具产生的任何后果（如账号封禁、法律纠纷等）不承担任何责任。
请勿将本工具用于高频、恶意请求，以免对B站服务器造成负担。

🙏 致谢
感谢B站开放的部分API接口。
项目参考了众多开源社区的经验，如 Bilivideoinfo 等。
