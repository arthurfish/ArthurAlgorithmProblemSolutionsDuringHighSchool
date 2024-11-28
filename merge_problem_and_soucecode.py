import csv

# 输入文件路径
PROBLEM_CSV_FILE = "problem_titles.csv"  # 题目 CSV
CODE_CSV_FILE = "record_source_codes_database.csv"  # 代码 CSV
OUTPUT_CSV_FILE = "merged_records.csv"  # 合并后的 CSV

def merge_csv(problem_file, code_file, output_file):
    # 读取题目 CSV
    problem_data = {}
    with open(problem_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            # 使用 problem_url 作为键
            problem_data[row["problem_url"]] = row["problem_in_base64"]

    # 合并两个 CSV
    merged_records = []
    with open(code_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            problem_url = row["problem_url"]
            # 检查问题 CSV 中是否存在对应的 problem_url
            if problem_url in problem_data:
                merged_records.append({
                    "problem_url": problem_url,
                    "submission_datetime": row["submission_datetime"],
                    "problem_in_base64": problem_data[problem_url],
                    "submission_sourcecode_in_base64": row["submission_sourcecode_in_base64"]
                })

    # 写入合并后的 CSV
    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["problem_url", "submission_datetime", "problem_in_base64", "submission_sourcecode_in_base64"])
        writer.writeheader()  # 写入表头
        writer.writerows(merged_records)  # 写入数据

    print(f"合并完成，共 {len(merged_records)} 条记录，结果已保存到 {output_file}")

# 主函数
def main():
    merge_csv(PROBLEM_CSV_FILE, CODE_CSV_FILE, OUTPUT_CSV_FILE)

if __name__ == "__main__":
    main()