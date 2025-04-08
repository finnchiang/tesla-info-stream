
import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import openai
import os

# OpenAI Key 从环境变量读取
openai.api_key = os.getenv("OPENAI_API_KEY")

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

SOURCES = [
    {
        "name": "Teslarati",
        "url": "https://www.teslarati.com/",
        "base": "https://www.teslarati.com",
        "parser": lambda soup: soup.select(".jeg_postblock_content .jeg_post_title a")
    },
    {
        "name": "Electrek",
        "url": "https://electrek.co/guides/tesla/",
        "base": "",
        "parser": lambda soup: soup.select("div.post-block > a")
    }
]

def translate(text):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": f"请把这段英文翻译成简体中文：{text}"}],
            temperature=0.3,
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("翻译失败:", e)
        return text

def fetch_articles():
    all_articles = []
    for source in SOURCES:
        try:
            res = requests.get(source["url"], headers=HEADERS, timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            links = source["parser"](soup)
            for a in links[:25]:
                title = a.get_text().strip()
                href = a["href"]
                url = href if href.startswith("http") else source["base"] + href
                summary = translate(f"This is a news about Tesla titled: {title}")
                article = {
                    "title": translate(title),
                    "source": source["name"],
                    "summary": summary,
                    "link": url
                }
                all_articles.append(article)
        except Exception as e:
            print(f"抓取 {source['name']} 出错：", e)
    return all_articles[:50]

def main():
    articles = fetch_articles()
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"{len(articles)} 篇文章已保存到 data.json")

if __name__ == "__main__":
    main()
