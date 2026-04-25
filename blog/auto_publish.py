#!/usr/bin/env python3
"""
HEY!BOSS Blog Auto-Publish Script
===================================
Scans blog/posts/ for all .html article files, extracts metadata,
and regenerates blog/index.html with article cards sorted by date (newest first).

Usage:
    python auto_publish.py

Metadata extracted from each article:
  - title (zh/en)     : from <h1><span data-zh="..." data-en="...">
  - category (zh/en)  : from <span class="category"><span data-zh="..." data-en="...">
  - date              : from <meta property="article:published_time" content="...">
  - reading time      : from <span data-zh="N 分鐘閱讀" data-en="N min read">
  - description (zh)  : from <meta name="description" content="...">
  - description (en)  : from <meta property="og:description" content="...">
"""

import os
import re
import glob
from datetime import datetime

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
POSTS_DIR = os.path.join(SCRIPT_DIR, "posts")
INDEX_PATH = os.path.join(SCRIPT_DIR, "index.html")

# ---------------------------------------------------------------------------
# Category translation map (zh -> en)
# ---------------------------------------------------------------------------
CATEGORY_EN_MAP = {
    "AI 建站": "AI Web Building",
    "系統開發": "System Development",
    "DevOps": "DevOps",
    "SEO": "SEO",
    "產業觀點": "Industry Insights",
}


def extract_meta(html, prop_name, attr="content"):
    """Extract content from a <meta> tag by property or name."""
    # Try property= first, then name=
    for key in ("property", "name"):
        pat = rf'<meta\s+{key}="{re.escape(prop_name)}"\s+{attr}="([^"]*)"'
        m = re.search(pat, html)
        if m:
            return m.group(1)
    return ""


def extract_data_span(html, pattern_before):
    """Extract data-zh and data-en from a <span> that appears after pattern_before."""
    pat = pattern_before + r'.*?data-zh="([^"]*)".*?data-en="([^"]*)"'
    m = re.search(pat, html, re.DOTALL)
    if m:
        return m.group(1), m.group(2)
    return "", ""


def extract_reading_time(html):
    """Extract reading time like '8 分鐘閱讀' / '8 min read' from article body."""
    m = re.search(r'data-zh="(\d+)\s*分鐘閱讀"\s*data-en="(\d+)\s*min read"', html)
    if m:
        minutes = m.group(1)
        return f"{minutes} 分鐘閱讀", f"{minutes} min read"
    # Fallback: estimate from text length
    text = re.sub(r'<[^>]+>', '', html)
    words = len(text)
    minutes = max(3, words // 500)
    return f"{minutes} 分鐘閱讀", f"{minutes} min read"


def parse_article(filepath):
    """Parse a single article HTML file and return metadata dict."""
    with open(filepath, "r", encoding="utf-8") as f:
        html = f.read()

    filename = os.path.basename(filepath)

    # Date
    date = extract_meta(html, "article:published_time")
    if not date:
        # Fallback: try to find datePublished in JSON-LD
        m = re.search(r'"datePublished"\s*:\s*"([^"]+)"', html)
        date = m.group(1) if m else "2026-01-01"

    # Category (zh/en) from article body: <span class="category"><span data-zh="..." data-en="...">
    cat_zh, cat_en = "", ""
    # First try: bilingual category with nested span (single line, no DOTALL)
    m = re.search(r'class="category"[^>]*>\s*<span\s+data-zh="([^"]*)"\s+data-en="([^"]*)"', html)
    if m:
        cat_zh, cat_en = m.group(1), m.group(2)
    else:
        # Try plain text category: <span class="category">Text</span>
        m = re.search(r'class="category"[^>]*>([^<]+)</span>', html)
        if m:
            cat_zh = m.group(1).strip()
            cat_en = CATEGORY_EN_MAP.get(cat_zh, cat_zh)
        else:
            # Fallback from meta tag
            cat_zh = extract_meta(html, "article:section")
            cat_en = CATEGORY_EN_MAP.get(cat_zh, cat_zh)

    # Title (zh/en) from <h1><span data-zh="..." data-en="...">
    title_zh, title_en = "", ""
    m = re.search(r'<h1[^>]*>.*?data-zh="([^"]*)".*?data-en="([^"]*)"', html, re.DOTALL)
    if m:
        title_zh, title_en = m.group(1), m.group(2)
    else:
        # Fallback from <title>
        m = re.search(r'<title>([^<]+)</title>', html)
        if m:
            title_zh = m.group(1).replace(" — HEY!BOSS Blog", "").strip()
            title_en = title_zh  # No EN available

    # Description
    desc_zh = extract_meta(html, "description")
    desc_en = extract_meta(html, "og:description")
    if not desc_en:
        desc_en = desc_zh  # Fallback

    # Reading time
    read_zh, read_en = extract_reading_time(html)

    return {
        "filename": filename,
        "date": date,
        "cat_zh": cat_zh,
        "cat_en": cat_en,
        "title_zh": title_zh,
        "title_en": title_en,
        "desc_zh": desc_zh,
        "desc_en": desc_en,
        "read_zh": read_zh,
        "read_en": read_en,
    }


def generate_card_html(article):
    """Generate the HTML for one post-card <a> element."""
    a = article
    # Escape HTML entities in text
    def esc(s):
        return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")

    card = f'''    <a href="posts/{a['filename']}" class="post-card">
      <div class="post-card-content">
        <div class="post-card-meta">
          <span class="post-card-category" data-zh="{esc(a['cat_zh'])}" data-en="{esc(a['cat_en'])}">{esc(a['cat_zh'])}</span>
          <span>{a['date']}</span>
          <span data-zh="{esc(a['read_zh'])}" data-en="{esc(a['read_en'])}">{esc(a['read_zh'])}</span>
        </div>
        <h2><span data-zh="{esc(a['title_zh'])}" data-en="{esc(a['title_en'])}">{esc(a['title_zh'])}</span></h2>
        <p data-zh="{esc(a['desc_zh'])}" data-en="{esc(a['desc_en'])}">{esc(a['desc_zh'])}</p>
      </div>
    </a>'''
    return card


def generate_index(articles):
    """Generate the full blog/index.html content."""
    cards = "\n\n".join(generate_card_html(a) for a in articles)

    html = f'''<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HEY!BOSS Blog — AI 建站・數位轉型・企業系統開發實戰分享</title>
<meta name="description" content="HEY!BOSS 銀月數位顧問官方 Blog，分享 AI 建站實戰、若依框架企業系統開發、自動化 SEO、CI/CD 自動部署等數位轉型技術與案例。">
<meta name="keywords" content="AI建站, 數位轉型, 若依框架, RuoYi, 企業系統開發, 自動化SEO, CI/CD, HEY!BOSS, 銀月數位顧問">
<link rel="canonical" href="https://www.heyboss.com.tw/blog/">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<meta property="og:title" content="HEY!BOSS Blog — AI 建站・數位轉型實戰分享">
<meta property="og:description" content="AI 建站實戰、企業系統開發、自動化 SEO 等數位轉型技術分享。">
<meta property="og:type" content="website">
<meta property="og:url" content="https://www.heyboss.com.tw/blog/">
<meta property="og:locale" content="zh_TW">
<meta property="og:site_name" content="HEY!BOSS 銀月數位顧問">
<link rel="icon" href="../heyboss/logos/logo_final.png" type="image/png">
<link rel="alternate" type="application/rss+xml" title="HEY!BOSS Blog RSS" href="rss.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&family=Noto+Sans+TC:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Blog",
  "name": "HEY!BOSS Blog",
  "description": "AI 建站、數位轉型、企業系統開發實戰分享",
  "url": "https://www.heyboss.com.tw/blog/",
  "inLanguage": "zh-TW",
  "publisher": {{
    "@type": "Organization",
    "name": "銀月數位顧問股份有限公司",
    "alternateName": "HEY!BOSS",
    "url": "https://www.heyboss.com.tw/",
    "logo": "https://www.heyboss.com.tw/heyboss/logos/logo_final.png"
  }}
}}
</script>
</head>
<body>

<nav class="blog-nav">
  <div class="blog-nav-inner">
    <a href="../" class="blog-nav-logo">
      <img src="../heyboss/logos/logo_final.png" alt="HEY!BOSS">
      <span>HEY!BOSS</span>
      <span class="blog-label">BLOG</span>
    </a>
    <div class="blog-nav-links">
      <a href="../#services"><span data-zh="服務" data-en="Services">服務</span></a>
      <a href="../#portfolio"><span data-zh="作品" data-en="Portfolio">作品</span></a>
      <a href="../#contact"><span data-zh="聯繫" data-en="Contact">聯繫</span></a>
      <button onclick="toggleLang()" style="background:var(--hey-blue,#2563eb);color:#fff;border:none;border-radius:6px;padding:6px 14px;cursor:pointer;font-size:14px;font-weight:600;margin-left:12px;white-space:nowrap;" id="langToggleBtn">EN/中</button>
    </div>
  </div>
</nav>

<section class="blog-hero">
  <div class="blog-container">
    <h1>HEY!BOSS Blog</h1>
    <p data-zh="AI 建站・數位轉型・企業系統開發的實戰經驗與技術分享" data-en="Real-world insights on AI web building, digital transformation &amp; enterprise systems">AI 建站・數位轉型・企業系統開發的實戰經驗與技術分享</p>
  </div>
</section>

<section class="post-grid">
  <div class="blog-container">

{cards}

</div>
</section>

<footer class="blog-footer">
  <a href="../">HEY!BOSS</a> <span data-zh="銀月數位顧問股份有限公司" data-en="Silver Moon Digital Consulting Co., Ltd.">銀月數位顧問股份有限公司</span> &copy; 2026
</footer>

<script>
let lang = localStorage.getItem('blogLang') || 'zh';
function applyLang() {{
  document.querySelectorAll('[data-zh]').forEach(function(el) {{
    el.textContent = el.getAttribute('data-' + lang);
  }});
  var btn = document.getElementById('langToggleBtn');
  if (btn) btn.textContent = lang === 'zh' ? 'EN/中' : '中/EN';
}}
function toggleLang() {{
  lang = lang === 'zh' ? 'en' : 'zh';
  localStorage.setItem('blogLang', lang);
  applyLang();
}}
if (lang !== 'zh') applyLang();
</script>
</body>
</html>'''
    return html


def main():
    print("=" * 60)
    print("HEY!BOSS Blog Auto-Publish")
    print("=" * 60)

    # Scan posts
    html_files = sorted(glob.glob(os.path.join(POSTS_DIR, "*.html")))
    if not html_files:
        print("No articles found in posts/")
        return

    print(f"\nScanning {len(html_files)} article(s) in posts/...")

    articles = []
    for filepath in html_files:
        try:
            article = parse_article(filepath)
            articles.append(article)
            print(f"  [{article['date']}] {article['title_zh'][:40]}")
        except Exception as e:
            print(f"  ERROR parsing {os.path.basename(filepath)}: {e}")

    # Sort by date descending (newest first)
    articles.sort(key=lambda a: a["date"], reverse=True)

    print(f"\nSorted {len(articles)} articles by date (newest first):")
    for i, a in enumerate(articles, 1):
        print(f"  {i}. [{a['date']}] [{a['cat_zh']}] {a['title_zh'][:50]}")

    # Generate index.html
    index_html = generate_index(articles)
    with open(INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(index_html)

    print(f"\nGenerated: {INDEX_PATH}")
    print(f"Total articles listed: {len(articles)}")

    # Summary by category
    cats = {}
    for a in articles:
        cats[a["cat_zh"]] = cats.get(a["cat_zh"], 0) + 1
    print("\nArticles by category:")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    print("\nDone!")


if __name__ == "__main__":
    main()
