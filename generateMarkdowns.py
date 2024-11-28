import csv
import base64
import os

# 输入 CSV 文件路径
INPUT_CSV_FILE = "merged_records.csv"

# 输出 Markdown 文件的目录
OUTPUT_DIR = "markdown_files"

# 创建输出目录
os.makedirs(OUTPUT_DIR, exist_ok=True)

def decode_base64(encoded_str):
    """将 Base64 字符串解码为普通文本"""
    try:
        return base64.b64decode(encoded_str).decode("utf-8")
    except Exception as e:
        print(f"Base64 解码失败: {e}")
        return ""

def generate_markdown(row):
    """根据 CSV 行生成 Markdown 文本"""
    # 解码 Base64 内容
    problem_text = decode_base64(row["problem_in_base64"])
    sourcecode_text = decode_base64(row["submission_sourcecode_in_base64"])

    # 提取题目编号
    problem_url = row["problem_url"]
    title = problem_url.split("/")[-1]  # 最后部分是题目编号

    # 生成 Markdown 内容
    markdown_content = f"""<html><body>
<h1>{title}</h1>

<strong>{row["submission_datetime"]}</strong>
    
<div>{problem_text}</div>

<h1>GCX的AC代码</h1>
<code>
{sourcecode_text}
</code>
</body>
</html>
"""
    temp_string = """```yaml
submission_time: {row["submission_datetime"]}
problem_base64: {row["problem_in_base64"]}
sourcecode_base64: {row["submission_sourcecode_in_base64"]}
title: {title}
author: Arthurfish
```"""
    return markdown_content

def process_csv(input_file, output_dir):
    """读取 CSV 文件并为每一行生成一个 Markdown 文件"""
    with open(input_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for i, row in enumerate(reader):
            # 提取题目编号作为文件名
            problem_url = row["problem_url"]
            title = problem_url.split("/")[-1]  # 最后部分是题目编号
            markdown_filename = f"{title}.html"

            # 生成 Markdown 内容
            markdown_content = generate_markdown(row)

            # 保存到 Markdown 文件
            output_path = os.path.join(output_dir, markdown_filename)
            with open(output_path, mode="w", encoding="utf-8") as md_file:
                md_file.write(markdown_content)

            print(f"[{i + 1}] 文件已生成: {output_path}")

# 主函数
def main():
    process_csv(INPUT_CSV_FILE, OUTPUT_DIR)

if __name__ == "__main__":
    main()