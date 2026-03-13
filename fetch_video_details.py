import requests
import json
import time
import random
from openpyxl import Workbook
from datetime import datetime

# ==================== 配置区域 ====================
# 输入的BV号列表文件（每行一个BV号）
INPUT_FILE = "all_bvids_2025.txt"                # 将此文件放在脚本同目录下

# 输出的Excel文件
OUTPUT_FILE = "video_details.xlsx"                # 结果Excel文件名

# 失败记录文件
FAILED_LOG = "failed_bvids.txt"                   # 失败的BV号记录

# 每次请求后的延迟（秒），避免请求过快
REQUEST_DELAY = 1.5

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0"

# 可选：如果你有登录cookies，可以在这里添加（能提高请求限额）
COOKIES = {
    # 'SESSDATA': '你的SESSDATA',   # 登录后从浏览器复制
    # 'bili_jct': '你的bili_jct',
}
# =================================================

def fetch_video_info(bvid):
    """
    调用B站API获取单个视频的详细信息
    返回字典，如果失败返回None
    """
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
    headers = {
        'User-Agent': USER_AGENT,
        'Referer': 'https://www.bilibili.com',
    }
    try:
        resp = requests.get(url, headers=headers, cookies=COOKIES, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        if data.get('code') != 0:
            print(f"API返回错误: {data.get('message')} (bvid={bvid})")
            return None
        info = data['data']
        stat = info['stat']
        owner = info['owner']
        return {
            'bvid': bvid,
            'title': info.get('title', ''),
            'link': f"https://www.bilibili.com/video/{bvid}",
            'author': owner.get('name', ''),
            'author_id': owner.get('mid', 0),
            'view': stat.get('view', 0),
            'danmaku': stat.get('danmaku', 0),
            'like': stat.get('like', 0),
            'coin': stat.get('coin', 0),
            'favorite': stat.get('favorite', 0),
            'share': stat.get('share', 0),
            'reply': stat.get('reply', 0),
            'pubdate': info.get('pubdate', 0),  # 时间戳
            'duration': info.get('duration', 0), # 时长（秒）
            'desc': info.get('desc', ''),
            'tname': info.get('tname', ''),      # 分区名称
            'aid': info.get('aid', 0),
        }
    except requests.exceptions.RequestException as e:
        print(f"网络请求失败 (bvid={bvid}): {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析失败 (bvid={bvid}): {e}")
        return None
    except Exception as e:
        print(f"未知错误 (bvid={bvid}): {e}")
        return None

def read_bvids(file_path):
    """
    尝试多种编码读取BV号列表文件，返回BV号列表
    """
    encodings = ['utf-8', 'gbk', 'utf-8-sig', 'gb2312', 'latin1']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                lines = [line.strip() for line in f if line.strip()]
            print(f"成功使用 {enc} 编码读取文件，共 {len(lines)} 条BV号")
            return lines
        except UnicodeDecodeError:
            continue
        except Exception as e:
            print(f"使用 {enc} 编码时出错: {e}")
            continue
    raise UnicodeDecodeError(f"无法解码文件 {file_path}，请检查文件编码或内容")

def main():
    # 读取BV号列表
    try:
        bvids = read_bvids(INPUT_FILE)
    except Exception as e:
        print(f"读取文件失败: {e}")
        return

    print(f"共读取到 {len(bvids)} 个BV号，开始采集...")

    # 创建Excel工作簿
    wb = Workbook()
    ws = wb.active
    ws.append([
        "BV号", "标题", "链接", "UP主", "UP主ID", "精确播放数", "弹幕数",
        "点赞数", "投币数", "收藏数", "分享数", "评论数", "发布时间", "时长(秒)",
        "视频简介", "分区", "视频aid"
    ])

    failed_bvids = []
    success_count = 0

    for idx, bvid in enumerate(bvids, 1):
        print(f"[{idx}/{len(bvids)}] 正在处理: {bvid}")
        info = fetch_video_info(bvid)
        if info:
            pub_date = datetime.fromtimestamp(info['pubdate']).strftime('%Y-%m-%d %H:%M:%S')
            ws.append([
                info['bvid'],
                info['title'],
                info['link'],
                info['author'],
                info['author_id'],
                info['view'],
                info['danmaku'],
                info['like'],
                info['coin'],
                info['favorite'],
                info['share'],
                info['reply'],
                pub_date,
                info['duration'],
                info['desc'],
                info['tname'],
                info['aid'],
            ])
            success_count += 1
            print(f"  成功获取: {info['title']}")
        else:
            failed_bvids.append(bvid)

        # 随机延迟，避免请求过快
        delay = REQUEST_DELAY + random.uniform(0, 1)
        time.sleep(delay)

    # 保存Excel
    wb.save(OUTPUT_FILE)
    print(f"\n采集完成！成功获取 {success_count} 个，失败 {len(failed_bvids)} 个。")
    print(f"结果已保存到: {OUTPUT_FILE}")

    if failed_bvids:
        with open(FAILED_LOG, 'w', encoding='utf-8') as f:
            for bvid in failed_bvids:
                f.write(bvid + '\n')
        print(f"失败的BV号已记录到: {FAILED_LOG}")

if __name__ == '__main__':
    main()