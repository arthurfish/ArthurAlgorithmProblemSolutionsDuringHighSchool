from bs4 import BeautifulSoup

in_file = "19.html"
out_file = "19.txt"

def convert_chat(html_file):
    # 读取HTML文件
    with open(html_file, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # 按顺序获取所有对话内容
    messages = []
    for div in soup.find_all('div', class_=['yu', 'gao']):
        if div['class'][0] == 'yu':
            messages.append(f"Yu: {div.text}")
        else:
            messages.append(f"Gao: {div.text}")


    with open(out_file, 'w', encoding='utf-8') as f:
        for message in messages:
            f.write(message + '\n')

# 使用文件路径调用函数
convert_chat(in_file)  # 替换成你的HTML文件路径