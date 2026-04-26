"""
fix_dates.py - Fix date mismatches in HeyBoss blog articles
Sync JSON-LD datePublished/dateModified with meta article:published_time
"""
import os
import re
import json

POSTS_DIR = os.path.join(os.path.dirname(__file__), 'posts')

stats = {'fixed': 0, 'scanned': 0}


def fix_file(filepath, fname):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    # Extract meta date
    meta_match = re.search(r'<meta\s+property="article:published_time"\s+content="([^"]+)"', html)
    if not meta_match:
        return False

    meta_date = meta_match.group(1)

    # Extract JSON-LD
    jsonld_match = re.search(r'<script\s+type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
    if not jsonld_match:
        return False

    jsonld_str = jsonld_match.group(1)
    try:
        jsonld = json.loads(jsonld_str)
    except json.JSONDecodeError:
        return False

    schema_date = jsonld.get('datePublished', '')
    schema_modified = jsonld.get('dateModified', '')

    if schema_date == meta_date and schema_modified == meta_date:
        return False

    # Fix: set both to meta date
    jsonld['datePublished'] = meta_date
    jsonld['dateModified'] = meta_date

    new_jsonld_str = json.dumps(jsonld, ensure_ascii=False, indent=2)
    html = html[:jsonld_match.start(1)] + new_jsonld_str + html[jsonld_match.end(1):]

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f'  [FIXED] {fname}: schema {schema_date} -> {meta_date}')
    stats['fixed'] += 1
    return True


def main():
    if not os.path.isdir(POSTS_DIR):
        print(f'Posts directory not found: {POSTS_DIR}')
        return

    print(f'Scanning {POSTS_DIR}...\n')

    files = sorted([f for f in os.listdir(POSTS_DIR) if f.endswith('.html')])

    for fname in files:
        filepath = os.path.join(POSTS_DIR, fname)
        stats['scanned'] += 1
        fix_file(filepath, fname)

    print(f'\n{"="*50}')
    print(f'Files scanned: {stats["scanned"]}')
    print(f'Dates fixed: {stats["fixed"]}')
    print(f'{"="*50}')


if __name__ == '__main__':
    main()
