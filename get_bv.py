import os
import time
import re
import json
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service

class BilibiliUpSpider:
    def __init__(self, headless=False, driver_path=None):
        options = webdriver.EdgeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0')
        if driver_path:
            service = Service(executable_path=driver_path)
        else:
            from webdriver_manager.microsoft import EdgeChromiumDriverManager
            service = Service(EdgeChromiumDriverManager().install())
        self.driver = webdriver.Edge(service=service, options=options)

    def login(self):
        self.driver.get('https://www.bilibili.com')
        input("请在弹出的浏览器中扫码登录，登录完成后按回车键继续...")
        time.sleep(3)

    def get_up_video_bvids(self, mid, year=2025, output_file=None):
        bvids = []
        base_url = f'https://space.bilibili.com/{mid}/video'
        print(f"正在访问UP主 {mid} 的空间: {base_url}")
        self.driver.get(base_url)

        try:
            WebDriverWait(self.driver, 10).until(
                lambda d: d.title not in ["登录", "哔哩哔哩登录"]
            )
            print(f"当前页面标题: {self.driver.title}")
        except:
            print("警告：页面标题可能是登录页，请检查登录状态")
        time.sleep(5)
        try:
            close_btn = self.driver.find_element(By.CLASS_NAME, 'bili-mini-close-icon')
            close_btn.click()
            print("关闭了登录提示框")
        except:
            pass

        start_timestamp = int(time.mktime(time.strptime(f"{year}-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")))
        end_timestamp = int(time.mktime(time.strptime(f"{year}-12-31 23:59:59", "%Y-%m-%d %H:%M:%S")))

        page_num = 1
        found_2025 = False  # 是否已经找到过目标年份的视频
        while True:
            print(f"正在处理第 {page_num} 页...")
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.bili-video-card'))
            )
            page_bvids, has_target = self._extract_bvids_from_page_with_year(start_timestamp, end_timestamp)

            if has_target:
                bvids.extend(page_bvids)
                found_2025 = True
                print(f"当前页获取到 {len(page_bvids)} 个{year}年BV号，累计 {len(bvids)} 个")
            else:
                if found_2025:
                    print("已记录完所有目标年份视频，停止翻页")
                    break
                else:
                    print("当前页尚无目标年份视频，继续翻页查找...")

            # 决定是否继续翻页：当还没进入目标年份或当前页还有目标年份时，继续
            should_continue = has_target or not found_2025
            if not should_continue:
                break

            # 尝试点击下一页
            try:
                next_btn = self.driver.find_element(By.XPATH, '//button[contains(text(), "下一页")]')
                if next_btn.is_displayed() and next_btn.is_enabled():
                    self.driver.execute_script("arguments[0].click();", next_btn)
                    print("已点击下一页，等待加载...")
                    time.sleep(5)
                    try:
                        WebDriverWait(self.driver, 10).until(
                            EC.staleness_of(self.driver.find_element(By.CSS_SELECTOR, '.bili-video-card'))
                        )
                    except:
                        pass
                    page_num += 1
                else:
                    print("下一页按钮不可见或不可用，已到达最后一页")
                    break
            except Exception as e:
                print(f"无法找到或点击下一页按钮，可能已到最后一页: {e}")
                break

        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                for bvid in bvids:
                    f.write(bvid + '\n')
            print(f"BV号已保存到 {output_file}")
        return bvids

    def _extract_bvids_from_page_with_year(self, start_ts, end_ts):
        bvids = []
        has_target = False
        try:
            cards = self.driver.find_elements(By.CSS_SELECTOR, '.bili-video-card')
            print(f"找到 {len(cards)} 个视频卡片")
        except Exception as e:
            print(f"查找视频卡片失败: {e}")
            return bvids, False

        for card in cards:
            try:
                time_elem = card.find_element(By.CSS_SELECTOR, '.bili-video-card__subtitle span')
                time_text = time_elem.text.strip()
                match = re.search(r'(\d{4})-(\d{2})-(\d{2})', time_text)
                if match:
                    pub_timestamp = int(time.mktime(time.strptime(match.group(0), "%Y-%m-%d")))
                else:
                    continue
            except:
                continue

            if start_ts <= pub_timestamp <= end_ts:
                has_target = True
                try:
                    link = card.find_element(By.CSS_SELECTOR, '.bili-video-card__title a')
                    href = link.get_attribute('href')
                    bvid = self._extract_bvid_from_url(href)
                    if bvid:
                        bvids.append(bvid)
                except:
                    try:
                        link = card.find_element(By.CSS_SELECTOR, 'a[href*="/video/"]')
                        href = link.get_attribute('href')
                        bvid = self._extract_bvid_from_url(href)
                        if bvid:
                            bvids.append(bvid)
                    except:
                        pass
        return bvids, has_target

    def _extract_bvid_from_url(self, url):
        match = re.search(r'/video/(BV\w+)', url)
        return match.group(1) if match else None

    def close(self):
        self.driver.quit()


if __name__ == '__main__':
    # ==================== 用户配置区域 ====================
    # 请根据实际情况修改以下路径和参数

    # UP主列表文件路径（JSON格式，包含id和name字段）
    INPUT_JSON = "up_list.json"               # 将此文件放在与脚本相同的目录下

    # 输出目录，用于保存每个UP主的BV号文件
    OUTPUT_DIR = "./output"                    # 会在当前目录下创建output文件夹

    # 所有BV号汇总文件名（将保存在OUTPUT_DIR内）
    TOTAL_BV_FILE = "all_bvids_2025.txt"       # 最终汇总文件

    # 是否启用无头模式（True为不显示浏览器界面）
    HEADLESS = False

    # Edge驱动路径（如果留空则尝试自动下载，建议留空）
    DRIVER_PATH = None                           # 例如：r"C:\webdrivers\msedgedriver.exe"

    # 目标年份
    TARGET_YEAR = 2025
    # =====================================================

    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 读取UP主列表
    try:
        with open(INPUT_JSON, 'r', encoding='utf-8') as f:
            up_list = json.load(f)
    except Exception as e:
        print(f"读取UP主列表失败: {e}")
        exit(1)

    # 初始化爬虫
    spider = BilibiliUpSpider(headless=HEADLESS, driver_path=DRIVER_PATH)

    # 必须登录
    spider.login()

    all_bvids = []
    for idx, up in enumerate(up_list):
        mid = up['id']
        name = up.get('name', str(mid))
        print(f"\n[{idx+1}/{len(up_list)}] 正在处理UP主 {name} ({mid})...")
        up_bv_file = os.path.join(OUTPUT_DIR, f"{mid}_{name}_{TARGET_YEAR}.txt")
        bvids = spider.get_up_video_bvids(mid, year=TARGET_YEAR, output_file=up_bv_file)

        if bvids:
            print(f"✅ 获取到 {len(bvids)} 个{TARGET_YEAR}年BV号")
            all_bvids.extend(bvids)
            total_file_path = os.path.join(OUTPUT_DIR, TOTAL_BV_FILE)
            with open(total_file_path, 'a', encoding='utf-8') as f:
                for bvid in bvids:
                    f.write(bvid + '\n')
        else:
            print(f"⚠️ 未获取到{TARGET_YEAR}年BV号")

        if idx < len(up_list) - 1:
            delay = random.uniform(60, 120)
            print(f"等待 {delay:.1f} 秒后继续...")
            time.sleep(delay)

    spider.close()
    total_file_path = os.path.join(OUTPUT_DIR, TOTAL_BV_FILE)
    print(f"\n🎉 全部完成！共获取 {len(all_bvids)} 个{TARGET_YEAR}年BV号。")
    print(f"所有BV号已汇总到: {total_file_path}")