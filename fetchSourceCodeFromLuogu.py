import csv
import time
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# 输入和输出文件路径
INPUT_CSV_FILE = "retry_records.csv"  # 输入的 CSV 文件
OUTPUT_CSV_FILE = "record_source_codes_retried.csv"  # 输出的 CSV 文件

# 定位器
CODE_TAB_SELECTOR = "#app > div.main-container > main > div > section.main > section > div.card.padding-none > div > ul > li:nth-child(3) > span"
CODE_CONTENT_SELECTOR = "#app > div.main-container > main > div > section.main > section > div:nth-child(2) > div > div > pre > code"
DATE_SELECTOR = "#app > div.main-container > main > div > section.side > div > div.info-rows > div:nth-child(3) > span:nth-child(2) > span"
PROBLEM_URL_SELECTOR = "#app > div.main-container > main > div > section.side > div > div.info-rows > div:nth-child(1) > span:nth-child(2) > span > div > a"

# 登录后的 Cookie（需要从浏览器提取）
COOKIES = [
    {"name": "__client_id", "value": "4764be73375e89135f51418f8d864c11a26f2c7a", "domain": ".luogu.com.cn"},
    {"name": "_uid", "value": "117381", "domain": ".luogu.com.cn"},
    # 添加其他 Cookie，如果需要
]


# 设置 Selenium 浏览器
def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # 无头模式
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    return driver

# 加载登录后的 Cookie
def load_cookies(driver):
    driver.get("https://www.luogu.com.cn/")  # 打开同域页面
    for cookie in COOKIES:
        driver.add_cookie(cookie)
    driver.refresh()  # 刷新页面使 Cookie 生效
    time.sleep(2)  # 等待页面加载
    print("Cookie 加载完成！")

# 获取提交详情（日期、源码、题目链接）
def fetch_submission_details(driver, record_url):
    try:
        # 打开评测记录页面
        driver.get(record_url)
        time.sleep(6)  # 等待页面加载

        # 点击 "代码" 标签
        code_tab = driver.find_element(By.CSS_SELECTOR, CODE_TAB_SELECTOR)
        ActionChains(driver).move_to_element(code_tab).click().perform()
        time.sleep(4)  # 等待代码显示

        # 提取代码内容
        code_element = driver.find_element(By.CSS_SELECTOR, CODE_CONTENT_SELECTOR)
        html_content = code_element.get_attribute("outerHTML")
        soup = BeautifulSoup(html_content, "html.parser")
        pure_text = soup.get_text()

        # 将代码转换为 Base64
        source_code_base64 = base64.b64encode(pure_text.encode("utf-8")).decode("utf-8")

        # 提取日期时间
        date_element = driver.find_element(By.CSS_SELECTOR, DATE_SELECTOR)
        submission_datetime = date_element.text.strip()

        # 提取题目链接
        problem_element = driver.find_element(By.CSS_SELECTOR, PROBLEM_URL_SELECTOR)
        problem_url = problem_element.get_attribute("href")
        if not problem_url.startswith("http"):
            problem_url = f"https://www.luogu.com.cn{problem_url}"  # 补全链接

        return submission_datetime, source_code_base64, problem_url
    except NoSuchElementException as e:
        print(f"页面元素未找到，跳过：{record_url} - {e}")
        return None, None, None
    except TimeoutException as e:
        print(f"加载页面超时，跳过：{record_url} - {e}")
        return None, None, None
    except Exception as e:
        print(f"发生错误：{e}")
        return None, None, None

# 读取 CSV 文件
def read_csv(file_path):
    records = []
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            records.append(row)
    return records

# 保存结果到 CSV
def save_to_csv(records, output_file):
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["submission_url", "submission_datetime", "problem_url", "submission_sourcecode_in_base64"])  # 写入表头
        writer.writerows(records)
    print(f"数据已保存到 {output_file}")

# 主函数
def main():
    # 读取输入记录
    input_records = read_csv(INPUT_CSV_FILE)

    # 设置 Selenium 浏览器
    driver = setup_driver()

    try:
        # 加载登录后的 Cookie
        load_cookies(driver)

        # 存储结果
        results = []

        for record in input_records:
            record_url = record["record"]
            print(f"正在处理：{record_url}")

            # 获取提交日期、源码、题目链接
            submission_datetime, source_code_base64, problem_url = fetch_submission_details(driver, record_url)

            if submission_datetime and source_code_base64 and problem_url:
                results.append([record_url, submission_datetime, problem_url, source_code_base64])

        # 保存到 CSV 文件
        save_to_csv(results, OUTPUT_CSV_FILE)

    finally:
        # 关闭浏览器
        driver.quit()


if __name__ == "__main__":
    main()