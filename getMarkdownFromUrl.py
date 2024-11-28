import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin
import urllib3
import base64
from openai import OpenAI
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import socket
import backoff
# 把需要的网址放在这里！！！！
expr_url = "https://phylab.suda.edu.cn/e8/7d/c22510a452733/page.htm"

prompt = r"""请提取PPT图片中的文字。用Markdown对格式进行排版并且用裸的latex来表现公式
（不要放到任何的多余的括号里，包括但不限于$, $$, \(, \[之类的）
因为我的目的是将所有的PPT拼接为一个文档，所以请删除页头和页尾重复的东西。"""


# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def create_retry_session(retries=3, backoff_factor=0.3,
                         status_forcelist=(500, 502, 504)):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

@backoff.on_exception(backoff.expo,
                      (requests.exceptions.RequestException,
                       socket.error,
                       ConnectionError),
                      max_tries=5)
def get_text_from_image(image_data, api_key, base_url):
    """使用GPT-4 Vision API提取图片中的文字"""
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "chatgpt-4o-latest",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 4096
        }

        # 确保endpoint正确
        endpoint = f"{base_url.rstrip('/')}/v1/chat/completions"

        response = requests.post(
            endpoint,
            headers=headers,
            json=payload,
            timeout=60
        )

        if response.status_code != 200:
            print(f"API Response Status Code: {response.status_code}")
            print(f"API Response Content: {response.text}")
            response.raise_for_status()

        result = response.json()
        return result['choices'][0]['message']['content']

    except Exception as e:
        print(f"Error using GPT-4 API: {e}")
        print(f"Error type: {type(e)}")
        return ""

def get_images_from_webpage(url, session):
    """获取网页中的图片"""
    try:
        response = session.get(url, verify=False, timeout=(10, 30))
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.select("#MyContent > div > p img")

        image_urls = []
        for img in images:
            img_url = img.get('src')
            if img_url:
                full_url = urljoin(url, img_url)
                image_urls.append(full_url)

        return image_urls

    except Exception as e:
        print(f"Error fetching webpage: {e}")
        return []

def download_image(url, session):
    """下载图片"""
    try:
        response = session.get(url, verify=False, timeout=(10, 30))
        response.raise_for_status()
        return base64.b64encode(response.content).decode('utf-8')
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

def main():
    # API配置
    API_KEY = "sk-JxUc85ea3b4ce9004a296523881ceb4b1dc7b5105edIw9CG"
    BASE_URL = "https://api.gptsapi.net"

    # 设置session
    session = create_retry_session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    })

    # 目标URL
    url = expr_url

    try:
        # 获取图片URL列表
        image_urls = get_images_from_webpage(url, session)
        print(f"Found {len(image_urls)} images")

        # 处理每张图片并收集文本
        all_text = []
        for i, img_url in enumerate(image_urls, 1):
            print(f"Processing image {i}/{len(image_urls)}: {img_url}")
            image_data = download_image(img_url, session)
            if image_data:
                text = get_text_from_image(image_data, API_KEY, BASE_URL)
                if text:
                    all_text.append(text)
                    # 保存中间结果
                    # with open(f"partial_result_{i}.md", "w", encoding="utf-8") as f:
                    #    f.write(text)
            time.sleep(2)

        # 将所有文本合并为一个Markdown文档
        final_markdown = "\n\n---\n\n".join(all_text)

        # 保存结果
        with open("experiment_content.md", "w", encoding="utf-8") as f:
            f.write(final_markdown)

        print("Process completed. Results saved to ？？？")

    except Exception as e:
        print(f"An error occurred in main execution: {e}")
        raise

if __name__ == "__main__":
    main()