import re
import requests
import json
import time
import random

# ==================== 配置 ====================
INPUT_FILE = "2025_bilibili_up.txt"        # 输入的昵称文件
OUTPUT_FILE = "up_list.json"                # 输出的JSON文件
FAILED_LOG = "failed_names.txt"             # 失败记录
REQUEST_DELAY = 1.5                          # API请求间隔
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
# 如果有登录cookies可提高成功率（可选）
COOKIES = {
    # 'SESSDATA': '你的SESSDATA',
}
# =============================================

def search_uid(name):
    url = "https://api.bilibili.com/x/web-interface/search/type"
    params = {'search_type': 'bili_user', 'keyword': name}
    headers = {'User-Agent': USER_AGENT}
    try:
        resp = requests.get(url, params=params, headers=headers, cookies=COOKIES, timeout=10)
        data = resp.json()
        if data.get('code') == 0 and data['data']['result']:
            return data['data']['result'][0]['mid']
    except Exception as e:
        print(f"查询出错 {name}: {e}")
    return None

def parse_line(line):
    line = line.strip()
    if not line:
        return None, None
    match = re.search(r'(\d+)$', line)
    if match:
        uid = int(match.group(1))
        name = line[:match.start()].strip()
        return name, uid
    else:
        return line, None

def main():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    up_list = []
    failed = []

    for idx, line in enumerate(lines, 1):
        name, uid = parse_line(line)
        if name is None:
            continue
        print(f"[{idx}] 处理: {name}" + (f" (已有UID: {uid})" if uid else ""))
        if uid is None:
            uid = search_uid(name)
            if uid:
                print(f"  查询到UID: {uid}")
            else:
                print(f"  查询失败")
                failed.append(name)
                continue
            time.sleep(REQUEST_DELAY + random.uniform(0, 1))
        up_list.append({'id': uid, 'name': name})

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(up_list, f, ensure_ascii=False, indent=2)
    print(f"\n成功保存 {len(up_list)} 条数据到 {OUTPUT_FILE}")

    if failed:
        with open(FAILED_LOG, 'w', encoding='utf-8') as f:
            for name in failed:
                f.write(name + '\n')
        print(f"有 {len(failed)} 个昵称查询失败，已记录到 {FAILED_LOG}")

if __name__ == '__main__':
    main()