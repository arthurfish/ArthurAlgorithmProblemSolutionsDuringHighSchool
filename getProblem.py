import csv
import time
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
import pyperclip  # 用于读取剪贴板内容

# 输入和输出文件路径
INPUT_CSV_FILE = "record_source_codes_database.csv"  # 输入的 CSV 文件
OUTPUT_CSV_FILE = "problem_titles.csv"  # 输出的 CSV 文件

# 题目复制按钮的 CSS 选择器
COPY_BUTTON_SELECTOR = "#app > div.main-container > main > div > section.main > section > div > div.action > a:nth-child(1)"

# 登录后的 Cookie（需要从浏览器提取）
COOKIES = [
    {"name": "__client_id", "value": "4764be73375e89135f51418f8d864c11a26f2c7a", "domain": ".luogu.com.cn"},
    {"name": "_uid", "value": "117381", "domain": ".luogu.com.cn"},
    # 添加其他 Cookie，如果需要
]

# 设置 Selenium 浏览器
def setup_driver():
    options = Options()
    #options.add_argument("--headless")  # 无头模式（可选，可以注释掉以调试）
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")
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

# 从剪贴板获取内容
def get_clipboard_content():
    try:
        time.sleep(3)  # 等待内容复制到剪贴板
        return pyperclip.paste()
    except Exception as e:
        print(f"无法读取剪贴板内容：{e}")
        return None

# 爬取题目内容
def fetch_problem_title(driver, problem_url):
    try:
        # 打开题目页面
        driver.get(problem_url)
        time.sleep(6)  # 等待页面加载

        # 找到复制按钮并点击
        copy_button = driver.find_element(By.CSS_SELECTOR, COPY_BUTTON_SELECTOR)
        ActionChains(driver).move_to_element(copy_button).click().perform()
        time.sleep(4)  # 等待内容复制到剪贴板

        # 从剪贴板获取题目内容
        problem_title = get_clipboard_content()
        if not problem_title:
            print(f"无法从剪贴板获取题目内容：{problem_url}")
            return None

        # 将题目内容转换为 Base64
        problem_title_base64 = base64.b64encode(problem_title.encode("utf-8")).decode("utf-8")
        return problem_title_base64
    except NoSuchElementException as e:
        print(f"页面元素未找到，跳过：{problem_url} - {e}")
        return None
    except TimeoutException as e:
        print(f"加载页面超时，跳过：{problem_url} - {e}")
        return None
    except Exception as e:
        print(f"发生错误：{e}")
        return None

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
        writer.writerow(["problem_url", "problem_in_base64"])  # 写入表头
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
            problem_url = record["problem_url"]
            print(f"正在处理：{problem_url}")

            # 获取题目标题的 Base64 编码
            problem_title_base64 = fetch_problem_title(driver, problem_url)

            if problem_title_base64:
                results.append([problem_url, problem_title_base64])

        # 保存到 CSV 文件
        save_to_csv(results, OUTPUT_CSV_FILE)

    finally:
        # 关闭浏览器
        driver.quit()


if __name__ == "__main__":
    main()