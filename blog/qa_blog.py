#!/usr/bin/env python3
"""HEY!BOSS Blog UX QA Script — run after every change before reporting to Travis.
Supports both bilingual (heyboss) and Chinese-only (rtp96/slotlab) articles."""

import os, re, hashlib, sys

DEMOS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG = os.path.join(DEMOS, "blog")
POSTS = os.path.join(BLOG, "posts")
DRAFTS = os.path.join(BLOG, "drafts")
INDEX = os.path.join(BLOG, "index.html")

PASS = 0
FAIL = 0
WARN = 0

def check(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}" + (f" — {detail}" if detail else ""))

def warn(name, detail=""):
    global WARN
    WARN += 1
    print(f"  ⚠️ {name}" + (f" — {detail}" if detail else ""))

def read(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def is_bilingual(html):
    """Detect if an HTML file uses the bilingual system (data-zh attributes)."""
    return len(re.findall(r'data-zh=', html)) >= 10

print("=" * 60)
print("HEY!BOSS Blog UX QA")
print("=" * 60)

# ============================================================
# INDEX PAGE
# ============================================================
print("\n📄 列表頁 (index.html)")
idx = read(INDEX)
idx_is_bilingual = is_bilingual(idx)

# Nav
idx_nav = re.search(r'<nav.*?</nav>', idx, re.DOTALL)
if idx_nav:
    idx_nav = idx_nav.group(0)
    if idx_is_bilingual:
        check("Nav 有 langToggleBtn", 'langToggleBtn' in idx_nav)
        check("langToggleBtn 只有 1 個", idx_nav.count('langToggleBtn') == 1, f"count={idx_nav.count('langToggleBtn')}")
        check("按鈕在 nav-links 裡", bool(re.search(r'blog-nav-links.*?langToggleBtn.*?</div>', idx_nav, re.DOTALL)))
        check("無多餘空 div", 'display:flex;align-items:center;gap:8px' not in idx_nav)
        check("有 toggleLang 腳本", 'toggleLang' in idx)
        check("有 localStorage", 'localStorage' in idx)
    else:
        warn("Index 非雙語模式，跳過 langToggleBtn/localStorage 檢查")
else:
    warn("Index 無 nav 區塊")

# Cards
cards = re.findall(r'<a href="posts/([^"]+)"[^>]*class="post-card"[^>]*>(.*?)</a>', idx, re.DOTALL)
post_files = [f for f in os.listdir(POSTS) if f.endswith('.html')]
check(f"卡片數 = 文章數", len(cards) == len(post_files), f"cards={len(cards)} posts={len(post_files)}")

for fname, card_html in cards:
    # Thumbnail
    has_thumb = 'data:image' in card_html
    check(f"卡片 {fname[:20]}... 有縮圖", has_thumb)

    if idx_is_bilingual:
        # Span wrapping on h2
        h2_span = bool(re.search(r'<h2><span data-zh', card_html))
        h2_direct = bool(re.search(r'<h2 data-zh', card_html))
        check(f"卡片 {fname[:20]}... h2 用 span", h2_span and not h2_direct, "h2直接放data-zh" if h2_direct else "")

        # English translation
        en_vals = re.findall(r'data-en="([^"]*)"', card_html)
        chinese_in_en = [v for v in en_vals if re.search(r'[\u4e00-\u9fff]', v) and 'min read' not in v.lower()]
        check(f"卡片 {fname[:20]}... data-en 是英文", len(chinese_in_en) == 0, f"中文: {chinese_in_en[0][:30]}..." if chinese_in_en else "")

# ============================================================
# ARTICLE PAGES
# ============================================================
print(f"\n📝 文章內頁 ({len(post_files)} 篇)")

ref_nav = None
MIN_DATA_ZH = 40

for fname in sorted(post_files):
    fpath = os.path.join(POSTS, fname)
    html = read(fpath)
    short = fname[:25]
    article_bilingual = is_bilingual(html)

    # Nav consistency (only among bilingual articles)
    nav_match = re.search(r'<nav.*?</nav>', html, re.DOTALL)
    if nav_match:
        nav = nav_match.group(0)
        if article_bilingual:
            if ref_nav is None:
                ref_nav = nav
            nav_hash = hashlib.md5(nav.encode()).hexdigest()
            ref_hash = hashlib.md5(ref_nav.encode()).hexdigest()
            check(f"{short} nav 一致", nav_hash == ref_hash)

            # Single button
            btn_count = nav.count('langToggleBtn')
            check(f"{short} 按鈕=1", btn_count == 1, f"count={btn_count}")

    # Cover image (warning only — newer template uses external CSS hero)
    has_cover = bool(re.search(r'data:image/jpeg;base64', html))
    if not has_cover:
        warn(f"{short} 無 base64 封面圖（可能使用外部圖片或 CSS）")
    else:
        check(f"{short} 有封面圖", True)

    # No hamburger
    has_hamburger = 'blog-hamburger' in html or 'blogMobileMenu' in html or 'blog-mobile-menu' in html
    check(f"{short} 無漢堡菜單", not has_hamburger)

    # Bilingual-specific checks
    if article_bilingual:
        has_script = 'function toggleLang' in html or 'function applyLang' in html
        check(f"{short} 有切換腳本", has_script)

        has_ls = 'localStorage' in html
        check(f"{short} 有 localStorage", has_ls)

        dz_count = len(re.findall(r'data-zh=', html))
        check(f"{short} data-zh≥{MIN_DATA_ZH}", dz_count >= MIN_DATA_ZH, f"only {dz_count}")

        direct = len(re.findall(r'<(h[1-3]|p|li|blockquote) data-zh', html))
        check(f"{short} 無直接屬性", direct == 0, f"{direct} elements with direct data-zh")
    else:
        warn(f"{short} 非雙語文章，跳過 data-zh/localStorage 檢查")

    # Back button (check both link-based and component-based)
    has_back = '返回' in html or 'Back to Blog' in html or 'breadcrumb' in html
    check(f"{short} 有返回/麵包屑", has_back)

    # Meta tags (universal check)
    has_title = bool(re.search(r'<title>.+</title>', html))
    has_desc = bool(re.search(r'<meta name="description"', html))
    check(f"{short} 有 title+description", has_title and has_desc)

# ============================================================
# DRAFTS (spot check)
# ============================================================
if os.path.isdir(DRAFTS):
    draft_files = [f for f in os.listdir(DRAFTS) if f.endswith('.html')]
    print(f"\n📦 草稿 ({len(draft_files)} 篇，抽查)")

    for fname in draft_files[:5]:
        fpath = os.path.join(DRAFTS, fname)
        html = read(fpath)
        short = fname[:25]
        draft_bilingual = is_bilingual(html)

        if draft_bilingual:
            has_btn = 'langToggleBtn' in html
            has_ls = 'localStorage' in html
            dz = len(re.findall(r'data-zh=', html))
            check(f"草稿 {short} 按鈕+LS+雙語", has_btn and has_ls and dz >= MIN_DATA_ZH, f"btn={has_btn} ls={has_ls} dz={dz}")
        else:
            has_title = bool(re.search(r'<title>.+</title>', html))
            has_desc = bool(re.search(r'<meta name="description"', html))
            has_h1 = bool(re.search(r'<h1>.+</h1>', html))
            check(f"草稿 {short} 基本結構", has_title and has_desc and has_h1, f"title={has_title} desc={has_desc} h1={has_h1}")
else:
    print("\n📦 無草稿目錄，跳過")

# ============================================================
# SUMMARY
# ============================================================
print(f"\n{'=' * 60}")
total = PASS + FAIL
print(f"結果：{PASS}/{total} 通過，{FAIL} 失敗，{WARN} 警告")
if FAIL == 0:
    print("🎉 全部通過！可以回報 Travis。")
else:
    print("🚫 有失敗項目，修好再回報。")
    sys.exit(1)
