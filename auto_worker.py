
import os, json, requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime
try:
    from googletrans import Translator
except:
    Translator = None

SOURCES = [
    {
        "name": "Teslarati",
        "url": "https://www.teslarati.com/",
        "base": "https://www.teslarati.com/",
        "selector": "div.td_module_10",
        "title_selector": "h3.entry-title a",
        "summary_selector": "div.td-excerpt",
    },
    {
        "name": "Electrek",
        "url": "https://electrek.co/tag/tesla/",
        "base": "https://electrek.co/",
        "selector": "div.post-block",
        "title_selector": "h2.post-block__title a",
        "summary_selector": "div.post-block__content",
    },
    {
        "name": "InsideEVs",
        "url": "https://insideevs.com/news/category/tesla/",
        "base": "https://insideevs.com/",
        "selector": "div.article-preview-item",
        "title_selector": "a.article-preview-title",
        "summary_selector": "div.article-preview-description",
    },
    {
        "name": "新浪科技",
        "url": "https://tech.sina.com.cn/roll/index.d.html?cid=56476",
        "base": "https://tech.sina.com.cn",
        "selector": "div.roll-news ul li",
        "title_selector": "a",
        "summary_selector": None,
    }
]

def fetch_news():
    result = []
    for site in SOURCES:
        try:
            res = requests.get(site['url'], timeout=10)
            soup = BeautifulSoup(res.text, "html.parser")
            items = soup.select(site["selector"])[:5]
            for item in items:
                title_el = item.select_one(site["title_selector"])
                if not title_el: continue
                title = title_el.text.strip()
                link = urljoin(site["base"], title_el.get("href"))
                summary = ""
                if site["summary_selector"]:
                    summary_el = item.select_one(site["summary_selector"])
                    summary = summary_el.text.strip() if summary_el else ""
                zh_title, zh_summary = title, summary
                if Translator:
                    translator = Translator()
                    zh_title = translator.translate(title, dest="zh-cn").text
                    if summary:
                        zh_summary = translator.translate(summary, dest="zh-cn").text
                result.append({
                    "title": zh_title,
                    "source": site["name"],
                    "summary": zh_summary,
                    "url": link,
                    "timestamp": datetime.utcnow().isoformat()
                })
        except Exception as e:
            print("错误源:", site["name"], e)
    return result

def render_html(data):
    html = '\n<!DOCTYPE html><html lang="zh-CN"><head>\n<meta charset="UTF-8"><title>Tesla 全网资讯信息流</title>\n<style>\nbody {font-family:sans-serif;background:#f1f1f1;padding:20px;}\n.news-card {background:white;padding:20px;margin-bottom:20px;border-radius:8px;}\nh2 {margin-top:0;} a {color:blue;text-decoration:none;}\n</style></head><body><h1>Tesla 全网资讯信息流</h1><div class=\'news-container\'>\n'
    for item in data:
        html += f"<div class='news-card'><h2>{item['title']}</h2><p><strong>来源：</strong> {item['source']}</p><p><strong>摘要：</strong> {item['summary']}</p><a href='{item['url']}' target='_blank'>查看原文</a></div>"
    html += '</div></body></html>'
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

def auto_commit():
    os.system("git add index.html")
    os.system("git commit -m 'Auto update'")
    os.system("git push origin main")

def main():
    data = fetch_news()
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    render_html(data)
    if os.environ.get("AUTO_PUSH") == "true":
        auto_commit()

if __name__ == "__main__":
    main()
