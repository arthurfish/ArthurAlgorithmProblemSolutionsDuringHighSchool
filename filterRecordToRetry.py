import csv

# 输入文件路径
SUCCESS_CSV_FILE = "record_source_codes_first_try.csv"  # 爬取成功的结果文件
ORIGINAL_CSV_FILE = "submission_records.csv"  # 原始待爬取的文件
RETRY_CSV_FILE = "retry_records.csv"  # 输出的重试文件

def generate_retry_csv(success_file, original_file, retry_file):
    # 读取成功记录的 submission_url
    success_urls = set()
    with open(success_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            success_urls.add(row["submission_url"])

    # 读取原始记录，筛选未成功的记录
    retry_records = []
    with open(original_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["record"] not in success_urls:  # 如果 record 不在成功记录中
                retry_records.append(row)

    # 写入重试文件
    with open(retry_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["record", "problem", "problem_name"])
        writer.writeheader()  # 写入表头
        writer.writerows(retry_records)  # 写入未成功的记录

    print(f"重试文件已生成，共 {len(retry_records)} 条记录：{retry_file}")

# 主函数
def main():
    generate_retry_csv(SUCCESS_CSV_FILE, ORIGINAL_CSV_FILE, RETRY_CSV_FILE)

if __name__ == "__main__":
    main()