from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import csv
import os

# 常量定义
BASE_URL = "https://www.luogu.com.cn/record/list?user=117381&status=12&page={}"
OUTPUT_FILE = "submission_records.csv"
HTML_DEBUG_DIR = "html_debug"

# 登录后的 Cookie（需要手动从浏览器获取）
COOKIES = [
    {"name": "__client_id", "value": "4764be73375e89135f51418f8d864c11a26f2c7a", "domain": ".luogu.com.cn"},
    {"name": "_uid", "value": "117381", "domain": ".luogu.com.cn"},
    # 添加其他 Cookie，如果需要
]

# 创建保存 HTML 文件的目录（如不存在则创建）
os.makedirs(HTML_DEBUG_DIR, exist_ok=True)


def scrape_using_selenium():
    """
    使用 Selenium 模拟浏览器，抓取动态渲染的页面内容
    """
    # 配置 Selenium WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 无头模式，不显示浏览器界面
    options.add_argument("--disable-gpu")  # 禁用 GPU 加速
    options.add_argument("--no-sandbox")  # 沙盒模式
    options.add_argument("--disable-dev-shm-usage")  # 解决资源限制问题

    # 动态安装并启动 ChromeDriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    try:
        # 打开基础页面（为了附加 Cookie，必须先加载同一域名的页面）
        driver.get("https://www.luogu.com.cn/")

        # 添加 Cookie
        for cookie in COOKIES:
            driver.add_cookie(cookie)
        print("Cookie 已成功附加！")

        # 刷新页面，使 Cookie 生效
        driver.refresh()
        time.sleep(2)  # 等待页面加载完成

        # 确认是否登录成功
        if "登录" in driver.page_source:
            print("附加 Cookie 后仍显示登录页面，请检查 Cookie 是否有效！")
            return []

        # 存储爬取结果
        records = []

        for page in range(1, 13):  # 爬取第 1 到第 12 页
            print(f"正在爬取第 {page} 页...")
            url = BASE_URL.format(page)
            driver.get(url)

            # 等待页面完全加载
            time.sleep(10)  # 可根据页面复杂程度调整加载等待时间

            # 提取页面 HTML
            html = driver.page_source

            # 保存 HTML 到本地（便于调试）
            with open(f"{HTML_DEBUG_DIR}/page_{page}.html", "w", encoding="utf-8") as file:
                file.write(html)

            # 解析 HTML 内容
            soup = BeautifulSoup(html, "html.parser")

            # 遍历记录
            for index in range(1, 21):  # 每页最多 20 条记录
                # 评测记录 URL
                record_selector = f"#app > div.main-container > main > div > div > div > div.border.table > div > div:nth-child({index}) > div.status > a"
                record_element = soup.select_one(record_selector)
                if record_element and "href" in record_element.attrs:
                    record_url = "https://www.luogu.com.cn" + record_element["href"]
                else:
                    continue

                # 题目 URL 和名称
                problem_selector = f"#app > div.main-container > main > div > div > div > div.border.table > div > div:nth-child({index}) > div.problem > div > a"
                problem_element = soup.select_one(problem_selector)
                if problem_element and "href" in problem_element.attrs:
                    problem_url = "https://www.luogu.com.cn" + problem_element["href"]
                    problem_name = problem_element.text.strip()
                else:
                    continue

                # 保存数据
                records.append((record_url, problem_url, problem_name))
                print(f"{record_url}, {problem_url}, {problem_name}")

    finally:
        driver.quit()  # 关闭浏览器

    return records


def save_to_csv(records, filename=OUTPUT_FILE):
    """
    将爬取的记录保存到 CSV 文件
    """
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["评测记录 URL", "题目 URL", "题目名称"])  # 表头
        writer.writerows(records)
    print(f"数据已保存到 {filename}")


if __name__ == "__main__":
    # 使用 Selenium 抓取数据
    submission_records = scrape_using_selenium()

    # 保存到 CSV 文件
    save_to_csv(submission_records)