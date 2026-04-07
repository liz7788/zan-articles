"""
讚讚讚小姐姐 SEO 導流站生成器
讀取 articles.txt，自動生成 index.html + sitemap.xml
用法：python generate_site.py
"""
import os
import re
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ARTICLES_FILE = os.path.join(SCRIPT_DIR, "..", "articles.txt")
OUTPUT_DIR = SCRIPT_DIR

# GitHub Pages 設定（需要先建 repo）
SITE_URL = "https://liz7788.github.io/zan-articles/"
VOCUS_URL = "https://vocus.cc/salon/msliz7788"


def load_articles():
    """從 articles.txt 讀取文章列表"""
    articles = []
    with open(ARTICLES_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if " | " in line:
                title, url = line.rsplit(" | ", 1)
                articles.append({"title": title.strip(), "url": url.strip()})
    return articles


def categorize(articles):
    """把文章分類（問題情境導向）"""
    categories = {}
    for a in articles:
        title = a["title"]
        if any(k in title for k in ["潮濕", "發霉", "除濕", "防潮", "曬不乾"]):
            cat = "潮濕 / 除濕"
        elif any(k in title for k in ["冷氣", "降溫", "省電", "電費"]):
            cat = "冷氣 / 省電"
        elif any(k in title for k in ["租屋", "套房", "搬家", "小家電"]):
            cat = "租屋族生活"
        elif any(k in title for k in ["清潔", "掃地", "吸塵", "拖地", "貓", "狗", "寵物"]):
            cat = "居家清潔 / 寵物"
        elif any(k in title for k in ["廚房", "氣炸", "微波", "洗碗", "煮飯"]):
            cat = "廚房家電"
        elif any(k in title for k in ["洗衣", "烘衣", "曬衣"]):
            cat = "洗衣 / 烘衣"
        elif any(k in title for k in ["空氣", "過敏", "清淨"]):
            cat = "空氣品質 / 過敏"
        elif any(k in title for k in ["睡眠", "床墊", "枕頭", "被"]):
            cat = "睡眠品質"
        elif any(k in title for k in ["行動電源", "充電", "藍牙", "耳機"]):
            cat = "3C 配件"
        else:
            cat = "其他生活攻略"
        categories.setdefault(cat, []).append(a)
    return categories


def generate_html(articles, categories):
    """生成 index.html"""
    today = datetime.now().strftime("%Y-%m-%d")

    cat_sections = ""
    for cat, items in categories.items():
        links = ""
        for a in items:
            links += f'<li><a href="{a["url"]}" target="_blank" rel="noopener">{a["title"]}</a></li>\n'
        cat_sections += f"""
    <section>
      <h2>{cat}</h2>
      <ul>
{links}      </ul>
    </section>
"""

    html = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>讚讚讚小姐姐｜生活問題解決攻略總整理</title>
  <meta name="description" content="讚讚讚小姐姐的方格子文章總整理，房間潮濕、租屋家電、居家清潔、冷氣省電等生活問題解決攻略，幫你找到最實用的解法和推薦商品。">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{SITE_URL}">
  <meta property="og:title" content="讚讚讚小姐姐｜生活問題解決攻略總整理">
  <meta property="og:description" content="房間潮濕、租屋家電、居家清潔等生活問題解決攻略">
  <meta property="og:type" content="website">
  <meta property="og:url" content="{SITE_URL}">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height: 1.7; color: #333; max-width: 800px; margin: 0 auto; padding: 20px; background: #fafafa; }}
    h1 {{ font-size: 1.6em; margin-bottom: 8px; color: #1a1a1a; }}
    .subtitle {{ color: #666; margin-bottom: 30px; font-size: 0.95em; }}
    h2 {{ font-size: 1.2em; margin: 25px 0 10px; padding: 8px 12px; background: #fff; border-left: 4px solid #e8734a; border-radius: 4px; }}
    ul {{ list-style: none; padding: 0; }}
    li {{ margin: 6px 0; }}
    a {{ color: #e8734a; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    section {{ margin-bottom: 15px; }}
    .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #999; font-size: 0.85em; }}
  </style>
</head>
<body>
  <h1>讚讚讚小姐姐｜生活問題解決攻略</h1>
  <p class="subtitle">所有文章都在<a href="{VOCUS_URL}">方格子 vocus</a>，這裡是快速導覽。共 {len(articles)} 篇文章，持續更新中。</p>
{cat_sections}
  <div class="footer">
    <p>最後更新：{today}｜所有文章發布在<a href="{VOCUS_URL}">方格子 vocus</a></p>
  </div>
</body>
</html>"""

    output_path = os.path.join(OUTPUT_DIR, "index.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"index.html 已生成（{len(articles)} 篇文章）")


def generate_sitemap(articles):
    """生成 sitemap.xml"""
    today = datetime.now().strftime("%Y-%m-%d")

    urls = f"""  <url>
    <loc>{SITE_URL}</loc>
    <lastmod>{today}</lastmod>
    <priority>1.0</priority>
  </url>
"""
    for a in articles:
        urls += f"""  <url>
    <loc>{a['url']}</loc>
    <lastmod>{today}</lastmod>
    <priority>0.8</priority>
  </url>
"""

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls}</urlset>"""

    output_path = os.path.join(OUTPUT_DIR, "sitemap.xml")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(sitemap)
    print(f"sitemap.xml 已生成（{len(articles) + 1} 個 URL）")


def generate_robots():
    """生成 robots.txt"""
    robots = f"""User-agent: *
Allow: /

Sitemap: {SITE_URL}sitemap.xml
"""
    output_path = os.path.join(OUTPUT_DIR, "robots.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(robots)
    print("robots.txt 已生成")


if __name__ == "__main__":
    articles = load_articles()
    if not articles:
        print("articles.txt 裡沒有文章，先發文後再跑")
        # 還是生成空的框架
        generate_html([], {})
        generate_sitemap([])
        generate_robots()
    else:
        categories = categorize(articles)
        generate_html(articles, categories)
        generate_sitemap(articles)
        generate_robots()
    print("完成！")
